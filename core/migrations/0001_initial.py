# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Developer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.CharField(max_length=50)),
                ('phone', models.CharField(max_length=15)),
            ],
        ),
        migrations.CreateModel(
            name='Documents',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('uploaded', models.DateTimeField(auto_now_add=True)),
                ('document_type', models.CharField(max_length=1, default='E', choices=[('E', 'EIA report'), ('O', 'Other')])),
            ],
        ),
        migrations.CreateModel(
            name='FatalityData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('coordinate', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('cause_of_death', models.CharField(max_length=1, choices=[('T', 'Turbine'), ('R', 'Road'), ('S', 'Solar panel'), ('E', 'Power lines (electric)'), ('N', 'Natural'), ('P', 'Predation'), ('U', 'Undetermined')])),
            ],
        ),
        migrations.CreateModel(
            name='FocalSite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
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
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count', models.IntegerField()),
                ('life_stage', models.CharField(max_length=1, default='A', choices=[('C', 'Chick/pup'), ('J', 'Juvenile'), ('A', 'Adult')])),
                ('activity', models.CharField(max_length=3, null=True, blank=True, choices=[('CDP', 'courtship display'), ('CAN', 'adult bird carrying nesting material'), ('ANB', 'active nest building'), ('NCN', 'newly completed nest'), ('NWE', 'nest with eggs'), ('NWC', 'nest with chicks'), ('PFY', 'parents feeding young in nest'), ('PFS', 'parents with fecal sac'), ('PAY', 'parents and young not in nest')])),
                ('focal_site', models.ForeignKey(to='core.FocalSite')),
            ],
        ),
        migrations.CreateModel(
            name='MetaData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('collected_to', models.DateTimeField()),
                ('collected_from', models.DateTimeField()),
                ('flagged_for_query', models.BooleanField(default=False)),
                ('control_data', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='PopulationData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count', models.IntegerField()),
                ('collision_risk', models.CharField(max_length=1, choices=[('H', 'High risk of collision'), ('M', 'Medium risk of collision'), ('L', 'Low risk of collision')])),
                ('density_km', models.IntegerField()),
                ('passage_rate', models.IntegerField()),
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
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('current_name', models.CharField(max_length=50)),
                ('location', django.contrib.gis.db.models.fields.PolygonField(srid=4326)),
                ('eia_number', models.CharField(max_length=20)),
                ('energy_type', models.CharField(max_length=1, default='W', choices=[('W', 'Wind turbine'), ('S', 'Solar panels')])),
                ('operation_date', models.DateField(null=True, blank=True)),
                ('construction_date', models.DateField(null=True, blank=True)),
                ('turbine_locations', django.contrib.gis.db.models.fields.MultiPointField(null=True, blank=True, srid=4326)),
                ('turbine_capacity', models.IntegerField(null=True, blank=True)),
                ('turbine_height', models.IntegerField(null=True, blank=True)),
                ('current_developer', models.ForeignKey(to='core.Developer')),
            ],
        ),
        migrations.CreateModel(
            name='Taxa',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('genus', models.CharField(max_length=20)),
                ('species', models.CharField(max_length=20)),
                ('added', models.DateTimeField(auto_now_add=True)),
                ('red_list', models.CharField(max_length=1, choices=[('EX', 'Extinct'), ('EW', 'Extinct in the Wild'), ('CR', 'Critically Endangered'), ('EN', 'Endangered'), ('VU', 'Vulnerable'), ('NT', 'Near Threatened'), ('LC', 'Least Concern'), ('DD', 'Least Concern')])),
                ('sensitive', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='TaxaOrder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='TurbineMake',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('make', models.CharField(max_length=50)),
            ],
        ),
        migrations.AddField(
            model_name='taxa',
            name='order',
            field=models.ForeignKey(to='core.TaxaOrder'),
        ),
        migrations.AddField(
            model_name='project',
            name='turbine_make',
            field=models.ForeignKey(null=True, blank=True, to='core.TurbineMake'),
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
            field=models.ForeignKey(to='core.Taxa'),
        ),
        migrations.AddField(
            model_name='focalsitedata',
            name='metadata',
            field=models.ForeignKey(to='core.MetaData'),
        ),
        migrations.AddField(
            model_name='focalsitedata',
            name='taxa',
            field=models.ForeignKey(to='core.Taxa'),
        ),
        migrations.AddField(
            model_name='focalsite',
            name='order',
            field=models.ForeignKey(to='core.TaxaOrder'),
        ),
        migrations.AddField(
            model_name='focalsite',
            name='project',
            field=models.ForeignKey(to='core.Project'),
        ),
        migrations.AddField(
            model_name='fatalitydata',
            name='metadata',
            field=models.ForeignKey(to='core.MetaData'),
        ),
        migrations.AddField(
            model_name='fatalitydata',
            name='taxa',
            field=models.ForeignKey(to='core.Taxa'),
        ),
        migrations.AddField(
            model_name='documents',
            name='project',
            field=models.ForeignKey(to='core.Project'),
        ),
    ]
