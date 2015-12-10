# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_auto_20151209_1432'),
    ]

    operations = [
        migrations.RenameField(
            model_name='project',
            old_name='operation_date',
            new_name='operational_date',
        ),
    ]
