from django.contrib.gis.db import models
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User, Group
from core.multiple_select_field import MultipleSelectField
from django.utils import formats
from mptt.models import MPTTModel, TreeForeignKey

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    #first_name = models.CharField(max_length=100)
    #last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    #profile_type_choices = models.ManyToManyField(ProfileTypeChoices)

    TYPE_CHOICES = (
        ('NG', 'NGO employee'),
        ('AC', 'Academic'),
        ('EI', 'EIA consultant'),
        ('PU', 'Member of the public'),
        ('BA', 'Bat specialist'),
        ('BI', 'Bird specialist'),
        ('DE', 'Developer'),
        ('OT', 'Other')
    )
    type = models.CharField(max_length=2, choices=TYPE_CHOICES)

    def get_absolute_url(self):
        return reverse('profile_detail')


class Developer(models.Model):
    """The companies who run the projects."""
    name = models.CharField(max_length=100, unique=True)
    email = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('developer_detail', kwargs={'pk': self.pk})


class EquipmentMake(models.Model):
    """Normalising the turbine make to avoid typos and to make it easier to search by turbine make."""
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('projects_list')


class Project(models.Model):
    """A renewable energy development."""
    # This information can change over time
    # However, I am storing it in the main table as it is UNLIKELY for most projects that they will experience name and
    # developer changes. Usually names will stay the same and so will the developer.
    # See http://stackoverflow.com/questions/2253962/should-i-add-this-new-column-to-customers-table-or-to-a-separate-new-table
    # http://stackoverflow.com/questions/2834361/should-i-store-logging-information-in-main-database-table
    name = models.CharField(max_length=50, unique=True)
    developer = models.ForeignKey(Developer)

    # Additional information
    location = models.PolygonField()
    objects = models.GeoManager()
    eia_number = models.CharField(max_length=20)

    WIND = 'W'
    SOLAR = 'S'
    ENERGY_TYPE_CHOICES = (
        (WIND, 'Wind turbine'),
        (SOLAR, 'Solar panels')
    )
    energy_type = models.CharField(max_length=1, choices=ENERGY_TYPE_CHOICES, default=WIND)

    # Operation details
    operational_date = models.DateField(null=True, blank=True)
    construction_date = models.DateField(null=True, blank=True)

    # Turbine location needs to be stored as points, solar panels are polygons
    turbine_locations = models.MultiPointField(null=True, blank=True)
    solar_panel_locations = models.PolygonField(null=True, blank=True)

    # Store info about the turbines/solar panels
    equipment_make = models.ForeignKey(EquipmentMake, null=True, blank=True)
    equipment_capacity = models.IntegerField(null=True, blank=True)
    equipment_height = models.IntegerField(null=True, blank=True)

    def get_absolute_url(self):
        return reverse('project_update_operational_info', kwargs={'pk': self.pk})

    def __str__(self):
        return self.name

    # Add a popup for the maps, see http://fle.github.io/easy-webmapping-with-django-leaflet-and-django-geojson.html
    def popup_content(self):
        return self.name + ' ' + self.developer

    def clean(self):
        # Coordinate cannot be outside the bounds of the project
        if self.turbine_locations:
            if not self.location.contains(self.turbine_locations):
                raise ValidationError({'turbine_locations': 'Turbine locations must be within the project bounds.'})
        elif self.solar_panel_locations:
            if not self.location.contains(self.solar_panel_locations):
                raise ValidationError({'solar_panel_locations': 'Solar panel locations must be within the project bounds.'})

    class Meta:
        permissions = (
            ('contributor', 'Can contribute data (i.e. upload datasets and create projects)'),
            ('trusted', 'Can view sensitive data'),
            ('request_contributor', 'Has requested contributor status'),
            ('request_trusted', 'Has requested trusted status'),
        )


class PreviousProjectNames(models.Model):
    """
    Renewable energy projects frequently change name. A list of all the previous names needs to be held for search
    purposes.
    """
    previous_name = models.CharField(max_length=50)
    project = models.ForeignKey(Project)
    stopped = models.DateTimeField(auto_now_add=True)


class PreviousDevelopers(models.Model):
    """
    Developers go bust and change projects, so we need to keep historical records of all the developers who worked on
    a particular project.
    """
    developer = models.ForeignKey(Developer)
    project = models.ForeignKey(Project)
    stopped = models.DateTimeField(auto_now_add=True)


class Documents(models.Model):
    """
    Scanned in documents should be uploadable.
    Note that DEA are collecting EIA reports separately, but until we get the two linked up this can be used to store
    EIA reports as well.
    """
    name = models.CharField(max_length=20)
    project = models.ForeignKey(Project)
    uploaded = models.DateTimeField(auto_now_add=True)
    # TODO uploader =

    EIA = 'E'
    OTHER = 'O'
    DOCUMENT_TYPE_CHOICES = (
        (EIA, 'EIA report'),
        (OTHER, 'Other')
    )
    document_type = models.CharField(max_length=1, choices=DOCUMENT_TYPE_CHOICES, default=EIA)


