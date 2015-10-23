# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BatFocalSiteData',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('count', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='BatPopulationData',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('activity_levels', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='BirdFocalSiteData',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('chick_count', models.IntegerField()),
                ('juvenile_count', models.IntegerField()),
                ('adult_count', models.IntegerField()),
                ('activity', models.CharField(choices=[('CDP', 'courtship display'), ('CAN', 'adult bird carrying nesting material'), ('ANB', 'active nest building'), ('NCN', 'newly completed nest'), ('NWE', 'nest with eggs'), ('NWC', 'nest with chicks'), ('PFY', 'parents feeding young in nest'), ('PFS', 'parents with fecal sac'), ('PAY', 'parents and young not in nest')], max_length=3)),
            ],
        ),
        migrations.CreateModel(
            name='BirdPopulationData',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('count', models.IntegerField()),
                ('density_km', models.IntegerField()),
                ('passage_rate', models.IntegerField()),
                ('collision_risk', models.CharField(choices=[('H', 'High risk of collision'), ('M', 'Medium risk of collision'), ('L', 'Low risk of collision')], max_length=1)),
            ],
        ),
        migrations.CreateModel(
            name='DataSet',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('collected_to', models.DateTimeField()),
                ('collected_from', models.DateTimeField()),
                ('flagged_for_query', models.BooleanField(default=False)),
                ('project_status', models.CharField(choices=[('PRE', 'Pre-construction data'), ('DUR', 'During-construction data'), ('POS', 'Post-construction data')], max_length=1)),
                ('data_type', models.CharField(choices=[('BIRDPOP', 'Bird population density estimate (Population indicator)'), ('BATPOP', 'Bat activity levels (Population indicator)')], max_length=1)),
            ],
        ),
        migrations.CreateModel(
            name='Developer',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(max_length=100)),
                ('email', models.CharField(max_length=50)),
                ('phone', models.CharField(max_length=15)),
            ],
        ),
        migrations.CreateModel(
            name='Documents',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(max_length=20)),
                ('uploaded', models.DateTimeField(auto_now_add=True)),
                ('document_type', models.CharField(choices=[('E', 'EIA report'), ('O', 'Other')], max_length=1, default='E')),
            ],
        ),
        migrations.CreateModel(
            name='FatalityData',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('coordinate', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('cause_of_death', models.CharField(choices=[('T', 'Turbine'), ('R', 'Road'), ('S', 'Solar panel'), ('E', 'Power lines (electric)'), ('N', 'Natural'), ('P', 'Predation'), ('U', 'Undetermined')], max_length=1)),
                ('dataset', models.ForeignKey(to='core.DataSet')),
            ],
        ),
        migrations.CreateModel(
            name='FocalSite',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('location', django.contrib.gis.db.models.fields.PolygonField(srid=4326)),
                ('name', models.CharField(max_length=50)),
                ('sensitive', models.BooleanField(default=False)),
                ('activity', models.CharField(choices=[('R', 'Roost'), ('C', 'Display/courtship area'), ('F', 'Feeding ground'), ('O', 'Other')], max_length=1)),
                ('habitat', models.CharField(choices=[('BU', 'Building'), ('BR', 'Bridge'), ('CA', 'Cave/ridge or underhanging'), ('CR', 'Rocky crevice'), ('CU', 'Culvert'), ('MI', 'Mine'), ('FT', 'Fruit trees'), ('TR', 'Trees'), ('CA', 'Cave/ridge or underhanging'), ('CL', 'Clearing'), ('SC', 'Grassy/shrubby area'), ('WA', 'Water body (e.g. pond, pool, etc)')], max_length=2)),
            ],
        ),
        migrations.CreateModel(
            name='PreviousDevelopers',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('stopped', models.DateTimeField(auto_now_add=True)),
                ('developer', models.ForeignKey(to='core.Developer')),
            ],
        ),
        migrations.CreateModel(
            name='PreviousProjectNames',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('previous_name', models.CharField(max_length=50)),
                ('stopped', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('current_name', models.CharField(max_length=50)),
                ('location', django.contrib.gis.db.models.fields.PolygonField(srid=4326)),
                ('eia_number', models.CharField(max_length=20)),
                ('energy_type', models.CharField(choices=[('W', 'Wind turbine'), ('S', 'Solar panels')], max_length=1, default='W')),
                ('operation_date', models.DateField()),
                ('construction_date', models.DateField()),
                ('turbine_locations', django.contrib.gis.db.models.fields.MultiPointField(srid=4326)),
                ('current_developer', models.ForeignKey(to='core.Developer')),
            ],
        ),
        migrations.CreateModel(
            name='Taxa',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('genus', models.CharField(max_length=20)),
                ('species', models.CharField(max_length=20)),
                ('added', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='TaxaOrder',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('order', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='TurbineDetails',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('height', models.IntegerField()),
                ('capacity', models.IntegerField()),
                ('project', models.ForeignKey(to='core.Project')),
            ],
        ),
        migrations.AddField(
            model_name='taxa',
            name='order',
            field=models.ForeignKey(to='core.TaxaOrder'),
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
            name='taxa',
            field=models.ForeignKey(to='core.Taxa'),
        ),
        migrations.AddField(
            model_name='documents',
            name='project',
            field=models.ForeignKey(to='core.Project'),
        ),
        migrations.AddField(
            model_name='birdpopulationdata',
            name='dataset',
            field=models.ForeignKey(to='core.DataSet'),
        ),
        migrations.AddField(
            model_name='birdpopulationdata',
            name='taxa',
            field=models.ForeignKey(to='core.Taxa'),
        ),
        migrations.AddField(
            model_name='birdfocalsitedata',
            name='dataset',
            field=models.ForeignKey(to='core.DataSet'),
        ),
        migrations.AddField(
            model_name='birdfocalsitedata',
            name='focal_site',
            field=models.ForeignKey(to='core.FocalSite'),
        ),
        migrations.AddField(
            model_name='birdfocalsitedata',
            name='taxa',
            field=models.ForeignKey(to='core.Taxa'),
        ),
        migrations.AddField(
            model_name='batpopulationdata',
            name='dataset',
            field=models.ForeignKey(to='core.DataSet'),
        ),
        migrations.AddField(
            model_name='batpopulationdata',
            name='taxa',
            field=models.ForeignKey(to='core.Taxa'),
        ),
        migrations.AddField(
            model_name='batfocalsitedata',
            name='dataset',
            field=models.ForeignKey(to='core.DataSet'),
        ),
        migrations.AddField(
            model_name='batfocalsitedata',
            name='focal_site',
            field=models.ForeignKey(to='core.FocalSite'),
        ),
        migrations.AddField(
            model_name='batfocalsitedata',
            name='taxa',
            field=models.ForeignKey(to='core.Taxa'),
        ),
    ]
