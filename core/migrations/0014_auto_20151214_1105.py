# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_auto_20151210_0909'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='turbinemake',
            name='make',
        ),
        migrations.AddField(
            model_name='turbinemake',
            name='name',
            field=models.CharField(max_length=50, default='Test', unique=True),
            preserve_default=False,
        ),
    ]
