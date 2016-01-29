from django.shortcuts import render_to_response, render, redirect
from django.template import RequestContext
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView, TemplateView
from core import models, forms
from django.http import HttpResponseRedirect, HttpResponse

from django.http import JsonResponse
from django.views.generic.edit import CreateView
from io import BytesIO

from django.core.urlresolvers import reverse, reverse_lazy
import tempfile
import os
from django.conf import settings
from core.spreadsheet_creation import create_population_data_spreadsheet, create_focal_site_data_spreadsheet, create_fatality_data_spreadsheet
from django.core.serializers import serialize
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from core.serializers import CustomGeoJSONSerializer, FocalSiteJSONSerializer

def index(request):
    return render(request, 'core/index.html', {'stats': 'hello'})


class AjaxableResponseMixinDataCreate(object):
    """
    Mixin to add AJAX support to a form.
    Must be used with an object-based FormView (e.g. CreateView)
    """

    def get_success_url(self):
        return reverse('project_detail', args={'pk': self.kwargs['project_pk']})

    # No idea why this needs to go in, but it seems to http://stackoverflow.com/questions/18605008/curious-about-get-form-kwargs-in-formview
    def get_form_kwargs(self):
        kwargs = super(AjaxableResponseMixinDataCreate, self).get_form_kwargs()
        kwargs['project_pk'] = self.kwargs['project_pk']
        kwargs['uploader'] = self.request.user

        if 'focal_site_pk' in self.kwargs:
            kwargs['focal_site_pk'] = self.kwargs['focal_site_pk']
        return kwargs

    # Pass the project as a whole to the template (so we can access name etc as well as pk
    def get_context_data(self, **kwargs):
        context = super(AjaxableResponseMixinDataCreate, self).get_context_data(**kwargs)
        context['project'] = models.Project.objects.get(pk=self.kwargs['project_pk'])
        return context


    def form_invalid(self, form):
        response = super(AjaxableResponseMixinDataCreate, self).form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        # A custom function which should be present in all data adding forms - note self.kwargs['project_pk']
        xlsx_with_errors = form.process_data()

        if self.request.is_ajax():
            print('returning data')
            data = {
                #'pk': self.object.pk,
                'error_sheet': xlsx_with_errors
            }
            return JsonResponse(data)
        else:
            return HttpResponseRedirect(self.get_success_url())


class ProfileUpdate(UpdateView):
    model = models.Profile #get_user_model()
    #fields = ['first_name', 'last_name', 'email', 'phone', 'type']
    template_name = 'account/profile_update.html'
    form_class = forms.ProfileUpdateForm

    # Get user from the request
    def get_object(self, queryset=None):
        #return get_object_or_404(User, name=self.request.user.pk)
        return self.request.user.profile

    # For some reason the get_absolute_url on the model doesn't work, so we need this
    #success_url = reverse_lazy('profile_detail')


class PopulationDataCreateView(AjaxableResponseMixinDataCreate, FormView):
    template_name = 'core/populationdata_create_form.html'
    form_class = forms.PopulationDataCreateForm


class FocalSiteDataCreateView(AjaxableResponseMixinDataCreate, FormView):
    template_name = 'core/focalsitedata_create_form.html'
    form_class = forms.FocalSiteDataCreateForm


class FatalityDataCreateView(AjaxableResponseMixinDataCreate, FormView):
    template_name = 'core/fatalitydata_create_form.html'
    form_class = forms.FatalityDataCreateForm


class FocalSiteCreate(CreateView):
    model = models.FocalSite
    template_name_suffix = '_create_form'
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


class ProjectCreate(CreateView):
    model = models.Project
    template_name_suffix = '_create_form'
    form_class = forms.ProjectCreateForm

    # TODO we need to allow people to upload shape files see https://docs.djangoproject.com/en/1.9/ref/contrib/gis/tutorial/

    def get_context_data(self, **kwargs):
        context = super(ProjectCreate, self).get_context_data(**kwargs)
        if 'developer_form' not in context:
            context['developer_form'] = forms.DeveloperCreateForm()
        return context


