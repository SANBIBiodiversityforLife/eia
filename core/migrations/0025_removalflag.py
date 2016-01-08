# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0024_metadata_uploaded_on'),
    ]

    operations = [
        migrations.CreateModel(
            name='RemovalFlag',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('reason', models.TextField(max_length=2000)),
                ('requested_on', models.DateTimeField(auto_now_add=True)),
                ('metadata', models.ForeignKey(to='core.MetaData')),
                ('requested_by', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
