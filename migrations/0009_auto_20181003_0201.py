# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('geosafe', '0008_auto_20181002_1109'),
    ]

    operations = [
        migrations.AlterField(
            model_name='analysis',
            name='aggregation_layer',
            field=models.ForeignKey(related_name='aggregation_layer', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='layers.Layer', help_text=b'Aggregation layer for analysis.', null=True, verbose_name=b'Aggregation Layer'),
        ),
    ]
