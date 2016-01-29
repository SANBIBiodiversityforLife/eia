# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_taxon_vernacular_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taxon',
            name='name',
            field=models.CharField(max_length=100),
        ),
    ]
