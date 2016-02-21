# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-21 14:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_auto_20160221_1413'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='equipment_capacity',
        ),
        migrations.RemoveField(
            model_name='project',
            name='solar_locations',
        ),
        migrations.AddField(
            model_name='project',
            name='capacity',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Nameplate capacity of the project', max_digits=6, null=True),
        ),
    ]
