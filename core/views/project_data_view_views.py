# Django rendering stuff
from django.shortcuts import render_to_response, render, redirect
from django.template import RequestContext

# Core & settings
from core import models, forms

# Serialization
from django.core.serializers import serialize
from core.serializers import CustomGeoJSONSerializer, FocalSiteJSONSerializer

# Distance
from django.contrib.gis.measure import D


def dataset_display_helper(request, metadata_ids, metadata_pk, data_model):
    # Retrieve the metadata objects
    metadata = models.MetaData.objects.filter(id__in=metadata_ids)

    # If we have post data from the metadata select form...
    # this takes precedence over the metadata_pk passed in as an arg (comes through admin panel)
    if request.method == 'POST':
        # We want to display the data belonging to the requested metadata
        metadata_for_display = request.POST['datasets']

        # Create a form instance and populate it with the post data so the right option is selected
        form = forms.DataViewForm(request.POST, metadata=metadata)
    # Otherwise, if we are showing the page for the first time...
    else:
        # Create a form with the list of metadata for selection with any preselected options (passed through admin)
        form = forms.DataViewForm(metadata=metadata)
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
    flag_for_removal_form = forms.RemovalFlagCreateForm()

    # Generate the documentation form for this dataset and get all the documents
    documents = models.Document.objects.filter(metadata=metadata_for_display)
    create_document_form = forms.DocumentCreateForm()

    # Add the response data
    return {'form': form,
            'flag_for_removal_form': flag_for_removal_form,
            'data_set': data,
            'metadata_pk': metadata_for_display,
            'create_document_form': create_document_form,
            'documents': documents}


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
                                               data_model=models.PopulationData.objects)
    else:
        response_data = {}

    # Retrieve the project
    response_data['project'] = models.Project.objects.get(pk=pk)

    # If we have any data to display
    if 'data_set' in response_data:
        # Add the project area
        response_data['project_area'] = serialize('geojson', [response_data['project']], geometry_field='location', fields=('location',))

        # Get the population specific metadata
        response_data['population_metadata'] = models.PopulationMetaData.objects.get(
            metadata__pk=response_data['metadata_pk'])

        # Is the survey area the same as the project area? If not then we need to display survey area too
        if response_data['project'].location != response_data['population_metadata'].location:
            response_data['survey_area'] = serialize('geojson', [response_data['population_metadata']],
                                                     geometry_field='location', fields=('location',))

    # Render the context
    return render_to_response('core/population_data_list.html',
                              response_data,
                              RequestContext(request))


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
                                                   data_model=models.FocalSiteData.objects)

        # We need to know which one has been selected for the map
        response_data['focal_site_pk'] = focal_site_pk

    # Get the project location geojson
    project = models.Project.objects.filter(pk=pk)
    response_data['project_location'] = serialize('geojson', project, geometry_field='location', fields=('location',))

    # Add the project object to the response data
    response_data['project'] = project[0]

    # See below, we want to get all focal sites within a xkm radius of the project location
    project_location = project[0].location

    # Only trusted users should be able to view sensitive focal site locations
    if request.user.has_perm('core.trusted'):
        focal_sites = models.FocalSite.objects.filter(location__distance_lte=(project_location, D(km=30)))
    else:
        focal_sites = models.FocalSite.objects.filter(location__distance_lte=(project_location, D(km=30)), sensitive=False)

    if focal_sites:
        # Get the focal site location geojson. Note we are using our own geojson serializer for this to get the display name
        fields = ('location', 'activity', 'name', 'habitat', 'id')
        response_data['focal_site_locations'] = FocalSiteJSONSerializer(project_pk=project[0].pk).serialize(focal_sites,
                                                                                    geometry_field='location',
                                                                                    fields=fields,
                                                                                    use_natural_foreign_keys=True,
                                                                                    use_natural_primary_keys=True)
    else:
        response_data['focal_site_locations'] = False

    # Render the context
    return render_to_response('core/focal_site_data_list.html',
                              response_data,
                              RequestContext(request))


def fatality_data(request, pk, metadata_pk=None):
    # Get the project, we need the location for the fatality points
    project = models.Project.objects.filter(pk=pk)

    # The following is a bit long winded, but I can't think of any other way of doing it
    # Get a queryset of the data objects for this project and then the corresponding metadata ids
    relevant_data = models.FatalityData.objects.filter(metadata__project__pk=pk)
    metadata_ids = relevant_data.values_list('metadata', flat=True).distinct()

    # If we have any metadata for this project, retrieve the corresponding data objects
    if metadata_ids:
        response_data = dataset_display_helper(request=request,
                                               metadata_ids=metadata_ids,
                                               metadata_pk=metadata_pk,
                                               data_model=models.FatalityData.objects)

        # Add some mapping data
        # Do we need some kind of permissions thing here? Does it matter if dead sensitive species are shown?
        # if request.user.has_perm('core.trusted'):
        response_data['fatality_locations'] = \
            CustomGeoJSONSerializer().serialize(response_data['data_set'],
                                                geometry_field='coordinates',
                                                fields=('coordinates', 'taxon', 'cause_of_death'),
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
    return render_to_response('core/fatality_data_list.html',
                              response_data,
                              RequestContext(request))


def fatality_rates(request, pk):
    # Get the project and create the response object
    project = models.Project.objects.filter(pk=pk)
    response = {'project': project[0]}

    # Get a queryset of the data objects for this project and then the corresponding metadata
    # Note we can do select_related('metadata') just for metadata, but we also need the taxa info
    fatality_rates = models.FatalityRate.objects.select_related('metadata').filter(metadata__project__pk=pk).order_by('start_date')

    # If we have any metadata for this project, retrieve the corresponding data objects
    if fatality_rates:
        # Split up the datasets into scavenger, searcher & actual estimates
        response['scavenger_rates'] = fatality_rates.filter(rate_type=models.FatalityRate.SCAVENGER)
        response['searcher_rates'] = fatality_rates.filter(rate_type=models.FatalityRate.SEARCHER)
        response['fatality_rates'] = fatality_rates.filter(rate_type=models.FatalityRate.FATALITY)

        # Generate the flagging form for these datasets
        response['flag_for_removal_form'] = forms.RemovalFlagCreateForm()

    # Render the context
    return render_to_response('core/fatality_rates_list.html',
                              response,
                              RequestContext(request))




