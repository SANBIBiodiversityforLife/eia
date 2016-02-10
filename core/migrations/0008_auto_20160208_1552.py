# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20160208_0941'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='focalsitedata',
            name='count',
        ),
        migrations.AddField(
            model_name='focalsitedata',
            name='abundance',
            field=models.IntegerField(default=1, help_text='Absolute abundance'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='focalsite',
            name='sensitive',
            field=models.BooleanField(default=False, help_text='If the focal site concerns sensitive species and should not be visible to the public, select this.'),
        ),
        migrations.AlterField(
            model_name='focalsitedata',
            name='activity',
            field=models.CharField(choices=[('CDP', 'courtship display'), ('CAN', 'adult bird carrying nesting material'), ('ANB', 'active nest building'), ('NCN', 'newly completed nest'), ('NWE', 'nest with eggs'), ('NWC', 'nest with chicks'), ('PFY', 'parents feeding young in nest'), ('PFS', 'parents with fecal sac'), ('PAY', 'parents and young not in nest')], help_text='Activity (only <br>applicable to birds)', blank=True, null=True, max_length=3),
        ),
        migrations.AlterField(
            model_name='focalsitedata',
            name='life_stage',
            field=models.CharField(default='A', help_text='Specify life stage', choices=[('C', 'Chick/pup'), ('J', 'Juvenile'), ('A', 'Adult')], max_length=1),
        ),
        migrations.AlterField(
            model_name='focalsitedata',
            name='observed',
            field=models.DateTimeField(help_text='Date<br>observed'),
        ),
    ]
