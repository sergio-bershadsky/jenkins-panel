# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jenkins', '0002_auto_20160102_1431'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='params',
            field=models.TextField(null=True, blank=True),
        ),
    ]
