# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_auto_20160216_1117'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='fatalityrate',
            name='taxon',
        ),
        migrations.AddField(
            model_name='fatalityrate',
            name='taxon',
            field=models.ManyToManyField(to='core.Taxon', help_text='Choose small, medium or large bird families, or Chiroptera for bats'),
        ),
    ]
