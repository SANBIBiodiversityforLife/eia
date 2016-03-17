from django.contrib.gis import forms
from leaflet.forms.widgets import LeafletWidget
from core import models
from datetime import datetime
import calendar

# This needs to get changed for Django 1.9 to from django.forms import SelectDateWidget
from django.forms.extras import SelectDateWidget

from django.utils.datastructures import MultiValueDict

class SignupForm(forms.ModelForm):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)

    class Meta:
        model = models.Profile
        fields = ('first_name', 'last_name', 'phone', 'type')

    # A custom method required to work with django-allauth, see https://stackoverflow.com/questions/12303478/how-to-customize-user-profile-when-using-django-allauth
    def signup(self, request, user):
        # Save your user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()

        # Save your profile
        profile = models.Profile()
        profile.user = user
        profile.phone = self.cleaned_data['phone']
        profile.type = self.cleaned_data['type']
        profile.save()


class ProfileUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)

    class Meta:
        model = models.Profile
        fields = ('first_name', 'last_name', 'email', 'phone', 'type')

    def __init__(self, *args, **kwargs):
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)
        try:
            self.fields['email'].initial = self.instance.user.email
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
        except models.User.DoesNotExist:
            pass

    def save(self, *args, **kwargs):
        """
        Update the primary email address on the related User object as well.
        """
        u = self.instance.user
        u.email = self.cleaned_data['email']
        u.save()
        profile = super(ProfileUpdateForm, self).save(*args, **kwargs)
        return profile


class ArrayFieldSelectMultiple(forms.SelectMultiple):
    """This is a Form Widget for use with a Postgres ArrayField. It implements
    a multi-select interface that can be given a set of `choices`.
    You can provide a `delimiter` keyword argument to specify the delimeter used.
    """
    def __init__(self, *args, **kwargs):
        # Accept a `delimiter` argument, and grab it (defaulting to a comma)
        self.delimiter = kwargs.pop("delimiter", ",")
        super(ArrayFieldSelectMultiple, self).__init__(*args, **kwargs)

    def render_options(self, choices, value):
        # value *should* be a list, but it might be a delimited string.
        if isinstance(value, str):  # python 2 users may need to use basestring instead of str
            value = value.split(self.delimiter)
        return super(ArrayFieldSelectMultiple, self).render_options(choices, value)

    def value_from_datadict(self, data, files, name):
        if isinstance(data, MultiValueDict):
            # Normally, we'd want a list here, which is what we get from the
            # SelectMultiple superclass, but the SimpleArrayField expects to
            # get a delimited string, so we're doing a little extra work.
            return self.delimiter.join(data.getlist(name))
        return data.get(name, None)


class PopulationMetaDataCreateForm(forms.ModelForm):
    # The location map needs to get prepopulated with the project area, so it can't be included in fields (below)
    #location = forms.PolygonField(widget=LeafletWidget(), label='')

    class Meta:
        model = models.PopulationMetaData
        fields = ('survey_types', 'hours', 'location')
        widgets = {'survey_types': ArrayFieldSelectMultiple(choices=models.PopulationMetaData.SURVEY_TYPE_CHOICES),
                   'location': LeafletWidget()}

    def __init__(self, *args, **kwargs):
        if 'project_polygon' in kwargs:
            project_polygon = kwargs.pop('project_polygon')
            super(PopulationMetaDataCreateForm, self).__init__(*args, **kwargs)
            self.fields['location'].initial = project_polygon
        else:
            super(PopulationMetaDataCreateForm, self).__init__(*args, **kwargs)

    '''def clean(self):

        import pdb; pdb.set_trace()'''


class ProjectCreateForm(forms.ModelForm):
    class Meta:
        model = models.Project
        fields = ('name', 'location', 'developer', 'eia_number', 'energy_type')
        widgets = {'location': LeafletWidget()}


class DeveloperCreateForm(forms.ModelForm):
    class Meta:
        model = models.Developer
        fields = ('name', 'email', 'phone')


class EquipmentMakeCreateForm(forms.ModelForm):
    class Meta:
        model = models.EquipmentMake
        fields = ('name',)


class DocumentCreateForm(forms.ModelForm):
    class Meta:
        model = models.Document
        fields = ('name', 'document', 'document_type')


class FocalSiteCreateForm(forms.ModelForm):
    class Meta:
        model = models.FocalSite
        fields = ('location', 'name', 'sensitive', 'activity', 'habitat')  # todo do i need to insert 'taxon' again?
        widgets = {'location': LeafletWidget()}

    def __init__(self, *args, **kwargs):
        self.project_pk = kwargs.pop('project_pk')
        self.uploader = kwargs.pop('uploader')
        super(FocalSiteCreateForm, self).__init__(*args, **kwargs)

    def clean(self):
        # Create the metadata object and store it to get its primary key
        # This must get deleted after this function if no actual data is stored
        print("adding project to instance...")
        cleaned_data = super(FocalSiteCreateForm, self).clean()
        self.instance.project = models.Project.objects.get(pk=self.project_pk)


