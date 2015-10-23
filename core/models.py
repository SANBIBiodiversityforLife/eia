from django.contrib.gis.db import models
from django.core.urlresolvers import reverse


class Developer(models.Model):
    """The companies who run the projects."""
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)

    def __str__(self):
        return self.name


class TurbineMake(models.Model):
    """Normalising the turbine make to avoid typos and to make it easier to search by turbine make."""
    make = models.CharField(max_length=50)

    def __str__(self):
        return self.make


class Project(models.Model):
    """A renewable energy development."""
    current_name = models.CharField(max_length=50)
    current_developer = models.ForeignKey(Developer)
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
    operation_date = models.DateField(null=True, blank=True)
    construction_date = models.DateField(null=True, blank=True)
    turbine_locations = models.MultiPointField(null=True, blank=True)
    turbine_make = models.ForeignKey(TurbineMake, null=True, blank=True)
    turbine_capacity = models.IntegerField(null=True, blank=True)
    turbine_height = models.IntegerField(null=True, blank=True)

    def get_absolute_url(self):
        return reverse('project', kwargs={'pk': self.pk})

    def __str__(self):
        return self.current_name


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


class TaxaOrder(models.Model):
    """Currently this tool just services birds and bats, but more orders might get added in the future."""
    order = models.CharField(max_length=20)  # Saurischia = birds, Laurasiatheria = bats


class Taxa(models.Model):
    """
    Holds a list of all of current names and statuses of the Southern African birds and bats.
    Should get synchronised regularly with a master list. For this reason genus has not been normalised.
    Order determines whether a species is a bird or a bat.
    """
    order = models.ForeignKey(TaxaOrder)
    genus = models.CharField(max_length=20)
    species = models.CharField(max_length=20)
    added = models.DateTimeField(auto_now_add=True)
    red_list_choices = (
        ('EX', 'Extinct'),
        ('EW', 'Extinct in the Wild'),
        ('CR', 'Critically Endangered'),
        ('EN', 'Endangered'),
        ('VU', 'Vulnerable'),
        ('NT', 'Near Threatened'),
        ('LC', 'Least Concern'),
        ('DD', 'Least Concern')
    )
    red_list = models.CharField(max_length=1, choices=red_list_choices)
    sensitive = models.BooleanField(default=False)


class FocalSite(models.Model):
    """
    Focal sites are locations of particular interest in projects.
    Data is collected and stored against each focal site.
    """
    location = models.PolygonField()
    name = models.CharField(max_length=50)
    order = models.ForeignKey(TaxaOrder)
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


class MetaData(models.Model):
    """
    Metadata for the 3 different types of datasets - population data, focal site data, fatality data
    """
    models.ForeignKey(Project)
    objects = models.GeoManager()
    collected_to = models.DateTimeField()
    collected_from = models.DateTimeField()
    flagged_for_query = models.BooleanField(default=False)
    control_data = models.BooleanField(default=False)
    # TODO uploader =


class PopulationData(models.Model):
    """
    Census, focal point & transect data form a population count/estimate
    """
    metadata = models.ForeignKey(MetaData)
    taxa = models.ForeignKey(Taxa)
    count = models.IntegerField()  # Actual number counted / for bats this activity levels

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
    density_km = models.IntegerField()  # Estimate of density per km^2
    passage_rate = models.IntegerField()  # Number passing through area per hour


class FocalSiteData(models.Model):
    """
    Records activity for a particular focal site
    """
    metadata = models.ForeignKey(MetaData)
    taxa = models.ForeignKey(Taxa)
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
    taxa = models.ForeignKey(Taxa)
    coordinate = models.PointField()

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
