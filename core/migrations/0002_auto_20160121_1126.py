# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taxon',
            name='rank',
            field=models.CharField(choices=[('KI', 'Kingdom'), ('PH', 'Phylum'), ('CL', 'Class'), ('OR', 'Order'), ('FA', 'Family'), ('GE', 'Genus'), ('IN', 'Infraspecific name'), ('SP', 'Species'), ('SU', 'Subspecies')], default='SP', max_length=2),
        ),
    ]
