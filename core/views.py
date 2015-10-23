from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from core import models, forms


class ProjectList(ListView):
    model = models.Project
    context_object_name = 'projects'


class ProjectDetail(DetailView):
    model = models.Project
    context_object_name = 'project'


class ProjectCreate(CreateView):
    template_name_suffix = '_create_form'
    form_class = forms.ProjectCreateForm


class ProjectUpdate(UpdateView):
    model = models.Project
    template_name_suffix = '_update_form'
    form_class = forms.ProjectUpdateForm


class ProjectDelete(DeleteView):
    model = models.Project
    template_name_suffix = '_delete_form'
    form_class = forms.ProjectDeleteForm


class DataList(ListView):
    model = models.Project
    context_object_name = 'projects'


class DataCreate(CreateView):
    template_name_suffix = '_create_form'
    form_class = forms.DataCreateForm