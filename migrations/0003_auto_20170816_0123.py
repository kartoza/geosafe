# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('geosafe', '0002_analysis_user_extent'),
    ]

    operations = [
        migrations.AddField(
            model_name='analysis',
            name='end_time',
            field=models.DateTimeField(default=datetime.datetime.now, verbose_name=b'end_time'),
        ),
        migrations.AddField(
            model_name='analysis',
            name='start_time',
            field=models.DateTimeField(default=datetime.datetime.now, verbose_name=b'start_time'),
        ),
    ]