"""
class TaxonLevelDefinitions(models.Model):
    name = models.CharField(max_length=50, unique=True)
    depth = models.SmallIntegerField(unique=True)


class TaxaFunctionalGroup(models.Model):
    order = models.ForeignKey(TaxaOrder)
    functional_group = models.CharField(max_length=20)

    def __str__(self):
        return self.functional_group

    def natural_key(self):
        return self.__str__()

"""


class Taxon(MPTTModel):
    # Scientific and common names
    name = models.CharField(max_length=100)
    vernacular_name = models.CharField(max_length=100, null=True, blank=True)

    # This is used by mptt to build trees, we are just translating directly from GBIF's data
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)

    # It is important to know when this name was last updated
    updated = models.DateTimeField(auto_now_add=True)

    # We want to keep a list of root taxa rather than getting all birds & bats
    # This way our taxa building tree mechanism is more robust & flexible
    # So for example, people can add new taxon roots which are snakes or plants or something
    is_root = models.BooleanField(default=False)

    # This is the GBIF id for the taxon, it will always be unique so let's use it as the PK
    id = models.IntegerField(primary_key=True)

    # I don't think we can map taxonomic levels directly to depth because some levels are optional, e.g. superfamily
    # Plus they might get changed in time e.g. subspecies might get added. So we are going to steal Specify's tactic:
    # level = models.ForeignKey(TaxonLevelDefinitions)
    # Actually no, I think we can safely see the taxonomic backbone as set in stone, this is how BRAHMS works
    KINGDOM = 'KI'
    PHYLUM = 'PH'
    CLASS = 'CL'
    ORDER = 'OR'
    FAMILY = 'FA'
    GENUS = 'GE'
    SPECIES = 'SP'
    INFRASPECIFIC_NAME = 'IN'
    SUBSPECIES = 'SU'
    RANK_CHOICES = (
        (KINGDOM, 'Kingdom'),
        (PHYLUM, 'Phylum'),
        (CLASS, 'Class'),
        (ORDER, 'Order'),
        (FAMILY, 'Family'),
        (GENUS, 'Genus'),
        (INFRASPECIFIC_NAME, 'Infraspecific name'),
        (SPECIES, 'Species'),
        (SUBSPECIES, 'Subspecies')
    )
    rank = models.CharField(max_length=2, choices=RANK_CHOICES, default=SPECIES)

    # Often we want to just refer to actual species or subspecies

    # Red list info will come from the IUCN using the API http://api.iucnredlist.org/index/species/Aves.js
    red_list_choices = (
        ('EX', 'Extinct'),
        ('EW', 'Extinct in the Wild'),
        ('CR', 'Critically Endangered'),
        ('EN', 'Endangered'),
        ('VU', 'Vulnerable'),
        ('NT', 'Near Threatened'),
        ('LC', 'Least Concern'),
        ('DD', 'Data Deficient')
    )
    red_list = models.CharField(max_length=2, choices=red_list_choices, default='LC')

    # I am not sure about where sensitive species will come from
    sensitive = models.BooleanField(default=False)

    # Required for the MPTT model class
    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        return self.name


class FocalSite(models.Model):
    """
    Focal sites are locations of particular interest in projects.
    Data is collected and stored against each focal site.
    """
    location = models.PolygonField()
    name = models.CharField(max_length=50)
    taxon = models.ForeignKey(Taxon)
    project = models.ForeignKey(Project)
    objects = models.GeoManager()
    sensitive = models.BooleanField(default=False)

    ROOST = 'R'
    COURTSHIP = 'C'
    FEEDING = 'F'
    OTHER = 'O'
    activity_choices = (
        (ROOST, 'Roost'),
        (COURTSHIP, 'Display/courtship area'),
        (FEEDING, 'Feeding ground'),
        (OTHER, 'Other')
    )
    activity = models.CharField(max_length=1, choices=activity_choices)

    # Note: For habitat we need to store anything that is not stored in another db

    # Bats
    BUILDING = 'BU'
    BRIDGE = 'BR'
    CAVE = 'CA'
    CREVICE = 'CR'
    CULVERT = 'CU'
    MINE = 'MI'
    FRUITTREES = 'FT'

    # Birds
    TREES = 'TR'
    CLEARING = 'CL'
    SCRUB = 'SC'
    WATER = 'WA'
    habitat_choices = (
        (BUILDING, 'Building'),
        (BRIDGE, 'Bridge'),
        (CAVE, 'Cave/ridge or underhanging'),
        (CREVICE, 'Rocky crevice'),
        (CULVERT, 'Culvert'),
        (MINE, 'Mine'),
        (FRUITTREES, 'Fruit trees'),
        (TREES, 'Trees'),
        (CAVE, 'Cave/ridge or underhanging'),
        (CLEARING, 'Clearing'),
        (SCRUB, 'Grassy/shrubby area'),
        (WATER, 'Water body (e.g. pond, pool, etc)')
    )
    habitat = models.CharField(max_length=2, choices=habitat_choices)

    def get_absolute_url(self):
        return reverse('focal_site_data', kwargs={'pk': self.project.pk})

    def clean(self):
        # Coordinate cannot be outside the bounds of the project
        if not self.project.location.contains(self.location):
            raise ValidationError({'location': 'Focal sites must be within the project bounds.'})

