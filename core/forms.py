from django import forms
from leaflet.forms.widgets import LeafletWidget
from core.models import Project, DataSet


class ProjectCreateForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('current_name', 'location', 'current_developer', 'eia_number', 'energy_type')
        widgets = {'location': LeafletWidget()}


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


class DataCreateForm(forms.ModelForm):
    class Meta:
        model = DataSet
        fields = ()
        widgets = {'location': LeafletWidget()}

