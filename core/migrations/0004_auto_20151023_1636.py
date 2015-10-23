# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20151023_0923'),
    ]

    operations = [
        migrations.CreateModel(
            name='FocalSiteData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('count', models.IntegerField()),
                ('life_stage', models.CharField(max_length=1, default='A', choices=[('C', 'Chick/pup'), ('J', 'Juvenile'), ('A', 'Adult')])),
                ('activity', models.CharField(max_length=3, blank=True, null=True, choices=[('CDP', 'courtship display'), ('CAN', 'adult bird carrying nesting material'), ('ANB', 'active nest building'), ('NCN', 'newly completed nest'), ('NWE', 'nest with eggs'), ('NWC', 'nest with chicks'), ('PFY', 'parents feeding young in nest'), ('PFS', 'parents with fecal sac'), ('PAY', 'parents and young not in nest')])),
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
                ('control_data', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='PopulationData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('count', models.IntegerField()),
                ('collision_risk', models.CharField(max_length=1, choices=[('H', 'High risk of collision'), ('M', 'Medium risk of collision'), ('L', 'Low risk of collision')])),
                ('density_km', models.IntegerField()),
                ('passage_rate', models.IntegerField()),
                ('metadata', models.ForeignKey(to='core.MetaData')),
            ],
        ),
        migrations.RemoveField(
            model_name='batfocalsitedata',
            name='dataset',
        ),
        migrations.RemoveField(
            model_name='batfocalsitedata',
            name='focal_site',
        ),
        migrations.RemoveField(
            model_name='batfocalsitedata',
            name='taxa',
        ),
        migrations.RemoveField(
            model_name='batpopulationdata',
            name='dataset',
        ),
        migrations.RemoveField(
            model_name='batpopulationdata',
            name='taxa',
        ),
        migrations.RemoveField(
            model_name='birdfocalsitedata',
            name='dataset',
        ),
        migrations.RemoveField(
            model_name='birdfocalsitedata',
            name='focal_site',
        ),
        migrations.RemoveField(
            model_name='birdfocalsitedata',
            name='taxa',
        ),
        migrations.RemoveField(
            model_name='birdpopulationdata',
            name='dataset',
        ),
        migrations.RemoveField(
            model_name='birdpopulationdata',
            name='taxa',
        ),
        migrations.RemoveField(
            model_name='fatalitydata',
            name='dataset',
        ),
        migrations.AddField(
            model_name='taxa',
            name='red_list',
            field=models.CharField(max_length=1, default=1, choices=[('EX', 'Extinct'), ('EW', 'Extinct in the Wild'), ('CR', 'Critically Endangered'), ('EN', 'Endangered'), ('VU', 'Vulnerable'), ('NT', 'Near Threatened'), ('LC', 'Least Concern'), ('DD', 'Least Concern')]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='taxa',
            name='sensitive',
            field=models.BooleanField(default=False),
        ),
        migrations.DeleteModel(
            name='BatFocalSiteData',
        ),
        migrations.DeleteModel(
            name='BatPopulationData',
        ),
        migrations.DeleteModel(
            name='BirdFocalSiteData',
        ),
        migrations.DeleteModel(
            name='BirdPopulationData',
        ),
        migrations.DeleteModel(
            name='DataSet',
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
            model_name='fatalitydata',
            name='metadata',
            field=models.ForeignKey(to='core.MetaData', default=1),
            preserve_default=False,
        ),
    ]
