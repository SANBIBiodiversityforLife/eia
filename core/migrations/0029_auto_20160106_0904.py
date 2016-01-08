# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0028_auto_20160106_0902'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='project',
            options={'permissions': (('contributor', 'Can contribute data (i.e. upload datasets and create projects)'), ('trusted', 'Can view sensitive data'))},
        ),
    ]
