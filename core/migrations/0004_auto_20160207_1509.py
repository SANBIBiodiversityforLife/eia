# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20160205_1051'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='metadata',
            name='control_data',
        ),
        migrations.AddField(
            model_name='populationdata',
            name='abundance_type',
            field=models.CharField(max_length=1, default='R', choices=[('R', 'Relative'), ('A', 'Absolute')]),
        ),
        migrations.AddField(
            model_name='populationdata',
            name='observed',
            field=models.DateTimeField(default=datetime.datetime(2016, 2, 7, 13, 9, 25, 671493, tzinfo=utc), help_text='Date observed'),
            preserve_default=False,
        ),
    ]
