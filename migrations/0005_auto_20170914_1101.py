# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geosafe', '0004_auto_20170914_1024'),
    ]

    operations = [
        migrations.AlterField(
            model_name='metadata',
            name='keywords_xml',
            field=models.TextField(default=b'', null=True, verbose_name=b'Full representation of InaSAFE keywords in xml format', blank=True),
        ),
    ]
