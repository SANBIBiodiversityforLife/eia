# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_auto_20151215_1100'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='turbine_locations',
            field=django.contrib.gis.db.models.fields.MultiPointField(blank=True, srid=4326, null=True),
        ),
    ]
