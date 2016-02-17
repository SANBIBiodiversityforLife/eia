# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_auto_20160216_1245'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='fatalityrate',
            name='radius',
        ),
        migrations.RemoveField(
            model_name='fatalityrate',
            name='shape',
        ),
        migrations.AlterField(
            model_name='fatalityrate',
            name='end_date',
            field=models.DateField(help_text='Select the end of the period this estimate/rate is for (should be seasonal or yearly, in special cases can be month-by-month)'),
        ),
        migrations.AlterField(
            model_name='fatalityrate',
            name='rate',
            field=models.DecimalField(max_digits=8, help_text='Enter your calculated rate, can be to 5 decimal places.', decimal_places=5),
        ),
        migrations.AlterField(
            model_name='fatalityrate',
            name='start_date',
            field=models.DateField(help_text='Select the start of the period this estimate/rate is for (should be seasonal or yearly, in special cases can be month-by-month)'),
        ),
    ]
