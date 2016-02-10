from django.contrib.gis.db import models
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User, Group
from django.utils import formats
from mptt.models import MPTTModel, TreeForeignKey
import re
from django.contrib.postgres.fields import IntegerRangeField

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


class PreviousProjectName(models.Model):
    """
    Renewable energy projects frequently change name. A list of all the previous names needs to be held for search
    purposes.
    """
    previous_name = models.CharField(max_length=50)
    project = models.ForeignKey(Project)
    stopped = models.DateTimeField(auto_now_add=True)


class PreviousDeveloper(models.Model):
    """
    Developers go bust and change projects, so we need to keep historical records of all the developers who worked on
    a particular project.
    """
    developer = models.ForeignKey(Developer)
    project = models.ForeignKey(Project)
    stopped = models.DateTimeField(auto_now_add=True)


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

    # This is used when serializing data so that we don't get a nasty meaningless number as output
    def natural_key(self):
        return self.__str__()

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
    location = models.PolygonField(help_text='The area of the focal site, should be within 30km of the project area or it will not be associated with this project.')
    objects = models.GeoManager()
    name = models.CharField(max_length=50, help_text='A name by which the focal site can be easily identified')
    sensitive = models.BooleanField(default=False, help_text='If the focal site concerns sensitive species and should not be visible to the public, select this.')

    # Perhaps projects don't have to be manually associated with focal sites, can just use GIS?
    # project = models.ManyToManyField(Project, help_text='Project(s) which are associated with this focal site')

    ROOST = 'R'
    COURTSHIP = 'C'
    FEEDING = 'F'
    OTHER = 'O'
    NOT_SPECIFIED = 'N'
    activity_choices = (
        (ROOST, 'Roost'),
        (COURTSHIP, 'Display/courtship area'),
        (FEEDING, 'Feeding ground'),
        (OTHER, 'Other'),
        (NOT_SPECIFIED, 'N')
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
    FRUIT_TREES = 'FT'

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
        (FRUIT_TREES, 'Fruit trees'),
        (TREES, 'Trees'),
        (CAVE, 'Cave/ridge or underhanging'),
        (CLEARING, 'Clearing'),
        (SCRUB, 'Grassy/shrubby area'),
        (WATER, 'Water body (e.g. pond, pool, etc)')
    )
    habitat = models.CharField(max_length=2, choices=habitat_choices)

    def get_absolute_url(self):
        return reverse('focal_site_data', kwargs={'pk': self.project.pk})

    # def clean(self):
        # Coordinate cannot be more than 50km outside the bounds of the project TODO implement this
        # if not self.project.location.contains(self.location):
        #    raise ValidationError({'location': 'Focal sites must be within the project bounds.'})

class MetaData(models.Model):
    """
    Metadata for the 3 different types of datasets - population data, focal site data, fatality data
    """
    project = models.ForeignKey(Project)
    flagged_for_query = models.BooleanField(default=False)
    uploader = models.ForeignKey(User)
    uploaded_on = models.DateTimeField(auto_now_add=True)

    # Following two functions are taken from
    # http://stackoverflow.com/questions/7366363/adding-custom-django-model-validation
    # See also the docs https://docs.djangoproject.com/en/1.8/ref/models/instances/
    #def clean(self):
    #    if self.collected_from >= self.collected_to:
    #        raise ValidationError({'collected_from': 'The collected from date must be earlier than the to date'})
    #    super(MetaData, self).clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        super(MetaData, self).save(*args, **kwargs)

    #def is_post_construction(self):
    #    if self.project.construction_date:
    #        return self.collected_from.date() > self.project.construction_date
    #    else:
    #        # There is no construction date up yet
    #        return False

    def __str__(self):
        """text = 'Collected: ' + formats.date_format(self.collected_from, "DATETIME_FORMAT") + ' - ' + \
               formats.date_format(self.collected_to, "DATETIME_FORMAT")
        if self.is_post_construction():
            text += '(post construction)'
        else:
            text += '(pre construction)'
        text += ' | Uploaded by ' + self.uploader.first_name + ' ' + self.uploader.last_name + ' on ' + \
                formats.date_format(self.uploaded_on, "DATETIME_FORMAT")
        if self.control_data:
            text += ' (control data)'"""
        return 'Uploaded : ' + formats.date_format(self.uploaded_on, "DATETIME_FORMAT") + ' by ' + \
               self.uploader.first_name + ' ' + self.uploader.last_name

    def get_data_object(self):
        # Population data
        models.PopulationData.objects.get(metadata=self)


class RemovalFlag(models.Model):
    """
    Allows users to flag datasets for removal
    """
    metadata = models.ForeignKey(MetaData, help_text='The dataset issued for removal')
    reason = models.TextField(max_length=2000, help_text='Why should this dataset be removed?')
    requested_by = models.ForeignKey(User, help_text='The user who has requested the removal of this dataset')
    requested_on = models.DateTimeField(auto_now_add=True, help_text='When the removal was requested')

    def get_absolute_url(self):
        return reverse('projects_list')


def document_upload_path(instance, filename):
    filename_parts = filename.split('.')
    extension = filename_parts[1]
    cleaned_name = re.sub('\s+', '_', instance.name)
    return '/'.join(['document_uploads', '{0}.{1}'.format(cleaned_name, extension)])


