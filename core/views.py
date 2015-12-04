#from django.shortcuts import render
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from core import models, forms
from django.http import HttpResponseRedirect, HttpResponse

from django.http import JsonResponse
from django.views.generic.edit import CreateView
from io import BytesIO

from django.core.urlresolvers import reverse
import tempfile
import os
from django.conf import settings
from core.spreadsheet_creation import create_population_data_spreadsheet
from django.core.serializers import serialize
from django.contrib.auth.decorators import login_required

def index(request):
    return render(request, 'core/index.html',{'stats': 'hello'})

class AjaxableResponseMixin(object):
    """
    Mixin to add AJAX support to a form.
    Must be used with an object-based FormView (e.g. CreateView)
    """
    def form_invalid(self, form):
        response = super(AjaxableResponseMixin, self).form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        # A custom function which should be present in all data adding forms
        xlsx_with_errors = form.process_data(project_pk=self.kwargs['project_pk'])

        # We make sure to call the parent's form_valid() method because
        # it might do some processing (in the case of CreateView, it will
        # call form.save() for example).
        # response = super(AjaxableResponseMixin, self).form_valid(form)
        # removed the above as I don't think i need it for my custom function
        import pdb; pdb.set_trace()
        if self.request.is_ajax():
            print('returning data')
            data = {
                #'pk': self.object.pk,
                'error_sheet': xlsx_with_errors
            }
            return JsonResponse(data)
        else:
            return HttpResponseRedirect(self.get_success_url())


class PopulationDataCreateView(FormView):#class PopulationDataCreateView(AjaxableResponseMixin, FormView):
    template_name = 'core/populationdata_create_form.html'
    form_class = forms.MetaDataCreateForm
    # create_population_data_spreadsheet()

    def get_success_url(self):
        return reverse('project_detail', args={'pk': self.kwargs['project_pk']})

    # No idea why this needs to go in, but it seems to http://stackoverflow.com/questions/18605008/curious-about-get-form-kwargs-in-formview
    def get_form_kwargs(self):
        kwargs = super(PopulationDataCreateView, self).get_form_kwargs()
        kwargs['project_pk'] = self.kwargs['project_pk']
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(PopulationDataCreateView, self).get_context_data(**kwargs)
        context['project_pk'] = self.kwargs['project_pk']
        return context


    def form_invalid(self, form):
        response = super(PopulationDataCreateView, self).form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        print('calling form_valid')
        # A custom function which should be present in all data adding forms
        xlsx_with_errors = form.process_data(project_pk=self.kwargs['project_pk'])
        print('back in form_valid')

        # We make sure to call the parent's form_valid() method because
        # it might do some processing (in the case of CreateView, it will
        # call form.save() for example).
        # response = super(AjaxableResponseMixin, self).form_valid(form)
        # removed the above as I don't think i need it for my custom function

        if self.request.is_ajax():
            print('returning data')
            data = {
                #'pk': self.object.pk,
                'error_sheet': xlsx_with_errors
            }
            return JsonResponse(data)
        else:
            return HttpResponseRedirect(self.get_success_url())


class FocalSiteDataCreate(CreateView):
    model = models.FocalSiteData
    template_name_suffix = '_create_form'
    form_class = forms.FocalSiteDataCreateForm


class FocalSiteCreate(CreateView):
    model = models.FocalSite
    template_name_suffix = '_create_form'
    form_class = forms.FocalSiteCreateForm


import django_filters
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

class ProjectFilter(django_filters.FilterSet):
    class Meta:
        model = models.Project
        fields = ['current_name', 'current_developer']

def project_list(request):
    f = ProjectFilter(request.GET, queryset=models.Project.objects.all())

    paginator = Paginator(f.qs, 100) # Show 100 events per page
    page = request.GET.get('page')
    try:
        projects = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        projects = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        projects = paginator.page(paginator.num_pages)

    return render(request, 'core/project_list_test.html', {'projects': projects, 'filter': f})

class ProjectList(ListView):
    model = models.Project
    context_object_name = 'projects'
    paginate_by = 10


class ProjectDetail(DetailView):
    model = models.Project
    context_object_name = 'project'


class ProjectCreate(CreateView):
    model = models.Project
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


class DeveloperCreate(CreateView):
    model = models.Developer
    fields = ['name', 'email', 'phone']
    template_name_suffix = '_create_form'


class DataList(ListView):
    model = models.Project
    context_object_name = 'projects'


class PopulationDataCreate(CreateView):
    model = models.PopulationData
    template_name_suffix = '_create_form'
    form_class = forms.PopulationDataCreateForm


@login_required
def project_detail(request, pk):
    project = models.Project.objects.filter(pk=pk)
    geojson = serialize('geojson', project)
    project = models.Project.objects.get(pk=pk)
    return render_to_response('core/project_detail.html',
                              {'geojson': geojson, 'project': project},
                              RequestContext(request))
