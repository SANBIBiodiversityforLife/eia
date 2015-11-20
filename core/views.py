#from django.shortcuts import render
from django.shortcuts import render_to_response
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

    # tmp_dir = os.path.join(settings.BASE_DIR, 'core', 'static', 'core', 'tmp')
    # fd, unique_file = tempfile.mkstemp(suffix='.xlsx', prefix='pop_', dir=tmp_dir)
    # os.close(fd)
    # print(os.path.join('static', 'core', 'tmp', os.path.basename(os.path.relpath(unique_file))))
    # TODO the above is terrible and must be fixed, serve the files through a proper webserver

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
'''
    # This method is called when valid form data has been POSTed. It should return an HttpResponse.
    def form_valid(self, form):
        # This is taking a long time...
        print('form_valid is running')

        # Run the data processing function
        form.process_data(project_pk=self.kwargs['project_pk'])

        # I don't think we need to run the super function, as the process_data should have taken care of all that
        # return super(PopulationDataCreateView, self).form_valid(form)

        return HttpResponseRedirect(self.get_success_url())'''

class FocalSiteDataCreate(CreateView):
    model = models.FocalSiteData
    template_name_suffix = '_create_form'
    form_class = forms.FocalSiteDataCreateForm


class FocalSiteCreate(CreateView):
    model = models.FocalSite
    template_name_suffix = '_create_form'
    form_class = forms.FocalSiteCreateForm


class ProjectList(ListView):
    model = models.Project
    context_object_name = 'projects'


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


'''def create_population_data(request, project_pk):
    metadata_form = forms.MetaDataCreateForm()

    if request.POST:
            metadata_form = forms.MetaDataCreateForm(request.POST, prefix='meta')
            data_form = forms.PopulationDataCreateForm(request.POST, request.FILES, prefix='meta')

            if metadata_form.is_valid() and data_form.is_valid():
                    # Prepare & save the metadata
                    metadata = metadata_form.save(commit=False)
                    metadata.project = models.Project.objects.get(pk=project_pk)
                    metadata.save()

                    # Parse the spreadsheet and get the data
                    data = request.FILES['spreadsheet']

                    # Prepare & save the data
                    data = data_form.save(commit=False)
                    data.metadata = metadata
                    data.save()

    # Create a spreadsheet with validation for them on-the-fly - note we may need to change this if it impacts performance
    workbook = xlsxwriter.Workbook('population_data_for_upload.xlsx')
    worksheet = workbook.add_worksheet()
    worksheet.write('A1', 'Hello world')
    workbook.close()

    return render_to_response('core/populationdata_create_form.html', {
        'metadata_form': metadata_form,
        'data_form': data_form,
        'project_pk': project_pk,
        },
        RequestContext(request))'''

