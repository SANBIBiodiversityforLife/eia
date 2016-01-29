# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20160121_1126'),
    ]

    operations = [
        migrations.DeleteModel(
            name='RedListStatus',
        ),
        migrations.AddField(
            model_name='taxon',
            name='is_root',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='taxon',
            name='red_list',
            field=models.CharField(max_length=2, choices=[('EX', 'Extinct'), ('EW', 'Extinct in the Wild'), ('CR', 'Critically Endangered'), ('EN', 'Endangered'), ('VU', 'Vulnerable'), ('NT', 'Near Threatened'), ('LC', 'Least Concern'), ('DD', 'Data Deficient')], default='LC'),
        ),
        migrations.AddField(
            model_name='taxon',
            name='sensitive',
            field=models.BooleanField(default=False),
        ),
    ]
