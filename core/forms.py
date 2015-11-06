from django.utils.safestring import mark_safe
from django import forms
from django.db import models
#from django.core.exceptions import DoesNotExist
from leaflet.forms.widgets import LeafletWidget
from core.models import Project, PopulationData, Taxa, TaxaOrder, FocalSite, FocalSiteData, MetaData
from core import validators
from openpyxl import load_workbook
#from django.contrib.staticfiles.templatetags.staticfiles import static
from openpyxl.styles import Color, Fill, Style, fills, PatternFill
from django.core.exceptions import ValidationError

class ProjectCreateForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('current_name', 'location', 'current_developer', 'eia_number', 'energy_type')
        widgets = {'location': LeafletWidget()}


class FocalSiteCreateForm(forms.ModelForm):
    class Meta:
        model = FocalSite
        fields = ('name', 'location', 'project')
        widgets = {'location': LeafletWidget()}


class FocalSiteDataCreateForm(forms.ModelForm):
    class Meta:
        model = FocalSiteData
        fields = ('taxa', 'focal_site', 'count')


class ProjectUpdateForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('current_name', 'location', 'current_developer', 'eia_number', 'energy_type')
        widgets = {'location': LeafletWidget()}


class ProjectDeleteForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('current_name', 'location', 'current_developer', 'eia_number', 'energy_type')
        widgets = {'location': LeafletWidget()}


class DataUploadForm(forms.Form):
    spreadsheet = forms.FileField()

# Think we are not going to use this one as we don't actually want form fields here
class PopulationDataCreateForm(forms.ModelForm):
    order = models.ForeignKey(TaxaOrder)
    test = models.CharField(max_length=200)

    class Meta:
        model = PopulationData
        fields = ('taxa', 'count', 'collision_risk', 'metadata', 'density_km', 'passage_rate')


def write_error(main_sheet, row_number, error_message):
    main_sheet.cell(column=7, row=row_number, value=error_message)
    main_sheet.cell(column=7, row=row_number).style = Style(fill=PatternFill(patternType='solid', fgColor=Color('FFFF0000')))

class MetaDataCreateForm(forms.ModelForm):
    upload_data = forms.FileField(
        label=mark_safe('Ready? Upload the filled-in spreadsheet'),
        validators=[validators.validate_spreadsheet]
    )

    def __init__(self, *args, **kwargs):
        self.project_pk = kwargs.pop('pk', None)
        super(MetaDataCreateForm, self).__init__(*args, **kwargs)
        self.fields['collected_to'].label = "to "

    class Meta:
        model = MetaData
        fields = ('collected_from', 'collected_to', 'control_data')
        widgets = {
            'collected_from': forms.TextInput(attrs={'class': 'datepicker'}),
            'collected_to': forms.TextInput(attrs={'class': 'datepicker'})
        }

    def process_data(self, project_pk):
        # Load the workbook from the file held in memory
        uploaded_data = load_workbook(self.files['upload_data'])

        # Delete the upload_data fields & file now they are in the openpyxl object
        del self.fields['upload_data']
        del self.files['upload_data']

        # Get the correct sheet - TODO how are we going to stop them from renaming the sheet?
        main_sheet = uploaded_data.get_sheet_by_name("Main")

        # Keep track of the errors somehow
        row_with_error_count = 0

        # Loop through the rows in the sheet
        for row in main_sheet.iter_rows(row_offset=1):
            # Gather the data into sensible variable names
            genus = row[0].value
            species = row[1].value
            count = row[2].value
            collision_risk = row[3].value
            density_km = row[4].value
            passage_rate = row[5].value

            # If all of these are blank, (i.e., none have a value), then ignore this row
            if not(genus or species or count or collision_risk or density_km or passage_rate):
                continue

            # If any of these are blank (i.e. any don't have a value), throw up an error and get them to fill it in
            if not(genus and species and count and collision_risk and density_km and passage_rate):
                write_error(main_sheet=main_sheet,
                            row_number=row[0].row,
                            error_message='Incomplete row. All the fields must be filled out.')
                row_with_error_count += row_with_error_count
                continue

            # Try and retrieve the taxa based on genus + species
            try:
                taxa = Taxa.objects.get(genus=genus, species=species)
            except Taxa.DoesNotExist:
                write_error(main_sheet=main_sheet,
                            row_number=row[0].row,
                            error_message='Error with genus/species - does not exist. Please check and correct.')
                row_with_error_count += row_with_error_count
                continue


            # Create the metadata object and store it to get its primary key
            # This must get deleted after this function if no actual data is stored
            self.instance.project = Project.objects.get(pk=project_pk)
            metadata = self.instance.save()

            # Try and create a population data object
            try:
                population_data = PopulationData(metadata=metadata,
                                                 taxa=taxa,
                                                 count=count,
                                                 collision_risk=collision_risk,
                                                 density_km=density_km,
                                                 passage_rate=passage_rate)
                population_data.save()
            except ValidationError:
                write_error(main_sheet=main_sheet,
                            row_number=row[0].row,
                            error_message='Error with genus/species - does not exist. Please check and correct.')
                row_with_error_count += row_with_error_count
                continue

        if row_with_error_count:
            uploaded_data.save('C:/test.xlsx')
        else:

            # If the validation complains then we have a problem

        #import pdb; pdb.set_trace()

        # Parse the file using
'''
    def __init__(self, *args, **kwargs):
        self.hello = kwargs.pop('initial', None)
        super(PopulationDataCreateForm, self).__init__(*args, **kwargs)'''