class ProjectUpdateOperationalInfoForm(forms.ModelForm):
    class Meta:
        model = models.Project
        fields = ('operational_date',
                  'construction_date',
                  'equipment_make',
                  'capacity',
                  'equipment_height',
                  'turbine_locations',
                  )
        widgets = {'turbine_locations': LeafletWidget()}

    def __init__(self, *args, **kwargs):
        energy_type = kwargs.pop('energy_type')
        super(ProjectUpdateOperationalInfoForm, self).__init__(*args, **kwargs)

        if energy_type == models.Project.SOLAR:
            del self.fields['turbine_locations']


class ProjectUpdateForm(forms.ModelForm):
    class Meta:
        model = models.Project
        fields = ('name', 'location', 'developer', 'eia_number', 'energy_type')
        widgets = {'location': LeafletWidget()}

    '''def __init__(self, *args, **kwargs):
        super(ProjectUpdateForm, self).__init__(*args, **kwargs)

        self.fields['location'].widget = LeafletWidget(attrs={
            'settings_overrides': {
                'DEFAULT_CENTER': (-33.0, 29.0),
                'DEFAULT_ZOOM': 11,
            }
        })

        import pdb; pdb.set_trace()

        attrs={
            'settings_overrides': {
                'DEFAULT_CENTER': (6.0, 45.0),
            }
        }'''


class ProjectDeleteForm(forms.ModelForm):
    class Meta:
        model = models.Project
        fields = ('name', 'location', 'developer', 'eia_number', 'energy_type')
        widgets = {'location': LeafletWidget()}


class DataViewForm(forms.Form):
    datasets = forms.ChoiceField(label='Choose a dataset to view', choices=())

    def __init__(self, *args, **kwargs):
        metadata = kwargs.pop('metadata')
        super(DataViewForm, self).__init__(*args, **kwargs)
        self.fields['datasets'].choices = [(d.id, d) for d in metadata]


class RemovalFlagCreateForm(forms.ModelForm):
    class Meta:
        model = models.RemovalFlag
        fields = ('reason',)


class FatalityRateCreateForm(forms.ModelForm):
    class Meta:
        model = models.FatalityRate
        fields = ('taxon', 'start_date', 'end_date', 'rate')
        # The widgets dictionary accepts either widget instances or classes
        # http://stackoverflow.com/questions/9878475/beginner-django-modelform-override-widget
        widgets = {'start_date': SelectDateWidget(years=range(1900, datetime.now().year + 1)),
                   'end_date': SelectDateWidget(years=range(1900, datetime.now().year + 1))}

    def __init__(self, *args, **kwargs):
        self.project_pk = kwargs.pop('project_pk')
        self.uploader = kwargs.pop('uploader')
        self.rate_type = kwargs.pop('rate_type')

        # Call the super method
        super(FatalityRateCreateForm, self).__init__(*args, **kwargs)

        # self.project_pk = project_pk
        # self.uploader = uploader

        # We only want to include the orders really
        self.fields['taxon'].queryset = models.Taxon.objects.filter(rank=models.Taxon.ORDER)

        # Set initial dates. Note we hide the days, so for start it must always be 1 and for end it must be last day
        now = datetime.now()
        self.fields['start_date'].initial = now.replace(day=1)
        last_day_of_month = calendar.monthrange(now.year, now.month)[1]
        self.fields['end_date'].initial = now.replace(day=last_day_of_month)

    # Called to validate the form
    def clean(self):
        metadata = models.MetaData(project_id=self.project_pk, uploader=self.uploader)
        metadata.save()
        self.instance.metadata = metadata
        self.instance.rate_type = self.rate_type

        # Run the super clean method once the metadata is set
        cleaned_data = super(FatalityRateCreateForm, self).clean()

        # Note that start date < end date validation is occurring in model's clean
        # Can't put the below in there because of manytomany field apparently
        # We should not be able to upload e.g. 2 scavenger removal rates for the same (or overlapping) time period
        # See https://www.reddit.com/r/django/comments/2ckxdy/dealing_with_start_and_end_date_fields/
        taxon = self.cleaned_data.get('taxon')
        start_date = self.cleaned_data.get('start_date')
        end_date = self.cleaned_data.get('end_date')

        same_timespan = models.FatalityRate.objects.filter(metadata__project__pk=self.instance.metadata.project.pk,
                                                           rate_type=self.instance.rate_type,
                                                           taxon=taxon,
                                                           end_date__gte=start_date,
                                                           start_date__lte=end_date)
        if same_timespan:
            self.add_error('',
                           forms.ValidationError('There is already a ' + self.instance.get_rate_type_display() +
                                                 ' for this project, time period and taxa'))
            # raise forms.ValidationError('There is already a ' + self.instance.get_rate_type_display() +
            #                            ' for this project, time period and taxa')



        # Always return the cleaned data
        return cleaned_data
