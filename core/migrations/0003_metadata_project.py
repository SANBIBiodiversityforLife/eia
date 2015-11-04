# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20151028_1611'),
    ]

    operations = [
        migrations.AddField(
            model_name='metadata',
            name='project',
            field=models.ForeignKey(to='core.Project', default=1),
            preserve_default=False,
        ),
    ]
