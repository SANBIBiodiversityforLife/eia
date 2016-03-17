# Django rendering stuff
from django.shortcuts import render_to_response, render, redirect
from django.views.generic import CreateView

# Core & settings
from core import models, forms

# JSON & serialization
from django.http import JsonResponse
import json
from django.contrib.gis.geos import Point

# Datetime
from datetime import datetime, timedelta


def population_data_create(request, project_pk):
    # Retrieve the project for passing to context and the form
    project = models.Project.objects.get(pk=project_pk)

    # Add the data-type-specific headers and count types for handsontable to the context
    context = {'project': project,
               'headers': [models.PopulationData.taxon_help,
                           models.PopulationData.abundance_help,
                           models.PopulationData.observed_help,
                           'Time (24h)<br>Round to hr',  # Split up date and time
                           models.PopulationData.abundance_type_help,
                           models.PopulationData.flight_height_help],
               'count_types': list(models.PopulationData.ABUNDANCE_TYPE_CHOICES)}

    # Process the submitted data
    if request.is_ajax():
        # First, the population metadata form (location, survey type, hours)
        population_metadata_form = forms.PopulationMetaDataCreateForm(request.POST)

        # Run basic validation and return any errors
        if not population_metadata_form.is_valid():
            return JsonResponse(population_metadata_form.errors, status=400)

        # Create the metadata
        metadata = models.MetaData(project=project, uploader=request.user)
        metadata.save()

        # The metadata specific to population type data can get saved at this point
        population_metadata = population_metadata_form.save(commit=False)
        population_metadata.metadata = metadata
        population_metadata.save()

        # Retrieve the hot_data
        hot_data = json.loads(request.POST['hot_data'])

        # We sometimes get validation errors, so wrap in a try
        try:
            objects = []
            for row in hot_data:
                print(row)
                # Often the last row seems to be blank, so if row[0 - 5] is blank skip it
                if all(r is None for r in row):
                    continue

                # Try get the taxa by scientific name
                taxon = models.Taxon.objects.filter(name=row[0])

                if not taxon:
                    # If that doesn't work try get it by common name
                    taxon = models.Taxon.objects.filter(vernacular_name=row[0])

                    if not taxon:
                        raise ValueError('No taxa found, something has gone wrong')

                taxon = taxon[0]

                # Abundance/count
                count = row[1]

                # Get a datetime from the time + date
                observed = datetime.strptime(row[2], '%d/%m/%Y') + timedelta(hours=row[3])

                # Count type
                abundance_type_choices = {v: k for k, v in dict(models.PopulationData.ABUNDANCE_TYPE_CHOICES).items()}
                abundance_type = abundance_type_choices[row[4]]  # At this stage it will raise a KeyError if the key is not found

                # Create - does this validate? i hope so
                obj = models.PopulationData(metadata=metadata,
                                            taxon=taxon,
                                            observed=observed,
                                            abundance=count,
                                            abundance_type=abundance_type)

                # Flight height integer range
                if row[5]:
                    flight_height = row[5].split('-')
                    flight_height = (int(flight_height[0]), int(flight_height[1]))
                    obj.flight_height = flight_height

                # Add to the list
                objects.append(obj)

            # Now we have successfully got all our taxa sorted, we save them
            for obj in objects:
                obj.save()

            # Return how many saved (should always be all, just to provide reassurance to them)
            return JsonResponse({'objects_saved': len(objects), 'metadata_pk': metadata.pk})
        except ValueError as e:
            # Delete the metadata
            metadata.delete()
            population_metadata.delete()

            # Send error back to form
            return JsonResponse({'error': e.args()}, status=400)

    # Otherwise, if we are showing the page for the first time, make the form
    context['map_form'] = forms.PopulationMetaDataCreateForm(project_polygon=project.location)

    # Get all the taxa
    taxa = models.Taxon.objects.filter(rank__in=[models.Taxon.GENUS, models.Taxon.SPECIES, models.Taxon.SUBSPECIES]) | \
           models.Taxon.objects.filter(id=0)

    # Get the scientific and vernacular names separately
    scientific_names = list(taxa.values_list('name', flat=True).distinct())
    vernacular_names = list(taxa.values_list('vernacular_name', flat=True).distinct())

    # Merge the two together, note it's going into a dropdown so can't have duplicate values anyway
    # When we reinterpret it coming back we can just assume it's a scientific name first and vernacular second
    names = scientific_names + vernacular_names

    # Get rid of the none value as it throws the js out (creeps in with vernacular names)
    names = [n for n in names if n is not None]
    context['taxa'] = names

    # Show the template
    return render(request, 'core/population_data_create.html', context)


