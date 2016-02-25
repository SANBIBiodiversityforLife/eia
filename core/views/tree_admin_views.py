# Core & settings
from core import models
from django.conf import settings
import requests
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.management import call_command
import time
from django.views.generic.base import RedirectView


def get_api_info(api_url):
    time_delay = 0
    r = False
    while not r:
        try:
            time.sleep(time_delay)
            r = requests.get(api_url)
        except ConnectionError:
            # Add 5 seconds onto the time delay
            time_delay += 15
            # Print out so we can monitor it
            print('Timed out, trying again in ' + time_delay + ' seconds')
    return r


class ResetTaxaTree(RedirectView):
    iucn_sa_occurrences = {}
    pattern_name = 'admin'

    def get_redirect_url(self, *args, **kwargs):
        # self.reset_taxa_tree()
        return super(ResetTaxaTree, self).get_redirect_url(*args, **kwargs)

    def reset_taxa_tree(self):
        # Empty taxon table and reload from fixture with base classes (Aves & chiroptera, parents, and unknown)
        models.Taxon.objects.all().delete()

        # Load it all again from the fixture
        call_command('loaddata', 'core_taxon')

        # Select the root items Chiroptera order (bats) & Aves class (birds)
        taxa = models.Taxon.objects.filter(is_root=True)

        # Retrieve IUCN list of all species in SA to reference against in your recursive tree builder
        r = get_api_info(settings.IUCN_API_OCCURRENCE_URL)
        self.iucn_sa_occurrences = r.json()['result']

        # Now all we have left is the items which we need to rebuild the db from
        for taxon in taxa:
            self.recursive_tree_builder(taxon.id)

    def recursive_tree_builder(self, parent_id):
        end_of_records = False
        offset = 0

        while not end_of_records:
            # Get the data
            r = get_api_info(settings.GBIF_API_CHILDREN_URL.format(id=parent_id, offset=offset))

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

                # First check the iucn and see if exists in that database
                iucn_category = False
                for occ in self.iucn_sa_occurrences:
                    if occ['scientific_name'].lower() == child['canonicalName'].lower():
                        print('IUCN - ' + occ['scientific_name'] + ' / ' + occ['category'])
                        iucn_category = occ['category']
                        break

                if not iucn_category:
                    # Check and see if there are any SA occurrence records on GBIF
                    r = get_api_info(settings.GBIF_API_OCCURRENCE_URL.format(id=taxon_id, limit=0))

                    # Get the jsoned data
                    occurrences = r.json()

                    print('GBIF - There are ' + str(occurrences['count']) + ' in SA for ' +
                          str(taxon_id) + ' = ' + child['canonicalName'])

                    # Skip this bit of the loop if they're not in SA
                    if occurrences['count'] == 0:
                        continue

                    # Right, so sometimes there's 1 or 2 random specimens stored in museums, these must be eliminated
                    if occurrences['count'] <= 3:
                        r = get_api_info(settings.GBIF_API_OCCURRENCE_URL.format(id=taxon_id,
                                                                                 limit=3) +
                                         '&basisofrecord=PRESERVED_SPECIMEN')
                        records = r.json()['results']

                        valid = False
                        for rec in records:
                            if rec['basisOfRecord'] == 'HUMAN_OBSERVATION':
                                valid = True

                        if not valid:
                            continue

                # Sanity print!
                print(' --- IN SA : ' + child['canonicalName'] + '(' + child['rank'] + ') - ' + str(taxon_id))

                # Populate the taxon object
                taxon = models.Taxon(name=child['canonicalName'],
                                     rank=rank,
                                     id=taxon_id,
                                     parent_id=parent_id)

                # Sometimes we don't have vernac name, so add that only if we have it
                if 'vernacularName' in child:
                    taxon.vernacular_name = child['vernacularName']

                if iucn_category:
                    taxon.red_list = iucn_category

                # Save the taxon
                taxon.save()

                # Recursion
                self.recursive_tree_builder(taxon_id)

            # Are we at the end of the records? if so we need to break out of the loop
            end_of_records = data['endOfRecords']

            # Increase the offset in case we are not at the end of records
            offset += settings.GBIF_API_OFFSET


def sync_iucn_redlisting(request):
    taxa = models.Taxon.objects.all()

    # Loop through allllllll the taxa
    for taxon in taxa:
        r = get_api_info(settings.IUCN_API_URL.format(name=taxon.name))

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
