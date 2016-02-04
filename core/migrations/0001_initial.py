# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.gis.db.models.fields
import core.models
import django.contrib.postgres.fields.ranges
from django.conf import settings
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Developer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(unique=True, max_length=100)),
                ('email', models.CharField(max_length=50)),
                ('phone', models.CharField(max_length=15)),
            ],
        ),
        migrations.CreateModel(
            name='Documents',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='A short, descriptive name for the document', max_length=20)),
                ('uploaded', models.DateTimeField(auto_now_add=True)),
                ('document', models.FileField(upload_to=core.models.document_upload_path)),
                ('document_type', models.CharField(default='E', choices=[('E', 'EIA report'), ('O', 'Other')], max_length=1)),
            ],
        ),
        migrations.CreateModel(
            name='EquipmentMake',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(unique=True, max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='FatalityData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('found', models.DateTimeField(help_text='Date found')),
                ('coordinates', django.contrib.gis.db.models.fields.PointField(help_text='The latitude and longitude values where the corpse was found', srid=4326)),
                ('cause_of_death', models.CharField(help_text='Specify cause of death', choices=[('T', 'Turbine'), ('R', 'Road'), ('S', 'Solar panel'), ('E', 'Power lines (electric)'), ('N', 'Natural'), ('P', 'Predation'), ('U', 'Undetermined')], max_length=1)),
            ],
        ),
        migrations.CreateModel(
            name='FocalSite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location', django.contrib.gis.db.models.fields.PolygonField(help_text='The area of the focal site', srid=4326)),
                ('name', models.CharField(help_text='A name by which the focal site can be easily identified', max_length=50)),
                ('sensitive', models.BooleanField(default=False)),
                ('activity', models.CharField(choices=[('R', 'Roost'), ('C', 'Display/courtship area'), ('F', 'Feeding ground'), ('O', 'Other')], max_length=1)),
                ('habitat', models.CharField(choices=[('BU', 'Building'), ('BR', 'Bridge'), ('CA', 'Cave/ridge or underhanging'), ('CR', 'Rocky crevice'), ('CU', 'Culvert'), ('MI', 'Mine'), ('FT', 'Fruit trees'), ('TR', 'Trees'), ('CA', 'Cave/ridge or underhanging'), ('CL', 'Clearing'), ('SC', 'Grassy/shrubby area'), ('WA', 'Water body (e.g. pond, pool, etc)')], max_length=2)),
            ],
        ),
        migrations.CreateModel(
            name='FocalSiteData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('observed', models.DateTimeField(help_text='Date observed')),
                ('count', models.IntegerField(help_text='Number counted')),
                ('life_stage', models.CharField(help_text='Please upload a single record for each individual and specify their life stage', default='A', choices=[('C', 'Chick/pup'), ('J', 'Juvenile'), ('A', 'Adult')], max_length=1)),
                ('activity', models.CharField(help_text='Only applicable for birds', null=True, choices=[('CDP', 'courtship display'), ('CAN', 'adult bird carrying nesting material'), ('ANB', 'active nest building'), ('NCN', 'newly completed nest'), ('NWE', 'nest with eggs'), ('NWC', 'nest with chicks'), ('PFY', 'parents feeding young in nest'), ('PFS', 'parents with fecal sac'), ('PAY', 'parents and young not in nest')], max_length=3, blank=True)),
                ('focal_site', models.ForeignKey(help_text='The focal site this dataset was recorded at', to='core.FocalSite')),
            ],
        ),
        migrations.CreateModel(
            name='MetaData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('flagged_for_query', models.BooleanField(default=False)),
                ('control_data', models.BooleanField(default=False, verbose_name='This is control data')),
                ('uploaded_on', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='PopulationData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('observed', models.DateTimeField(help_text='Date observed')),
                ('count', models.IntegerField(help_text='Number counted, or activity level/number of passes per hour (for bats)')),
                ('flight_height_bounds', django.contrib.postgres.fields.ranges.IntegerRangeField(help_text='Flight height range in metres (equipment height for bats)')),
                ('location', django.contrib.gis.db.models.fields.PolygonField(default=core.models.PopulationData.get_project_location, srid=4326)),
                ('metadata', models.ForeignKey(to='core.MetaData')),
            ],
        ),
        migrations.CreateModel(
            name='PreviousDevelopers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stopped', models.DateTimeField(auto_now_add=True)),
                ('developer', models.ForeignKey(to='core.Developer')),
            ],
        ),
        migrations.CreateModel(
            name='PreviousProjectNames',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('previous_name', models.CharField(max_length=50)),
                ('stopped', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(max_length=100)),
                ('type', models.CharField(choices=[('NG', 'NGO employee'), ('AC', 'Academic'), ('EI', 'EIA consultant'), ('PU', 'Member of the public'), ('BA', 'Bat specialist'), ('BI', 'Bird specialist'), ('DE', 'Developer'), ('OT', 'Other')], max_length=2)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(unique=True, max_length=50)),
                ('location', django.contrib.gis.db.models.fields.PolygonField(srid=4326)),
                ('eia_number', models.CharField(max_length=20)),
                ('energy_type', models.CharField(default='W', choices=[('W', 'Wind turbine'), ('S', 'Solar panels')], max_length=1)),
                ('operational_date', models.DateField(null=True, blank=True)),
                ('construction_date', models.DateField(null=True, blank=True)),
                ('turbine_locations', django.contrib.gis.db.models.fields.MultiPointField(null=True, srid=4326, blank=True)),
                ('solar_panel_locations', django.contrib.gis.db.models.fields.PolygonField(null=True, srid=4326, blank=True)),
                ('equipment_capacity', models.IntegerField(null=True, blank=True)),
                ('equipment_height', models.IntegerField(null=True, blank=True)),
                ('developer', models.ForeignKey(to='core.Developer')),
                ('equipment_make', models.ForeignKey(null=True, to='core.EquipmentMake', blank=True)),
            ],
            options={
                'permissions': (('contributor', 'Can contribute data (i.e. upload datasets and create projects)'), ('trusted', 'Can view sensitive data'), ('request_contributor', 'Has requested contributor status'), ('request_trusted', 'Has requested trusted status')),
            },
        ),
        migrations.CreateModel(
            name='RemovalFlag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.TextField(help_text='Why should this dataset be removed?', max_length=2000)),
                ('requested_on', models.DateTimeField(help_text='When the removal was requested', auto_now_add=True)),
                ('metadata', models.ForeignKey(help_text='The dataset issued for removal', to='core.MetaData')),
                ('requested_by', models.ForeignKey(help_text='The user who has requested the removal of this dataset', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Taxon',
            fields=[
                ('name', models.CharField(max_length=100)),
                ('vernacular_name', models.CharField(null=True, max_length=100, blank=True)),
                ('updated', models.DateTimeField(auto_now_add=True)),
                ('is_root', models.BooleanField(default=False)),
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('rank', models.CharField(default='SP', choices=[('KI', 'Kingdom'), ('PH', 'Phylum'), ('CL', 'Class'), ('OR', 'Order'), ('FA', 'Family'), ('GE', 'Genus'), ('IN', 'Infraspecific name'), ('SP', 'Species'), ('SU', 'Subspecies')], max_length=2)),
                ('red_list', models.CharField(default='LC', choices=[('EX', 'Extinct'), ('EW', 'Extinct in the Wild'), ('CR', 'Critically Endangered'), ('EN', 'Endangered'), ('VU', 'Vulnerable'), ('NT', 'Near Threatened'), ('LC', 'Least Concern'), ('DD', 'Data Deficient')], max_length=2)),
                ('sensitive', models.BooleanField(default=False)),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('parent', mptt.fields.TreeForeignKey(related_name='children', null=True, to='core.Taxon', blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='previousprojectnames',
            name='project',
            field=models.ForeignKey(to='core.Project'),
        ),
        migrations.AddField(
            model_name='previousdevelopers',
            name='project',
            field=models.ForeignKey(to='core.Project'),
        ),
        migrations.AddField(
            model_name='populationdata',
            name='taxa',
            field=models.ForeignKey(help_text='Identify to genus or species level, or select Unknown', to='core.Taxon'),
        ),
        migrations.AddField(
            model_name='metadata',
            name='project',
            field=models.ForeignKey(to='core.Project'),
        ),
        migrations.AddField(
            model_name='metadata',
            name='uploader',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='focalsitedata',
            name='metadata',
            field=models.ForeignKey(to='core.MetaData'),
        ),
        migrations.AddField(
            model_name='focalsitedata',
            name='taxa',
            field=models.ForeignKey(help_text='Identify to genus or species level, or select Unknown', to='core.Taxon'),
        ),
        migrations.AddField(
            model_name='fatalitydata',
            name='metadata',
            field=models.ForeignKey(to='core.MetaData'),
        ),
        migrations.AddField(
            model_name='fatalitydata',
            name='taxa',
            field=models.ForeignKey(help_text='Identify to genus or species level, or select Unknown', to='core.Taxon'),
        ),
        migrations.AddField(
            model_name='documents',
            name='project',
            field=models.ForeignKey(to='core.Project'),
        ),
        migrations.AddField(
            model_name='documents',
            name='uploader',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]
