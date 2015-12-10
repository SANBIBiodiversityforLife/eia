# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_profile_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='profile_type_choices',
        ),
        migrations.AlterField(
            model_name='profile',
            name='type',
            field=models.CharField(choices=[('NG', 'NGO employee'), ('AC', 'Academic'), ('EI', 'EIA consultant'), ('PU', 'Member of the public'), ('BA', 'Bat specialist'), ('BI', 'Bird specialist'), ('DE', 'Developer'), ('OT', 'Other')], default='NG', max_length=2),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='ProfileTypeChoices',
        ),
    ]
