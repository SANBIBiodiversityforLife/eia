from django.contrib.gis import forms
from leaflet.forms.widgets import LeafletWidget
from core import models


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
        profile = super(ProfileUpdateForm, self).save(*args,**kwargs)
        return profile


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
        fields = ('location', 'name', 'sensitive', 'activity', 'habitat') # todo do i need to insert 'taxon' again?
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
        model = models.Project
        fields = ('name', 'location', 'developer', 'eia_number', 'energy_type')
        widgets = {'location': LeafletWidget()}


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

