# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import core.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0002_auto_20160204_1530'),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=20, help_text='A short, descriptive name for the document')),
                ('uploaded', models.DateTimeField(auto_now_add=True)),
                ('document', models.FileField(upload_to=core.models.document_upload_path)),
                ('document_type', models.CharField(choices=[('E', 'EIA report'), ('O', 'Other')], max_length=1, default='E')),
                ('metadata', models.ForeignKey(to='core.MetaData', null=True, blank=True)),
                ('project', models.ForeignKey(to='core.Project')),
                ('uploader', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PreviousDeveloper',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('stopped', models.DateTimeField(auto_now_add=True)),
                ('developer', models.ForeignKey(to='core.Developer')),
                ('project', models.ForeignKey(to='core.Project')),
            ],
        ),
        migrations.CreateModel(
            name='PreviousProjectName',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('previous_name', models.CharField(max_length=50)),
                ('stopped', models.DateTimeField(auto_now_add=True)),
                ('project', models.ForeignKey(to='core.Project')),
            ],
        ),
        migrations.RemoveField(
            model_name='documents',
            name='project',
        ),
        migrations.RemoveField(
            model_name='documents',
            name='uploader',
        ),
        migrations.RemoveField(
            model_name='previousdevelopers',
            name='developer',
        ),
        migrations.RemoveField(
            model_name='previousdevelopers',
            name='project',
        ),
        migrations.RemoveField(
            model_name='previousprojectnames',
            name='project',
        ),
        migrations.RemoveField(
            model_name='populationdata',
            name='observed',
        ),
        migrations.DeleteModel(
            name='Documents',
        ),
        migrations.DeleteModel(
            name='PreviousDevelopers',
        ),
        migrations.DeleteModel(
            name='PreviousProjectNames',
        ),
    ]
