# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_auto_20151207_1526'),
    ]

    operations = [
        migrations.RenameField(
            model_name='project',
            old_name='current_developer',
            new_name='developer',
        ),
        migrations.RenameField(
            model_name='project',
            old_name='current_name',
            new_name='name',
        ),
    ]
