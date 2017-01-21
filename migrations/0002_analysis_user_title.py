# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geosafe', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='analysis',
            name='user_title',
            field=models.CharField(help_text=b'Title to assign after analysis is generated.', max_length=255, null=True, verbose_name=b'User defined title for analysis', blank=True),
        ),
    ]