def focal_site_data_create(request, project_pk, focal_site_pk):
    # Retrieve the project for passing to context and the form
    project = models.Project.objects.get(pk=project_pk)

    # Add the data-type-specific headers and count types for handsontable to the context
    context = {'project': project,
               'focal_site_pk': focal_site_pk,
               'headers': [models.FocalSiteData.taxon_help,
                           models.FocalSiteData.abundance_help,
                           models.FocalSiteData.observed_help,
                           'Time (24h)<br>Round to hr',  # Split up date and time
                           models.FocalSiteData.life_stage_help,
                           models.FocalSiteData.activity_choices_help],
               'life_stage_choices': list(models.FocalSiteData.LIFE_STAGE_CHOICES),
               'activity_choices': list(models.FocalSiteData.ACTIVITY_CHOICES)}

    # Process the handsontable data
    if request.is_ajax():
        # Retrieve the hot_data
        hot_data = json.loads(request.POST['hot_data'])

        # Create the metadata
        metadata = models.MetaData(project=project, uploader=request.user)
        metadata.save()

        # We mustn't save anything unless they are all ok, so wrap in a try
        try:
            objects = []
            for row in hot_data:
                print(row)
                # Often the last row seems to be blank, so if row[0 - 5] is blank skip it
                if all(r is None for r in row):
                    continue

                # Try get the taxa by scientific name
                taxon = models.Taxon.objects.filter(name=row[0])

                if not taxon:
                    # If that doesn't work try get it by common name
                    taxon = models.Taxon.objects.filter(vernacular_name=row[0])

                    if not taxon:
                        raise ValueError('No taxa found, something has gone wrong')
                print('taxon')

                taxon = taxon[0]

                # Abundance/count
                count = row[1]

                # Get a datetime from the time + date
                observed = datetime.strptime(row[2], '%d/%m/%Y') + timedelta(hours=row[3])

                # Life stage
                life_stage_choices = {v: k for k, v in dict(models.FocalSiteData.LIFE_STAGE_CHOICES).items()}
                life_stage = life_stage_choices[row[4]]  # At this stage it will raise a KeyError if the key is not found

                # Activity
                activity_choices = {v: k for k, v in dict(models.FocalSiteData.ACTIVITY_CHOICES).items()}
                activity = activity_choices[row[5]]  # At this stage it will raise a KeyError if the key is not found

                # Create - does this validate? i hope so
                obj = models.FocalSiteData(metadata=metadata,
                                           taxon=taxon,
                                           observed=observed,
                                           abundance=count,
                                           life_stage=life_stage,
                                           activity=activity,
                                           focal_site_id=focal_site_pk)  # Instead of focal_site = obj

                # Add to the list
                objects.append(obj)

            # Now we have successfully got all our taxa sorted, we save them
            for obj in objects:
                obj.save()

            # Return how many saved (should always be all, just to provide reassurance to them)
            return JsonResponse({'objects_saved': len(objects), 'metadata_pk': metadata.pk})
        except ValueError as e:
            # Delete the metadata
            metadata.delete()

            # Send error back to form
            return JsonResponse({'error': e.args()}, status=400)

    # Otherwise, if we are showing the page for the first time...
    # Get all the taxa
    taxa = models.Taxon.objects.filter(rank__in=[models.Taxon.GENUS, models.Taxon.SPECIES, models.Taxon.SUBSPECIES]) | \
           models.Taxon.objects.filter(id=0)

    # Get the scientific and vernacular names separately
    scientific_names = list(taxa.values_list('name', flat=True).distinct())
    vernacular_names = list(taxa.values_list('vernacular_name', flat=True).distinct())

    # Merge the two together, note it's going into a dropdown so can't have duplicate values anyway
    # When we reinterpret it coming back we can just assume it's a scientific name first and vernacular second
    names = scientific_names + vernacular_names

    # Get rid of the none value as it throws the js out (creeps in with vernacular names)
    names = [n for n in names if n is not None]
    context['taxa'] = names

    # Show the template
    return render(request, 'core/focal_site_data_create.html', context)


