# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geosafe', '0003_auto_20170816_0123'),
    ]

    operations = [
        migrations.AddField(
            model_name='metadata',
            name='keywords_xml',
            field=models.CharField(default=b'', max_length=4000, null=True, verbose_name=b'Full representation of InaSAFE keywords in xml format', blank=True),
        ),
        migrations.AlterField(
            model_name='metadata',
            name='layer',
            field=models.OneToOneField(related_name='inasafe_metadata', primary_key=True, serialize=False, to='layers.Layer'),
        ),
    ]
