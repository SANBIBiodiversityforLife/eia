# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_metadata_project'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='taxa',
            unique_together=set([('genus', 'species')]),
        ),
    ]
