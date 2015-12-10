# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import core.multiple_select_field


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20151207_1044'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='type',
            field=core.multiple_select_field.MultipleSelectField(blank=True, max_length=2, null=True, choices=[('NG', 'NGO employee'), ('AC', 'Academic'), ('EI', 'EIA consultant'), ('PU', 'Member of the public'), ('BA', 'Bat specialist'), ('BI', 'Bird specialist'), ('DE', 'Developer'), ('OT', 'Other')]),
        ),
    ]
