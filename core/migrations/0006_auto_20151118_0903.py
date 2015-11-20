# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20151102_1500'),
    ]

    operations = [
        migrations.AlterField(
            model_name='metadata',
            name='control_data',
            field=models.BooleanField(default=False, verbose_name='This is control data'),
        ),
        migrations.AlterUniqueTogether(
            name='metadata',
            unique_together=set([('collected_to', 'collected_from', 'control_data')]),
        ),
    ]
