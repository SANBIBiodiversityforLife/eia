# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_auto_20160217_1007'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='equipment_capacity',
            field=models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=6),
        ),
        migrations.AlterField(
            model_name='project',
            name='equipment_height',
            field=models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=6),
        ),
    ]
