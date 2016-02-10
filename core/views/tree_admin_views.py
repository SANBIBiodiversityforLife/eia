# Core & settings
from core import models
from django.conf import settings
import requests


def reset_taxa_tree(request):
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
        # Get the data
        r = requests.get(settings.GBIF_API_CHILDREN_URL.format(id=parent_id, offset=offset))
        data = r.json()

        # First, loop through the children in this result set
        children = data['results']
        for child in children:
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

            # If it's a family, species, genus then check and see if there are any occurrence
            # records in SA before proceeding. If there are none then go onto the next item in the loop.
            # Maybe todo don't want to check subsp, variety etc in case they are unknown/rare/new and have no occurrence records?
            # if rank in [models.Taxon.FAMILY, models.Taxon.GENUS, models.Taxon.SPECIES]:
            r = requests.get(settings.GBIF_API_OCCURRENCE_URL.format(id=taxon_id))
            occurrences = r.json()
            if occurrences['count'] == 0:
               # print(' Not in SA : ' + child['canonicalName'] + '(' + child['rank'] + ') - ' + str(taxon_id))
                continue
            #else:
            print(' --- IN SA : ' + child['canonicalName'] + '(' + child['rank'] + ') - ' + str(taxon_id))

            # Populate and save the taxon object
            taxon = models.Taxon(name=child['canonicalName'],
                                 rank=rank,
                                 id=taxon_id,
                                 parent_id=parent_id)
            if 'vernacularName' in child:
                taxon.vernacular_name = child['vernacularName']
            taxon.save()

            # Recursion
            recursive_tree_builder(taxon_id)

        # Are we at the end of the records? if so we need to break out of the loop
        end_of_records = data['endOfRecords']

        # Increase the offset in case we are not at the end of records
        offset += settings.GBIF_API_OFFSET