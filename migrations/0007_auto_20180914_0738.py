# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geosafe', '0006_auto_20180914_0526'),
    ]

    operations = [
        migrations.AlterField(
            model_name='analysis',
            name='impact_function_id',
            field=models.CharField(help_text=b'The ID of Impact Function used in the analysis.', max_length=100, null=True, verbose_name=b'ID of Impact Function', blank=True),
        ),
    ]
