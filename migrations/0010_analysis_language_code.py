# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geosafe', '0009_auto_20181003_0201'),
    ]

    operations = [
        migrations.AddField(
            model_name='analysis',
            name='language_code',
            field=models.CharField(help_text=b'Language being used by the django app', max_length=10, null=True, verbose_name=b'Language Code', blank=True),
        ),
    ]
