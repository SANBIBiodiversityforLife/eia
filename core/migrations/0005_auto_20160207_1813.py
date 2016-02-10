# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.postgres.fields.ranges


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20160207_1509'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='fatalitydata',
            name='taxa',
        ),
        migrations.RemoveField(
            model_name='focalsitedata',
            name='taxa',
        ),
        migrations.RemoveField(
            model_name='populationdata',
            name='taxa',
        ),
        migrations.AddField(
            model_name='fatalitydata',
            name='taxon',
            field=models.ForeignKey(help_text='Identify to genus or <br>species, or select Unknown', default=1, to='core.Taxon'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='focalsitedata',
            name='taxon',
            field=models.ForeignKey(help_text='Identify to genus or <br>species, or select Unknown', default=1, to='core.Taxon'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='populationdata',
            name='taxon',
            field=models.ForeignKey(help_text='Identify to genus or <br>species, or select Unknown', default=1, to='core.Taxon'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='populationdata',
            name='abundance',
            field=models.IntegerField(help_text='Count'),
        ),
        migrations.AlterField(
            model_name='populationdata',
            name='abundance_type',
            field=models.CharField(default='R', choices=[('R', 'Relative'), ('A', 'Absolute')], max_length=1, help_text='Abundance<br>type'),
        ),
        migrations.AlterField(
            model_name='populationdata',
            name='flight_height_bounds',
            field=django.contrib.postgres.fields.ranges.IntegerRangeField(help_text='Flight/equipment<br>height range (m)'),
        ),
        migrations.AlterField(
            model_name='populationdata',
            name='observed',
            field=models.DateTimeField(help_text='Date<br>observed'),
        ),
    ]
