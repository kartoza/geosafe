# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geosafe', '0010_analysis_language_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='metadata',
            name='keywords_json',
            field=models.TextField(default=b'{}', null=True, verbose_name=b'Full representation of InaSAFE keywords in json format', blank=True),
        ),
    ]
