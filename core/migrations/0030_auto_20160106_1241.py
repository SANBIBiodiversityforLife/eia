# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0029_auto_20160106_0904'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='project',
            options={'permissions': (('contributor', 'Can contribute data (i.e. upload datasets and create projects)'), ('trusted', 'Can view sensitive data'), ('request_contributor', 'Has requested contributor status'), ('request_trusted', 'Has requested trusted status'))},
        ),
    ]
