# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20160207_1915'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='document_type',
            field=models.CharField(max_length=1, default='E', choices=[('E', 'EIA report'), ('O', 'Other'), ('R', 'Raw data')]),
        ),
    ]
