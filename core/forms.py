from django.utils.safestring import mark_safe
from django import forms
from django.db import models
#from django.core.exceptions import DoesNotExist
from leaflet.forms.widgets import LeafletWidget
from core.models import Project, PopulationData, Taxa, TaxaOrder, FocalSite, FocalSiteData, MetaData, Profile, \
    Developer, EquipmentMake, User
from core import validators
from openpyxl import load_workbook
#from django.contrib.staticfiles.templatetags.staticfiles import static
from openpyxl.styles import Color, Fill, Style, fills, PatternFill, Font
from django.core.exceptions import ValidationError
from django.contrib.staticfiles.templatetags.staticfiles import static
import tempfile
import os
from django.conf import settings
from core.spreadsheet_creation import population_data_spreadsheet_validation
from django.contrib.auth import get_user_model


'''class SignupForm(forms.Form):
    first_name = forms.CharField(max_length=30, label='Voornaam')
    last_name = forms.CharField(max_length=30, label='Achternaam')'''


class SignupForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('first_name', 'last_name', 'phone', 'type')

    # A custom method required to work with django-allauth, see https://stackoverflow.com/questions/12303478/how-to-customize-user-profile-when-using-django-allauth
    def signup(self, request, user):
        # Save your user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()

        # Save your profile
        profile = Profile()
        profile.user = user
        profile.phone = self.cleaned_data['phone']
        profile.type = self.cleaned_data['type']
        profile.save()


class ProjectCreateForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('name', 'location', 'developer', 'eia_number', 'energy_type')
        widgets = {'location': LeafletWidget()}


class DeveloperCreateForm(forms.ModelForm):
    class Meta:
        model = Developer
        fields = ('name', 'email', 'phone')


class EquipmentMakeCreateForm(forms.ModelForm):
    class Meta:
        model = EquipmentMake
        fields = ('name',)


class FocalSiteCreateForm(forms.ModelForm):
    class Meta:
        model = FocalSite
        fields = ('name', 'location', 'project')
        widgets = {'location': LeafletWidget()}


class FocalSiteDataCreateForm(forms.ModelForm):
    class Meta:
        model = FocalSiteData
        fields = ('taxa', 'focal_site', 'count')


class ProjectUpdateOperationalInfoForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('operational_date', 'construction_date', 'turbine_locations', 'equipment_make', 'equipment_capacity',
                  'equipment_height')
        widgets = {'turbine_locations': LeafletWidget()}
        help_texts = {
            'operational_date': 'The date the project first became operational',
            'construction_date': 'The date construction began on the project',
            'turbine_locations': 'The locations of the turbines',
            'equipment_make': 'The make of the turbines/solar panels',
            'equipment_capacity': 'The capacity of the turbines/solar panels',
            'equipment_height': 'The height of the turbines/solar panels',
        }


class ProjectUpdateForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('name', 'location', 'developer', 'eia_number', 'energy_type')
        widgets = {'location': LeafletWidget()}


class ProjectDeleteForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('name', 'location', 'developer', 'eia_number', 'energy_type')
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
    main_sheet.cell(column=7, row=row_number).style = Style(font=Font(color='FFFFFFFF'),
                                                            fill=PatternFill(patternType='solid', fgColor=Color('FFFF0000')))

