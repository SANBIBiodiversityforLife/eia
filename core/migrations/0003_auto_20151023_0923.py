# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20151022_1337'),
    ]

    operations = [
        migrations.CreateModel(
            name='TurbineMake',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('make', models.CharField(max_length=50)),
            ],
        ),
        migrations.RemoveField(
            model_name='project',
            name='turbine_details',
        ),
        migrations.AddField(
            model_name='project',
            name='turbine_capacity',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='project',
            name='turbine_height',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.DeleteModel(
            name='TurbineDetails',
        ),
        migrations.AddField(
            model_name='project',
            name='turbine_make',
            field=models.ForeignKey(null=True, blank=True, to='core.TurbineMake'),
        ),
    ]
