# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0025_removalflag'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='project',
            options={'permissions': (('contributor', 'Can contribute data (i.e. upload datasets and create projects)'), ('specialist', 'Can view sensitive data'))},
        ),
    ]
