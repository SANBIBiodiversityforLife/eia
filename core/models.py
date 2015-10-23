from django.contrib.gis.db import models
from django.core.urlresolvers import reverse


class Developer(models.Model):
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)

    def __str__(self):
        return self.name


class TurbineMake(models.Model):
    make = models.CharField(max_length=50)

    def __str__(self):
        return self.make

class Project(models.Model):
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
    previous_name = models.CharField(max_length=50)
    project = models.ForeignKey(Project)
    stopped = models.DateTimeField(auto_now_add=True)


class PreviousDevelopers(models.Model):
    developer = models.ForeignKey(Developer)
    project = models.ForeignKey(Project)
    stopped = models.DateTimeField(auto_now_add=True)


class Documents(models.Model):
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
    order = models.CharField(max_length=20)  # Saurischia = birds, Laurasiatheria = bats


class Taxa(models.Model):
    '''
    ' Holds a list of all of current names and statuses of the Southern African birds and bats
    ' Should get synchronised regularly with a master list. For this reason genus has not been normalised
    ' Order determines whether a species is a bird or a bat
    '''
    order = models.ForeignKey(TaxaOrder)
    genus = models.CharField(max_length=20)
    species = models.CharField(max_length=20)
    added = models.DateTimeField(auto_now_add=True)


class DataSet(models.Model):
    models.ForeignKey(Project)
    objects = models.GeoManager()
    collected_to = models.DateTimeField()
    collected_from = models.DateTimeField()
    flagged_for_query = models.BooleanField(default=False)
    # TODO uploader =

    PRE_CONSTRUCTION = 'PRE'
    DURING_CONSTRUCTION = 'DUR'
    POST_CONSTRUCTION = 'POS'
    project_status_choices = (
        (PRE_CONSTRUCTION, 'Pre-construction data'),
        (DURING_CONSTRUCTION, 'During-construction data'),
        (POST_CONSTRUCTION, 'Post-construction data')
    )
    project_status = models.CharField(max_length=1, choices=project_status_choices)

    population_data = models.ForeignKey(PopulationData, null=True, blank=True)
    focal_site_data = models.ForeignKey(FocalSiteData, null=True, blank=True)
    fatality_data = models.ForeignKey(FatalityData, null=True, blank=True)


class PopulationData(models.Model):
    dataset = models.ForeignKey(DataSet)
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


class FocalSite(models.Model):
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


class FocalSiteData(models.Model):
    dataset = models.ForeignKey(DataSet)
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
    dataset = models.ForeignKey(DataSet)
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
