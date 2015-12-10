# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_auto_20151207_1407'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='surname',
            new_name='last_name',
        ),
    ]
