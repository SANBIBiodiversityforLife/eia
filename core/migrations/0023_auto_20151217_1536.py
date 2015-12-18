# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0022_metadata_uploader'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='TurbineMake',
            new_name='EquipmentMake',
        ),
        migrations.RenameField(
            model_name='project',
            old_name='turbine_capacity',
            new_name='equipment_capacity',
        ),
        migrations.RenameField(
            model_name='project',
            old_name='turbine_height',
            new_name='equipment_height',
        ),
        migrations.RenameField(
            model_name='project',
            old_name='turbine_make',
            new_name='equipment_make',
        ),
        migrations.AddField(
            model_name='project',
            name='solar_panel_locations',
            field=django.contrib.gis.db.models.fields.PolygonField(blank=True, srid=4326, null=True),
        ),
    ]