class ProjectUpdate(UpdateView):
    model = models.Project
    template_name_suffix = '_update_form'
    form_class = forms.ProjectUpdateForm

    # TODO we need to allow people to upload shape files see https://docs.djangoproject.com/en/1.9/ref/contrib/gis/tutorial/

    def get_context_data(self, **kwargs):
        context = super(ProjectUpdate, self).get_context_data(**kwargs)

        # Developer form
        if 'developer_form' not in context:
            context['developer_form'] = forms.DeveloperCreateForm()

        project = models.Project.objects.filter(pk=self.object.pk)
        geojson = serialize('geojson', project)
        context['project_geojson'] = geojson
        context['project'] = project[0]
        return context


class ProjectUpdateOperationalInfo(UpdateView):
    model = models.Project
    template_name_suffix = '_update_operational_info_form'
    form_class = forms.ProjectUpdateOperationalInfoForm

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

class ProjectDelete(DeleteView):
    model = models.Project
    template_name_suffix = '_delete_form'
    form_class = forms.ProjectDeleteForm


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


class EquipmentMakeCreate(CreateView):
    model = models.EquipmentMake
    fields = ['name',]
    template_name_suffix = '_create_form'

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


class DeveloperDetail(DetailView):
    model = models.Developer
    context_object_name = 'developer'


class DataList(ListView):
    model = models.Project
    context_object_name = 'projects'


@login_required
def project_detail(request, pk):
    # Retrieve the project
    project = models.Project.objects.filter(pk=pk)

    # Get the project location geojson
    project_location_geojson = serialize('geojson', project, geometry_field='location', fields=('location',))

    # Get the turbine location geojson
    turbine_locations_geojson = serialize('geojson',
                                          project,
                                          geometry_field='turbine_locations',
                                          fields=('turbine_locations',))

    # Project is a queryset (from filter), as this is what geojson requires, now return the actual object
    project = project[0]

    # Render the context
    return render_to_response('core/project_detail.html',
                              {'project_location': project_location_geojson,
                               'turbine_locations': turbine_locations_geojson,
                               'project': project},
                              RequestContext(request))


def dataset_display_helper(request, metadata_ids, metadata_pk, data_model, data_form):
    # Retrieve the metadata objects
    metadata = models.MetaData.objects.filter(id__in=metadata_ids)

    # If we have post data from the metadata select form...
    # this takes precedence over the metadata_pk passed in as an arg (comes through admin panel)
    if request.method == 'POST':
        # We want to display the data belonging to the requested metadata
        metadata_for_display = request.POST['datasets']

        # Create a form instance and populate it with the post data so the right option is selected
        form = data_form(request.POST, metadata=metadata)
    # Otherwise, if we are showing the page for the first time...
    else:
        # Create a form with the list of metadata for selection with any preselected options (passed through admin)
        form = data_form(metadata=metadata)
        if metadata_pk:
            form.fields['datasets'].initial = metadata_pk
            metadata_for_display = metadata_pk
        else:
            # If there's no preselected option passed via the URL we
            # want to display the data belonging to the most recent metadata
            metadata_for_display = metadata[0].pk

    # Retrieve the data
    data = data_model.filter(metadata=metadata_for_display)

    # Generate the flagging form for this dataset
    flag_for_removal_form = forms.RemovalFlagCreateForm(initial={'requested_by': request.user, 'metadata': metadata_for_display})

    # Add the response data
    return {'form': form,
            'flag_for_removal_form': flag_for_removal_form,
            'data_set': data}


def population_data(request, pk, metadata_pk=None):
    # The following is a bit long winded, but I can't think of any other way of doing it
    # Get a queryset of the data objects for this project and then the corresponding metadata ids
    relevant_data = models.PopulationData.objects.filter(metadata__project__pk=pk)
    metadata_ids = relevant_data.values_list('metadata', flat=True).distinct()

    # If we have any metadata for this project, retrieve the corresponding data objects
    if metadata_ids:
        response_data = dataset_display_helper(request=request,
                                               metadata_ids=metadata_ids,
                                               metadata_pk=metadata_pk,
                                               data_model=models.PopulationData.objects,
                                               data_form=forms.DataViewForm)
    else:
        response_data = {}

    # Retrieve the project
    response_data['project'] = models.Project.objects.get(pk=pk)

    # Render the context
    return render_to_response('core/project_population_data.html',
                              response_data,
                              RequestContext(request))


