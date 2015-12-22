# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0023_auto_20151217_1536'),
    ]

    operations = [
        migrations.AddField(
            model_name='metadata',
            name='uploaded_on',
            field=models.DateTimeField(default=datetime.datetime(2015, 12, 22, 13, 8, 1, 688616, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
    ]