class Document(models.Model):
    """
    Scanned in documents should be uploadable and can be associated with a project and optionally also a metadata
    Note that DEA are collecting EIA reports separately, but until we get the two linked up this can be used to store
    EIA reports as well.
    """
    name = models.CharField(max_length=20, help_text='A short, descriptive name for the document')
    project = models.ForeignKey(Project)
    metadata = models.ForeignKey(MetaData, null=True, blank=True)
    uploaded = models.DateTimeField(auto_now_add=True)
    uploader = models.ForeignKey(User)
    document = models.FileField(upload_to=document_upload_path)

    EIA = 'E'
    OTHER = 'O'
    RAW = 'R'
    DOCUMENT_TYPE_CHOICES = (
        (EIA, 'EIA report'),
        (OTHER, 'Other'),
        (RAW, 'Raw data')
    )
    document_type = models.CharField(max_length=1, choices=DOCUMENT_TYPE_CHOICES, default=EIA)

    def get_table_display(self):
        # Used to display in table format on all the data_list type pages, must be wrapped in table tags
        # Headings: Document, File type, Uploader, Uploaded on, Document type
        return '<tr><td>' \
               '<a href="' + self.document.url + '">' + self.name + '</a></td><td>' + \
               self.document.name.split('.')[1].upper() + '</td><td>' + \
               self.uploader.first_name + ' ' + self.uploader.last_name + '</td><td>' + \
               formats.date_format(self.uploaded, "DATETIME_FORMAT") + '</td><td>' + \
               self.get_document_type_display() + '</td></tr>'

    def __str__(self):
        return '<a href="' + self.document.url + '">' + self.name + '</a> (.' + \
               self.document.name.split('.')[1].upper() + ' Uploaded: ' + self.uploader.first_name + ' ' + \
               self.uploader.last_name + ' on ' + \
               formats.date_format(self.uploaded, "DATETIME_FORMAT") + ' Type: ' + self.get_document_type + ')'


# This help text is used in the models below
taxon_help_text = 'Identify to genus or <br>species, or select Unknown'
observed_help_text = 'Date<br>observed'


class PopulationData(models.Model):
    """
    Census, focal point & transect data form a population count/estimate
    """
    metadata = models.ForeignKey(MetaData)

    taxon_help = taxon_help_text
    taxon = models.ForeignKey(Taxon, help_text=taxon_help)

    observed_help = observed_help_text
    observed = models.DateTimeField(help_text=observed_help)

    abundance_help = 'Count'
    abundance = models.IntegerField(help_text=abundance_help)

    RELATIVE = 'R'
    ABSOLUTE = 'A'
    ABUNDANCE_TYPE_CHOICES = (
        (RELATIVE, 'Relative'),
        (ABSOLUTE, 'Absolute')
    )
    abundance_type_help = 'Abundance<br>type'
    abundance_type = models.CharField(max_length=1, choices=ABUNDANCE_TYPE_CHOICES, default='R', help_text=abundance_type_help)

    flight_height_help = 'Flight/equipment<br>height range (m)'
    flight_height = IntegerRangeField(help_text=flight_height_help)

    def get_flight_height_display(self):
        return str(self.flight_height.lower) + ' - ' + str(self.flight_height.upper) + 'm'

    location = models.PolygonField()
    objects = models.GeoManager()


    # Birds only:
    # density_km = models.DecimalField(max_digits=10, decimal_places=5)  # Estimate of density per km^2
    # passage_rate = models.DecimalField(max_digits=7, decimal_places=2)  # Number passing through area per hour

    def get_absolute_url(self):
        return reverse('project_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return str(self.abundance) + ' ' + self.taxon.name + ' seen on ' + formats.date_format(self.observed, "DATETIME_FORMAT")

    def save(self, *args, **kwargs):
        self.full_clean()
        super(PopulationData, self).save(*args, **kwargs)

    def _get_help_text(self, field_name):
        """Given a field name, return its help text."""
        # Let's iterate over all the fields on this model.
        for field in self._meta.fields:
            # The name of your field is stored as a name attribute on the field object
            if field.name == field:
                # and there's the help_text!
                return field.help_text


class FocalSiteData(models.Model):
    """
    Records activity for a particular focal site
    """
    metadata = models.ForeignKey(MetaData)

    taxon_help = taxon_help_text
    taxon = models.ForeignKey(Taxon, help_text=taxon_help)

    observed_help = observed_help_text
    observed = models.DateTimeField(help_text=observed_help)

    abundance_help = 'Absolute<br>abundance'
    abundance = models.IntegerField(help_text=abundance_help)

    focal_site_help = 'The focal site this dataset was recorded at'
    focal_site = models.ForeignKey(FocalSite, help_text=focal_site_help)

    life_stage_help = 'Life<br>stage'
    LIFE_STAGE_CHOICES = (
        ('C', 'Chick/pup'),
        ('J', 'Juvenile'),
        ('A', 'Adult')
    )
    life_stage = models.CharField(max_length=1, choices=LIFE_STAGE_CHOICES, default='A', help_text=life_stage_help)

    # Only applicable to birds
    activity_choices_help = 'Activity (only <br>applicable to birds)'
    ACTIVITY_CHOICES = (
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
    activity = models.CharField(max_length=3, choices=ACTIVITY_CHOICES, null=True, blank=True,
                                help_text=activity_choices_help)


class FatalityData(models.Model):
    """
    Records fatalities
    """
    metadata = models.ForeignKey(MetaData)

    taxon_help = taxon_help_text
    taxon = models.ForeignKey(Taxon, help_text=taxon_help)

    found_help = 'Date<br>found'
    found = models.DateTimeField(help_text=found_help)

    coordinates = models.PointField(help_text='The latitude and longitude values where the corpse was found')
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
    cause_of_death_help = 'Specify cause of death'
    cause_of_death = models.CharField(max_length=1, choices=cause_of_death_choices, help_text=cause_of_death_help)

    def clean(self):
        # Coordinate cannot be outside the bounds of the project
        if not self.metadata.project.location.contains(self.coordinates):
            raise ValidationError({'coordinates': 'Fatality coordinates are outside the project polygon bounds.'})
