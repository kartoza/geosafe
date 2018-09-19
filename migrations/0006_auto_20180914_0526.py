# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geosafe', '0005_auto_20170914_1101'),
    ]

    operations = [
        migrations.AddField(
            model_name='analysis',
            name='aggregation_filter',
            field=models.TextField(help_text=b'List of aggregation area being used in aggregation layer', null=True, verbose_name=b'Serialized JSON of selected aggregation area name', blank=True),
        ),
        migrations.AddField(
            model_name='analysis',
            name='filtered_aggregation',
            field=models.CharField(max_length=255, null=True, verbose_name=b'Temporary file location of filtered aggregation', blank=True),
        ),
    ]