class MetaData(models.Model):
    """
    Metadata for the 3 different types of datasets - population data, focal site data, fatality data
    """
    project = models.ForeignKey(Project)
    collected_to = models.DateTimeField()
    collected_from = models.DateTimeField()
    flagged_for_query = models.BooleanField(default=False)
    control_data = models.BooleanField("This is control data", default=False)
    uploader = models.ForeignKey(User)
    uploaded_on = models.DateTimeField(auto_now_add=True)

    # Following two functions are taken from
    # http://stackoverflow.com/questions/7366363/adding-custom-django-model-validation
    # See also the docs https://docs.djangoproject.com/en/1.8/ref/models/instances/
    def clean(self):
        if self.collected_from >= self.collected_to:
            raise ValidationError({'collected_from': 'The collected from date must be earlier than the to date'})
        super(MetaData, self).clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        super(MetaData, self).save(*args, **kwargs)

    def is_post_construction(self):
        if self.project.construction_date:
            return self.collected_from.date() > self.project.construction_date
        else:
            # There is no construction date up yet
            return False

    def __str__(self):
        text = 'Collected: ' + formats.date_format(self.collected_from, "DATETIME_FORMAT") + ' - ' + \
               formats.date_format(self.collected_to, "DATETIME_FORMAT")
        if self.is_post_construction():
            text += '(post construction)'
        else:
            text += '(pre construction)'
        text += ' | Uploaded by ' + self.uploader.first_name + ' ' + self.uploader.last_name + ' on ' + \
                formats.date_format(self.uploaded_on, "DATETIME_FORMAT")
        if self.control_data:
            text += ' (control data)'
        return text

    def get_data_object(self):
        # Population data
        models.PopulationData.objects.get(metadata=self)


class PopulationData(models.Model):
    """
    Census, focal point & transect data form a population count/estimate
    """
    metadata = models.ForeignKey(MetaData)
    taxa = models.ForeignKey(Taxon)
    count = models.IntegerField()  # Actual number counted / for bats this activity levels or number of passes

    COLLISION_HIGH = 'H'
    COLLISION_MEDIUM = 'M'
    COLLISION_LOW = 'L'
    collision_risk_choices = (
        (COLLISION_HIGH, 'High risk of collision'),
        (COLLISION_MEDIUM, 'Medium risk of collision'),
        (COLLISION_LOW, 'Low risk of collision')
    )
    collision_risk = models.CharField(max_length=1, choices=collision_risk_choices)

    # Birds only:
    density_km = models.DecimalField(max_digits=10, decimal_places=5)  # Estimate of density per km^2
    passage_rate = models.DecimalField(max_digits=7, decimal_places=2)  # Number passing through area per hour

    def get_absolute_url(self):
        return reverse('project_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.collision_risk


class FocalSiteData(models.Model):
    """
    Records activity for a particular focal site
    """
    metadata = models.ForeignKey(MetaData)
    taxa = models.ForeignKey(Taxon)
    focal_site = models.ForeignKey(FocalSite)
    count = models.IntegerField()

    life_stage_choices = (
        ('C', 'Chick/pup'),
        ('J', 'Juvenile'),
        ('A', 'Adult')
    )
    life_stage = models.CharField(max_length=1, choices=life_stage_choices, default='A')

    # Only applicable to birds
    activity_choices = (
        ('CDP', 'courtship display'),
        ('CAN', 'adult bird carrying nesting material'),
        ('ANB', 'active nest building'),
        ('NCN', 'newly completed nest'),
        ('NWE', 'nest with eggs'),
        ('NWC', 'nest with chicks'),
        ('PFY', 'parents feeding young in nest'),
        ('PFS', 'parents with fecal sac'),
        ('PAY', 'parents and young not in nest')
    )
    activity = models.CharField(max_length=3, choices=activity_choices, null=True, blank=True)


class FatalityData(models.Model):
    """
    Records fatalities
    """
    metadata = models.ForeignKey(MetaData)
    taxa = models.ForeignKey(Taxon)
    coordinates = models.PointField()
    objects = models.GeoManager()

    cause_of_death_choices = (
        ('T', 'Turbine'),
        ('R', 'Road'),
        ('S', 'Solar panel'),
        ('E', 'Power lines (electric)'),
        ('N', 'Natural'),
        ('P', 'Predation'),
        ('U', 'Undetermined')
    )
    cause_of_death = models.CharField(max_length=1, choices=cause_of_death_choices)

    def clean(self):
        # Coordinate cannot be outside the bounds of the project
        if not self.metadata.project.location.contains(self.coordinates):
            raise ValidationError({'coordinates': 'Fatality coordinates are outside the project polygon bounds.'})


class RemovalFlag(models.Model):
    """
    Allows users to flag datasets for removal
    """
    metadata = models.ForeignKey(MetaData)
    reason = models.TextField(max_length=2000)
    requested_by = models.ForeignKey(User)
    requested_on = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        return reverse('projects_list')