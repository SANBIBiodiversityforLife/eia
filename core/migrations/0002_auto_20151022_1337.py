# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='turbinedetails',
            name='project',
        ),
        migrations.AddField(
            model_name='project',
            name='turbine_details',
            field=models.ForeignKey(blank=True, to='core.TurbineDetails', null=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='construction_date',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='operation_date',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='turbine_locations',
            field=django.contrib.gis.db.models.fields.MultiPointField(null=True, srid=4326, blank=True),
        ),
    ]
