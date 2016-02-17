# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20160208_1552'),
    ]

    operations = [
        migrations.CreateModel(
            name='FatalityRate',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('rate', models.DecimalField(max_digits=8, decimal_places=5)),
                ('rate_type', models.CharField(max_length=2, choices=[('SC', 'Scavenger removal rate'), ('SE', 'Searcher efficiency rate'), ('FA', 'Calculated fatality rate (per year)')])),
                ('radius', models.IntegerField()),
                ('shape', models.CharField(max_length=1, choices=[('S', 'Square'), ('C', 'Circle'), ('N', 'Not applicable')])),
                ('metadata', models.ForeignKey(to='core.MetaData')),
                ('taxon', models.ForeignKey(to='core.Taxon', help_text='Choose the highest level applicable - e.g. families for small birds, or chiroptera for bats')),
            ],
        ),
        migrations.AlterField(
            model_name='fatalitydata',
            name='found',
            field=models.DateTimeField(help_text='Date<br>found'),
        ),
        migrations.AlterField(
            model_name='focalsite',
            name='activity',
            field=models.CharField(max_length=1, choices=[('R', 'Roost'), ('C', 'Display/courtship area'), ('F', 'Feeding ground'), ('O', 'Other'), ('N', 'N')]),
        ),
        migrations.AlterField(
            model_name='focalsite',
            name='location',
            field=django.contrib.gis.db.models.fields.PolygonField(srid=4326, help_text='The area of the focal site, should be within 30km of the project area or it will not be associated with this project.'),
        ),
        migrations.AlterField(
            model_name='focalsitedata',
            name='abundance',
            field=models.IntegerField(help_text='Absolute<br>abundance'),
        ),
        migrations.AlterField(
            model_name='focalsitedata',
            name='life_stage',
            field=models.CharField(default='A', help_text='Life<br>stage', max_length=1, choices=[('C', 'Chick/pup'), ('J', 'Juvenile'), ('A', 'Adult')]),
        ),
        migrations.AlterField(
            model_name='project',
            name='construction_date',
            field=models.DateField(blank=True, help_text='The day on which construction starts', null=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='developer',
            field=models.ForeignKey(to='core.Developer', help_text='The company doing the development work on the project'),
        ),
        migrations.AlterField(
            model_name='project',
            name='eia_number',
            field=models.CharField(help_text='The official number provided by DEA', max_length=20),
        ),
        migrations.AlterField(
            model_name='project',
            name='energy_type',
            field=models.CharField(default='W', help_text='The type of renewable energy', max_length=1, choices=[('W', 'Wind turbine'), ('S', 'Solar panels')]),
        ),
        migrations.AlterField(
            model_name='project',
            name='equipment_make',
            field=models.ForeignKey(help_text='The make and brand of the equipment', to='core.EquipmentMake', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='location',
            field=django.contrib.gis.db.models.fields.PolygonField(srid=4326, help_text='<a href="#" onClick="startIntro()"  data-toggle="tooltip" data-placement="right" title="Click to learn how to use our maps">Learn how to use the map. You can load a KML or GPX, or draw a shape manually          <span class="glyphicon glyphicon-question-sign" aria-hidden="true"></span></a>.'),
        ),
        migrations.AlterField(
            model_name='project',
            name='name',
            field=models.CharField(unique=True, help_text='The official name of the project', max_length=50),
        ),
        migrations.AlterField(
            model_name='project',
            name='operational_date',
            field=models.DateField(blank=True, help_text='The day on which building is complete (e.g. the turbines are revolving)', null=True),
        ),
    ]
