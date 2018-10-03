# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('geosafe', '0007_auto_20180914_0738'),
    ]

    operations = [
        migrations.AlterField(
            model_name='analysis',
            name='exposure_layer',
            field=models.ForeignKey(related_name='exposure_layer', on_delete=django.db.models.deletion.SET_NULL, verbose_name=b'Exposure Layer', to='layers.Layer', help_text=b'Exposure layer for analysis.', null=True),
        ),
        migrations.AlterField(
            model_name='analysis',
            name='hazard_layer',
            field=models.ForeignKey(related_name='hazard_layer', on_delete=django.db.models.deletion.SET_NULL, verbose_name=b'Hazard Layer', to='layers.Layer', help_text=b'Hazard layer for analysis.', null=True),
        ),
    ]