def fatality_data_create(request, project_pk):
    # Retrieve the project for passing to context and the form
    project = models.Project.objects.get(pk=project_pk)

    # Add the data-type-specific headers and count types for handsontable to the context
    context = {'project': project,
               'headers': [models.FatalityData.taxon_help,
                           models.FatalityData.found_help,
                           'Time (24h)<br>Round to hr',  # Split up date and time
                           'Latitude',
                           'Longitude',
                           models.FatalityData.cause_of_death_help],
               'cause_of_death_choices': list(models.FatalityData.cause_of_death_choices)}

    # Process the handsontable data
    if request.is_ajax():
        # Retrieve the hot_data
        hot_data = json.loads(request.POST['hot_data'])

        # Create the metadata
        metadata = models.MetaData(project=project, uploader=request.user)
        metadata.save()

        # We mustn't save anything unless they are all ok, so wrap in a try
        try:
            objects = []
            for row in hot_data:
                print(row)
                # Often the last row seems to be blank, so if row[0 - 5] is blank skip it
                if all(r is None for r in row):
                    continue

                # Try get the taxa by scientific name
                taxon = models.Taxon.objects.filter(name=row[0])

                if not taxon:
                    # If that doesn't work try get it by common name
                    taxon = models.Taxon.objects.filter(vernacular_name=row[0])

                    if not taxon:
                        raise ValueError('No taxa found, something has gone wrong')

                taxon = taxon[0]

                # Get a datetime from the time + date
                found = datetime.strptime(row[1], '%d/%m/%Y') + timedelta(hours=row[2])

                # Point
                coordinates = Point(row[4], row[3])

                # Cause of death
                cause_of_death_choices = {v: k for k, v in dict(models.FatalityData.cause_of_death_choices).items()}
                cause_of_death = cause_of_death_choices[row[5]]  # At this stage it will raise a KeyError if the key is not found

                # Create - does this validate? i hope so
                obj = models.FatalityData(metadata=metadata,
                                          taxon=taxon,
                                          found=found,
                                          coordinates=coordinates,
                                          cause_of_death=cause_of_death)

                # Add to the list
                objects.append(obj)

            # Now we have successfully got all our taxa sorted, we save them
            for obj in objects:
                obj.save()

            # Return how many saved (should always be all, just to provide reassurance to them)
            return JsonResponse({'objects_saved': len(objects), 'metadata_pk': metadata.pk})
        except ValueError as e:
            # Delete the metadata
            metadata.delete()

            # Send error back to form
            return JsonResponse({'error': e.args()}, status=400)

    # Otherwise, if we are showing the page for the first time...
    # Get all the taxa
    taxa = models.Taxon.objects.filter(rank__in=[models.Taxon.GENUS, models.Taxon.SPECIES, models.Taxon.SUBSPECIES]) | \
           models.Taxon.objects.filter(id=0)

    # Get the scientific and vernacular names separately
    scientific_names = list(taxa.values_list('name', flat=True).distinct())
    vernacular_names = list(taxa.values_list('vernacular_name', flat=True).distinct())

    # Merge the two together, note it's going into a dropdown so can't have duplicate values anyway
    # When we reinterpret it coming back we can just assume it's a scientific name first and vernacular second
    names = scientific_names + vernacular_names

    # Get rid of the none value as it throws the js out (creeps in with vernacular names)
    names = [n for n in names if n is not None]
    context['taxa'] = names

    # Show the template
    return render(request, 'core/fatality_data_create.html', context)


class FatalityRateCreate(CreateView):
    model = models.FatalityRate
    template_name = 'core/fatality_rate_create.html'
    form_class = forms.FatalityRateCreateForm

    def get_form_kwargs(self):
        kwargs = super(FatalityRateCreate, self).get_form_kwargs()
        kwargs['project_pk'] = self.kwargs['project_pk']
        kwargs['uploader'] = self.request.user
        kwargs['rate_type'] = models.FatalityRate.FATALITY
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(FatalityRateCreate, self).get_context_data(**kwargs)
        #self.project_pk = self.kwargs['project_pk']
        context['project'] = models.Project.objects.get(pk=self.kwargs['project_pk'])
        kwargs['rate_type'] = models.FatalityRate.FATALITY
        return context

"""
    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        import pdb; pdb.set_trace()
        metadata = models.MetaData(project=self.kwargs['project_pk'], uploader=self.request.user)
        metadata.save()
        form.instance.metadata = metadata
        return super(FatalityRateCreate, self).form_valid(form)"""


class ScavengerRateCreate(FatalityRateCreate):
    """
    Subclasses the fatality rate create as we just need to override the rate_type
    """
    def get_form_kwargs(self):
        kwargs = super(ScavengerRateCreate, self).get_form_kwargs()
        kwargs['rate_type'] = models.FatalityRate.SCAVENGER
        return kwargs


class SearcherRateCreate(FatalityRateCreate):
    """
    Subclasses the fatality rate create as we just need to override the rate_type
    """
    def get_form_kwargs(self):
        kwargs = super(SearcherRateCreate, self).get_form_kwargs()
        kwargs['rate_type'] = models.FatalityRate.SEARCHER
        return kwargs
