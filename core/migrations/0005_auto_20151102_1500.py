# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20151029_1546'),
    ]

    operations = [
        migrations.RenameField(
            model_name='taxa',
            old_name='added',
            new_name='updated',
        ),
        migrations.AddField(
            model_name='taxa',
            name='family',
            field=models.CharField(max_length=20, default='hello'),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='taxa',
            unique_together=set([('family', 'genus', 'species')]),
        ),
    ]
