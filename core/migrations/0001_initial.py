# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import mptt.fields
import django.contrib.gis.db.models.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Developer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('name', models.CharField(unique=True, max_length=100)),
                ('email', models.CharField(max_length=50)),
                ('phone', models.CharField(max_length=15)),
            ],
        ),
        migrations.CreateModel(
            name='Documents',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=20)),
                ('uploaded', models.DateTimeField(auto_now_add=True)),
                ('document_type', models.CharField(choices=[('E', 'EIA report'), ('O', 'Other')], max_length=1, default='E')),
            ],
        ),
        migrations.CreateModel(
            name='EquipmentMake',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('name', models.CharField(unique=True, max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='FatalityData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('coordinates', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('cause_of_death', models.CharField(max_length=1, choices=[('T', 'Turbine'), ('R', 'Road'), ('S', 'Solar panel'), ('E', 'Power lines (electric)'), ('N', 'Natural'), ('P', 'Predation'), ('U', 'Undetermined')])),
            ],
        ),
        migrations.CreateModel(
            name='FocalSite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('location', django.contrib.gis.db.models.fields.PolygonField(srid=4326)),
                ('name', models.CharField(max_length=50)),
                ('sensitive', models.BooleanField(default=False)),
                ('activity', models.CharField(max_length=1, choices=[('R', 'Roost'), ('C', 'Display/courtship area'), ('F', 'Feeding ground'), ('O', 'Other')])),
                ('habitat', models.CharField(max_length=2, choices=[('BU', 'Building'), ('BR', 'Bridge'), ('CA', 'Cave/ridge or underhanging'), ('CR', 'Rocky crevice'), ('CU', 'Culvert'), ('MI', 'Mine'), ('FT', 'Fruit trees'), ('TR', 'Trees'), ('CA', 'Cave/ridge or underhanging'), ('CL', 'Clearing'), ('SC', 'Grassy/shrubby area'), ('WA', 'Water body (e.g. pond, pool, etc)')])),
            ],
        ),
        migrations.CreateModel(
            name='FocalSiteData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('count', models.IntegerField()),
                ('life_stage', models.CharField(choices=[('C', 'Chick/pup'), ('J', 'Juvenile'), ('A', 'Adult')], max_length=1, default='A')),
                ('activity', models.CharField(max_length=3, choices=[('CDP', 'courtship display'), ('CAN', 'adult bird carrying nesting material'), ('ANB', 'active nest building'), ('NCN', 'newly completed nest'), ('NWE', 'nest with eggs'), ('NWC', 'nest with chicks'), ('PFY', 'parents feeding young in nest'), ('PFS', 'parents with fecal sac'), ('PAY', 'parents and young not in nest')], blank=True, null=True)),
                ('focal_site', models.ForeignKey(to='core.FocalSite')),
            ],
        ),
        migrations.CreateModel(
            name='MetaData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('collected_to', models.DateTimeField()),
                ('collected_from', models.DateTimeField()),
                ('flagged_for_query', models.BooleanField(default=False)),
                ('control_data', models.BooleanField(verbose_name='This is control data', default=False)),
                ('uploaded_on', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='PopulationData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('count', models.IntegerField()),
                ('collision_risk', models.CharField(max_length=1, choices=[('H', 'High risk of collision'), ('M', 'Medium risk of collision'), ('L', 'Low risk of collision')])),
                ('density_km', models.DecimalField(max_digits=10, decimal_places=5)),
                ('passage_rate', models.DecimalField(max_digits=7, decimal_places=2)),
                ('metadata', models.ForeignKey(to='core.MetaData')),
            ],
        ),
        migrations.CreateModel(
            name='PreviousDevelopers',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('stopped', models.DateTimeField(auto_now_add=True)),
                ('developer', models.ForeignKey(to='core.Developer')),
            ],
        ),
        migrations.CreateModel(
            name='PreviousProjectNames',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('previous_name', models.CharField(max_length=50)),
                ('stopped', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('phone', models.CharField(max_length=100)),
                ('type', models.CharField(max_length=2, choices=[('NG', 'NGO employee'), ('AC', 'Academic'), ('EI', 'EIA consultant'), ('PU', 'Member of the public'), ('BA', 'Bat specialist'), ('BI', 'Bird specialist'), ('DE', 'Developer'), ('OT', 'Other')])),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('name', models.CharField(unique=True, max_length=50)),
                ('location', django.contrib.gis.db.models.fields.PolygonField(srid=4326)),
                ('eia_number', models.CharField(max_length=20)),
                ('energy_type', models.CharField(choices=[('W', 'Wind turbine'), ('S', 'Solar panels')], max_length=1, default='W')),
                ('operational_date', models.DateField(blank=True, null=True)),
                ('construction_date', models.DateField(blank=True, null=True)),
                ('turbine_locations', django.contrib.gis.db.models.fields.MultiPointField(blank=True, null=True, srid=4326)),
                ('solar_panel_locations', django.contrib.gis.db.models.fields.PolygonField(blank=True, null=True, srid=4326)),
                ('equipment_capacity', models.IntegerField(blank=True, null=True)),
                ('equipment_height', models.IntegerField(blank=True, null=True)),
                ('developer', models.ForeignKey(to='core.Developer')),
                ('equipment_make', models.ForeignKey(blank=True, to='core.EquipmentMake', null=True)),
            ],
            options={
                'permissions': (('contributor', 'Can contribute data (i.e. upload datasets and create projects)'), ('trusted', 'Can view sensitive data'), ('request_contributor', 'Has requested contributor status'), ('request_trusted', 'Has requested trusted status')),
            },
        ),
        migrations.CreateModel(
            name='RedListStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('red_list', models.CharField(max_length=2, choices=[('EX', 'Extinct'), ('EW', 'Extinct in the Wild'), ('CR', 'Critically Endangered'), ('EN', 'Endangered'), ('VU', 'Vulnerable'), ('NT', 'Near Threatened'), ('LC', 'Least Concern'), ('DD', 'Least Concern')])),
                ('sensitive', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='RemovalFlag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('reason', models.TextField(max_length=2000)),
                ('requested_on', models.DateTimeField(auto_now_add=True)),
                ('metadata', models.ForeignKey(to='core.MetaData')),
                ('requested_by', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Taxon',
            fields=[
                ('name', models.CharField(max_length=50)),
                ('updated', models.DateTimeField(auto_now_add=True)),
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('rank', models.CharField(choices=[('KI', 'Kingdom'), ('PH', 'Phylum'), ('CL', 'Class'), ('OR', 'Order'), ('FA', 'Family'), ('GE', 'Genus'), ('SP', 'Species'), ('SU', 'Subspecies')], max_length=2, default='SP')),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
                ('parent', mptt.fields.TreeForeignKey(blank=True, to='core.Taxon', related_name='children', null=True)),
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
            field=models.ForeignKey(to='core.Taxon'),
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
            field=models.ForeignKey(to='core.Taxon'),
        ),
        migrations.AddField(
            model_name='focalsite',
            name='project',
            field=models.ForeignKey(to='core.Project'),
        ),
        migrations.AddField(
            model_name='focalsite',
            name='taxon',
            field=models.ForeignKey(to='core.Taxon'),
        ),
        migrations.AddField(
            model_name='fatalitydata',
            name='metadata',
            field=models.ForeignKey(to='core.MetaData'),
        ),
        migrations.AddField(
            model_name='fatalitydata',
            name='taxa',
            field=models.ForeignKey(to='core.Taxon'),
        ),
        migrations.AddField(
            model_name='documents',
            name='project',
            field=models.ForeignKey(to='core.Project'),
        ),
    ]
