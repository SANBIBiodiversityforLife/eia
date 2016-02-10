# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20160207_1813'),
    ]

    operations = [
        migrations.RenameField(
            model_name='populationdata',
            old_name='flight_height_bounds',
            new_name='flight_height',
        ),
    ]
