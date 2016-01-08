# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0026_auto_20160105_0933'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='request_contributor_status',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='profile',
            name='request_specialist_status',
            field=models.BooleanField(default=False),
        ),
    ]
