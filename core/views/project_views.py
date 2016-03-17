# Django rendering stuff
from django.shortcuts import render_to_response, render, redirect
from django.template import RequestContext
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView, TemplateView
from django.views.generic.edit import CreateView
from django.contrib.auth.decorators import login_required

# Core & settings
from core import models, forms

# Filters
import django_filters
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# JSON & serialization
from django.http import JsonResponse
from django.core.serializers import serialize
from core.serializers import ProjectJSONSerializer


class ProjectCreate(CreateView):
    model = models.Project
    template_name_suffix = '_create_form'
    form_class = forms.ProjectCreateForm

    def get_context_data(self, **kwargs):
        context = super(ProjectCreate, self).get_context_data(**kwargs)
        if 'developer_form' not in context:
            context['developer_form'] = forms.DeveloperCreateForm()
        return context


class ProjectUpdate(UpdateView):
    model = models.Project
    template_name_suffix = '_update_form'
    form_class = forms.ProjectUpdateForm

    '''def get_form_kwargs(self):
        kwargs = super(ProjectUpdate, self).get_form_kwargs()
        import pdb; pdb.set_trace()
        # kwargs['bounds'] = self.object.energy_type
        return kwargs'''

    def get_context_data(self, **kwargs):
        context = super(ProjectUpdate, self).get_context_data(**kwargs)

        # Developer form for companies who build renewable energy projects
        if 'developer_form' not in context:
            context['developer_form'] = forms.DeveloperCreateForm()

        # We also need to provide the geojson for the project area
        project = models.Project.objects.filter(pk=self.object.pk)
        geojson = serialize('geojson', project)
        context['project_geojson'] = geojson
        context['project'] = project[0]

        return context


class ProjectUpdateOperationalInfo(UpdateView):
    model = models.Project
    template_name_suffix = '_update_operational_info_form'
    form_class = forms.ProjectUpdateOperationalInfoForm

    def get_form_kwargs(self):
        kwargs = super(ProjectUpdateOperationalInfo, self).get_form_kwargs()
        kwargs['energy_type'] = self.object.energy_type
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(ProjectUpdateOperationalInfo, self).get_context_data(**kwargs)

        # Equipment form
        if 'equipment_form' not in context:
            context['equipment_form'] = forms.EquipmentMakeCreateForm()

        project = models.Project.objects.filter(pk=self.object.pk)
        geojson = serialize('geojson', project)
        context['project_geojson'] = geojson
        context['project'] = project[0]
        return context


class DeveloperCreate(CreateView):
    model = models.Developer
    fields = ['name', 'email', 'phone']
    template_name_suffix = '_create_form'

    def form_invalid(self, form):
        response = super(DeveloperCreate, self).form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        # We make sure to call the parent's form_valid() method because
        # it might do some processing (in the case of CreateView, it will
        # call form.save() for example).
        response = super(DeveloperCreate, self).form_valid(form)
        if self.request.is_ajax():
            data = {
                'pk': self.object.pk,
                'name': self.object.name,
            }
            return JsonResponse(data)
        else:
            return response


class DeveloperDetail(DetailView):
    model = models.Developer
    context_object_name = 'developer'


class EquipmentMakeCreate(CreateView):
    model = models.EquipmentMake
    fields = ['name',]
    template_name = 'equipment_make_create_form'

    def form_invalid(self, form):
        # TODO add validation to ensure that turbine points are within the project polygon

        response = super(EquipmentMakeCreate, self).form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        # We make sure to call the parent's form_valid() method because
        # it might do some processing (in the case of CreateView, it will
        # call form.save() for example).
        response = super(EquipmentMakeCreate, self).form_valid(form)
        if self.request.is_ajax():
            data = {
                'pk': self.object.pk,
                'name': self.object.name,
            }
            return JsonResponse(data)
        else:
            return response


@login_required
def project_detail(request, pk):
    # Retrieve the project
    project = models.Project.objects.get(pk=pk)

    # Set up the context
    context = {'project': project}

    # Get the project location geojson
    context['project_location'] = serialize('geojson', [project], geometry_field='location', fields=('location',))

    # Get the equipment locations
    if project.turbine_locations:
        context['turbine_geojson'] = serialize('geojson',
                                               [project],
                                               geometry_field='turbine_locations',
                                               fields=('turbine_locations',))

    # Generate the documentation form for this dataset and get all the documents
    context['documents'] = models.Document.objects.filter(project=project, metadata=None)
    context['create_document_form'] = forms.DocumentCreateForm()

    # Render the context
    return render_to_response('core/project_detail.html',
                              context,
                              RequestContext(request))


class ProjectFilter(django_filters.FilterSet):
    class Meta:
        model = models.Project
        fields = ['name', 'developer']


def project_list(request):
    f = ProjectFilter(request.GET, queryset=models.Project.objects.all())

    paginator = Paginator(f.qs, 100)  # Show 100 events per page
    page = request.GET.get('page')
    try:
        projects = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        projects = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        projects = paginator.page(paginator.num_pages)

    return render(request, 'core/project_list.html', {'projects': projects, 'filter': f})


def projects_map(request):
    q = models.Project.objects.all().select_related('developer')
    f = ProjectFilter(request.GET, queryset=q)
    #geojsons = serialize('geojson', f)
    geojsons = serialize('geojson', f, geometry_field='location',
                         fields=('id', 'pk', 'developer', 'name', 'location'),
                         use_natural_foreign_keys=True)
    geojsons = ProjectJSONSerializer().serialize(f, geometry_field='location', use_natural_foreign_keys=True, use_natural_primary_keys=True)
    return render(request, 'core/projects_map.html', {'geojson': geojsons, 'filter': f})


class FocalSiteCreate(CreateView):
    model = models.FocalSite
    template_name = 'core/focal_site_create_form.html'
    form_class = forms.FocalSiteCreateForm

    # No idea why this needs to go in, but it seems to http://stackoverflow.com/questions/18605008/curious-about-get-form-kwargs-in-formview
    def get_form_kwargs(self):
        kwargs = super(FocalSiteCreate, self).get_form_kwargs()
        kwargs['project_pk'] = self.kwargs['project_pk']
        kwargs['uploader'] = self.request.user
        return kwargs

    # Pass the project as a whole to the template (so we can access name etc as well as pk
    def get_context_data(self, **kwargs):
        context = super(FocalSiteCreate, self).get_context_data(**kwargs)

        # Retrieve the project
        project = models.Project.objects.filter(pk=self.kwargs['project_pk'])

        # Get the project location geojson
        context['project_location_geojson'] = serialize('geojson',
                                                         project,
                                                         geometry_field='location',
                                                         fields=('location',))

        # Get the turbine location geojson
        context['turbine_locations_geojson'] = serialize('geojson',
                                                         project,
                                                         geometry_field='turbine_locations',
                                                         fields=('turbine_locations',))

        # Project is a queryset (from filter), as this is what geojson requires, now return the actual object
        context['project'] = project[0]

        # Return the context
        return context