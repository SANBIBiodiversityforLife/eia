# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0034_auto_20160113_1017'),
    ]

    operations = [
        migrations.RenameField(
            model_name='fatalitydata',
            old_name='coordinate',
            new_name='coordinates',
        ),
    ]
