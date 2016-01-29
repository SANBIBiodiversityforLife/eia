# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20160122_1052'),
    ]

    operations = [
        migrations.AddField(
            model_name='taxon',
            name='vernacular_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