class MetaDataCreateForm(forms.ModelForm):
    upload_data = forms.FileField(
        label=mark_safe('Upload spreadsheet'),
        validators=[validators.validate_spreadsheet]
    )

    def __init__(self, *args, **kwargs):
        self.project_pk = kwargs.pop('project_pk')
        self.uploader = kwargs.pop('uploader')
        super(MetaDataCreateForm, self).__init__(*args, **kwargs)
        self.fields['collected_from'].label = "Data was collected between"
        self.fields['collected_to'].label = "and"

    class Meta:
        model = MetaData
        fields = ('upload_data', 'collected_from', 'collected_to', 'control_data')
        widgets = {
            'collected_from': forms.TextInput(attrs={'class': 'datepicker'}),
            'collected_to': forms.TextInput(attrs={'class': 'datepicker'})
        }

    def process_data(self):
        print('processing data...')
        # Load the workbook from the file held in memory
        uploaded_data = load_workbook(self.files['upload_data'])
        print('loaded workbook...')
        # Delete the upload_data fields & file now they are in the openpyxl object
        del self.fields['upload_data']
        del self.files['upload_data']

        # Get the correct sheet - TODO how are we going to stop them from renaming the sheet?
        main_sheet = uploaded_data.get_sheet_by_name("Main")
        print('Retrieved worksheet...')

        # Create the metadata object and store it to get its primary key
        # This must get deleted after this function if no actual data is stored
        print("adding project to instance...")
        self.instance.project = Project.objects.get(pk=self.project_pk)
        self.instance.uploader = self.uploader

        # self.instance.request

        print("saving project")
        self.instance.save()
        print("project saved")
        metadata = self.instance

        # Keep track of the errors somehow
        row_with_error_count = 0

        # Keep track of all the population data objects - if we have no errors at the end we shall save them
        population_data_list = []

        # Loop through the rows in the sheet
        for row in main_sheet.iter_rows(row_offset=1):
            print('Looping through main sheet')

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
                row_with_error_count += 1
                continue

            # Try and retrieve the taxa based on genus + species
            try:
                taxa = Taxa.objects.get(genus=genus, species=species)
            except Taxa.DoesNotExist:
                write_error(main_sheet=main_sheet,
                            row_number=row[0].row,
                            error_message='Error with genus/species - does not exist. Please check and correct.')
                row_with_error_count += 1
                continue

            # Try and create a population data object
            try:
                # Create a new object so we can run the validation on it
                population_data = PopulationData(metadata=metadata,
                                                 taxa=taxa,
                                                 count=count,
                                                 collision_risk=collision_risk,
                                                 density_km=density_km,
                                                 passage_rate=passage_rate)

                # Call the validation on the object
                population_data.full_clean()

                # If it hasn't slipped into the except, add it to the main list
                population_data_list.append(population_data)
            except ValidationError as err:
                write_error(main_sheet=main_sheet,
                            row_number=row[0].row,
                            error_message='Error when saving {}'.format(err))
                row_with_error_count += 1
                continue

        if row_with_error_count > 0:
            print('Errors with data - extra processing')
            # Delete the metadata
            metadata.delete()

            # Add the validation
            population_data_spreadsheet_validation(uploaded_data, main_sheet,
                                                   uploaded_data.get_sheet_by_name("Valid Species"),
                                                   uploaded_data.get_sheet_by_name("Valid Genera"))

            # Unique filename and timestamp
            # fd, unique_file = tempfile.mkstemp(suffix='.xlsx', prefix='pop_', dir=os.path.join(settings.BASE_DIR, 'tmp'))
            tmp_dir = os.path.join(settings.BASE_DIR, 'core', 'static', 'core', 'tmp')
            print(tmp_dir)
            fd, unique_file = tempfile.mkstemp(suffix='.xlsx', prefix='pop_', dir=tmp_dir)
            # TODO the above is terrible and must be fixed, serve the files through a proper webserver
            uploaded_data.save(unique_file)
            os.close(fd)
            print('Created error file, returning URL')

            # Send back the file url
            return os.path.join('static', 'core', 'tmp', os.path.basename(os.path.relpath(unique_file)))
        else:
            print('No errors - saving data')
            # Save all the population data
            for population_data in population_data_list:
                population_data.save()

            # No errors, return
            return False

        #import pdb; pdb.set_trace()

        # Parse the file using
'''
    def __init__(self, *args, **kwargs):
        self.hello = kwargs.pop('initial', None)
        super(PopulationDataCreateForm, self).__init__(*args, **kwargs)'''


