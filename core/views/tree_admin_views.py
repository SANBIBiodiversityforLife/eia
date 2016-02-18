# Core & settings
from core import models
from django.conf import settings
import requests
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.management import call_command
import time


def reset_taxa_tree(request):
    return
    # Empty taxon table of everything and reload from the fixture with base classes (Aves & chiroptera, parents, and unknown)
    models.Taxon.objects.all().delete()

    # Load it all again from the fixture
    call_command('loaddata', 'core_taxon')

    # Select the root items Chiroptera order (bats) & Aves class (birds)
    taxa = models.Taxon.objects.filter(is_root=True)

    # Now all we have left is the items which we need to rebuild the db from
    for taxon in taxa:
        recursive_tree_builder(taxon.id)


def recursive_tree_builder(parent_id):
    end_of_records = False
    offset = 0

    while not end_of_records:
        # Get the data, sometimes this times out so just wait a few seconds and try again
        time_delay = 0
        r = False
        while not r:
            try:
                time.sleep(time_delay)
                r = requests.get(settings.GBIF_API_CHILDREN_URL.format(id=parent_id, offset=offset))
            except ConnectionError:
                # Add 5 seconds onto the time delay
                time_delay += 15
                # Print out so we can monitor it
                print('Timed out, trying again in ' + time_delay + ' seconds')

        # Get the jsoned data
        data = r.json()

        # Loop through the children in this result set
        children = data['results']
        for child in children:
            # This is the main ID number in the GBIF system
            taxon_id = int(child['nubKey'])

            # Get the rank key
            rank = False
            for key, value in dict(models.Taxon.RANK_CHOICES).items():
                if value.lower() == child['rank'].lower():
                    rank = key

            # If we couldn't find it in our list throw an exception
            if not rank:
                raise ValueError('Rank does not exist in database: ' + child['rank'] + ' For taxon ' +
                                 child['canonicalName'] + '(' + child['rank'] + ') - ' + str(taxon_id))

            # If it's a family, species, genus then check and see if there are any SA occurrence records
            # TODO perhaps don't want to check subsp, variety etc in case they are unknown/rare and have no occ recs?
            # Again, this sometimes times out so loop it:
            time_delay = 0
            r = False
            while not r:
                try:
                    time.sleep(time_delay)
                    r = requests.get(settings.GBIF_API_OCCURRENCE_URL.format(id=taxon_id))
                except ConnectionError:
                    # Add 5 seconds onto the time delay
                    time_delay += 15
                    # Print out so we can monitor it
                    print('Timed out, trying again in ' + time_delay + ' seconds')

            # Get the jsoned data
            occurrences = r.json()

            # Skip this bit of the loop if they're not in SA
            if occurrences['count'] == 0:
                continue

            # Sanity print to make sure the thing is running
            print(' --- IN SA : ' + child['canonicalName'] + '(' + child['rank'] + ') - ' + str(taxon_id))

            # Populate the taxon object
            taxon = models.Taxon(name=child['canonicalName'],
                                 rank=rank,
                                 id=taxon_id,
                                 parent_id=parent_id)

            # Sometimes we don't have vernac name, so add that only if we have it
            if 'vernacularName' in child:
                taxon.vernacular_name = child['vernacularName']

            # Save the taxon
            taxon.save()

            # Recursion
            recursive_tree_builder(taxon_id)

        # Are we at the end of the records? if so we need to break out of the loop
        end_of_records = data['endOfRecords']

        # Increase the offset in case we are not at the end of records
        offset += settings.GBIF_API_OFFSET


def sync_iucn_redlisting(request):
    taxa = models.Taxon.objects.all()

    # Loop through allllllll the taxa
    for taxon in taxa:
        # Try and get the info from IUCN
        time_delay = 0
        r = False
        while not r:
            try:
                time.sleep(time_delay)
                r = requests.get(settings.IUCN_API_URL.format(name=taxon.name))
            except ConnectionError:
                # Add x seconds onto the time delay
                time_delay += 15
                # Print out so we can monitor it
                print('Timed out, trying again in ' + time_delay + ' seconds')

        # Get the jsoned data
        data = r.json()

        # Set the info if it is available
        result = data['result']
        if result:
            print(str(taxon) + ' - ' + result[0]['category'])
            taxon.red_list = result[0]['category']
        taxon.save()

    # Render the context
    return render_to_response('/admin/',
                              {'message': str(len(taxa)) + ' taxa updated with IUCN redlist statuses'},
                              RequestContext(request))
