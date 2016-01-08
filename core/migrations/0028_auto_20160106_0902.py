# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0027_auto_20160106_0902'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='request_contributor_status',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='request_specialist_status',
        ),
    ]