def get_focal_site_locations(user, pk):
    # Only trusted users should be able to view sensitive focal site locations
    if user.has_perm('core.trusted'):
        focal_sites = models.FocalSite.objects.filter(project__pk=pk)
    else:
        focal_sites = models.FocalSite.objects.filter(project__pk=pk, sensitive=False)

    if focal_sites:
        # Get the focal site location geojson. Note we are using our own geojson serializer for this to get the display name
        fields = ('location', 'activity', 'name', 'order', 'habitat', 'id')
        return FocalSiteJSONSerializer().serialize(focal_sites, geometry_field='location', fields=fields,
                                                   use_natural_foreign_keys=True, use_natural_primary_keys=True)
    else:
        return False


def focal_site_data(request, pk, focal_site_pk=None, metadata_pk=None):
    # Holds all of the variables we're passing to the template
    response_data = {}

    # If the user has selected a particular focal site they must be able to select different metadata
    if focal_site_pk:
        # Get a queryset of the data objects for this project AND this focal site and then the corresponding metadata ids
        relevant_data = models.FocalSiteData.objects.filter(metadata__project__pk=pk, focal_site__pk=focal_site_pk)
        metadata_ids = relevant_data.values_list('metadata', flat=True).distinct()

        if metadata_ids:
            # Populates form, flag_for_removal form and data_set
            response_data = dataset_display_helper(request=request,
                                                   metadata_ids=metadata_ids,
                                                   metadata_pk=metadata_pk,
                                                   data_model=models.FocalSiteData.objects,
                                                   data_form=forms.DataViewForm)

        # We need to know which one has been selected for the map
        response_data['focal_site_pk'] = focal_site_pk

    response_data['focal_site_locations'] = get_focal_site_locations(request.user, pk)

    # Get the project location geojson
    project = models.Project.objects.filter(pk=pk)
    response_data['project_location'] = serialize('geojson', project, geometry_field='location', fields=('location',))

    # Add the project object to the response data
    response_data['project'] = project[0]

    # Render the context
    return render_to_response('core/project_focal_site_data.html',
                              response_data,
                              RequestContext(request))


def fatality_data(request, pk, metadata_pk=None):
    # The following is a bit long winded, but I can't think of any other way of doing it
    # Get a queryset of the data objects for this project and then the corresponding metadata ids
    relevant_data = models.FatalityData.objects.filter(metadata__project__pk=pk)
    metadata_ids = relevant_data.values_list('metadata', flat=True).distinct()

    # Get the project location geojson
    project = models.Project.objects.filter(pk=pk)

    # If we have any metadata for this project, retrieve the corresponding data objects
    if metadata_ids:
        response_data = dataset_display_helper(request=request,
                                               metadata_ids=metadata_ids,
                                               metadata_pk=metadata_pk,
                                               data_model=models.FatalityData.objects,
                                               data_form=forms.DataViewForm)

        # Add some mapping data
        # Do we need some kind of permissions thing here? Does it matter if dead sensitive species are shown?
        # if request.user.has_perm('core.trusted'):
        response_data['fatality_locations'] = \
            CustomGeoJSONSerializer().serialize(response_data['data_set'],
                                                geometry_field='coordinates',
                                                fields=('coordinates', 'taxa', 'cause_of_death'),
                                                use_natural_foreign_keys=True,
                                                use_natural_primary_keys=True)

        # Add the project polygon and turbine locations
        response_data['project_location'] = serialize('geojson', project, geometry_field='location', fields=('location',))
        response_data['turbine_locations'] = serialize('geojson',
                                                       project,
                                                       geometry_field='turbine_locations',
                                                       fields=('turbine_locations',))
    else:
        response_data = {}

    # Add the project object to the response data
    response_data['project'] = project[0]

    # Render the context
    return render_to_response('core/project_fatality_data.html',
                              response_data,
                              RequestContext(request))


def request_status(request, status):
    # Retrieve the correct group for users, note the regex in the urls stops this being anything weird
    group = Group.objects.get(name=status)

    # Add the user to the group
    request.user.groups.add(group)

    # Redirect the user
    return redirect('profile_update')


def flag_for_removal(request, pk):
    # Flag a dataset for removal
    # If the form has been submitted and is valid
    if request.method == 'POST':
        # Create a form instance and populate it with the post data
        form = forms.RemovalFlagCreateForm(request.POST)

        # Security check
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False})


import django_filters
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


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
    geojsons = serialize('geojson', f)
    return render(request, 'core/projects_map.html', {'geojson': geojsons, 'filter': f})
