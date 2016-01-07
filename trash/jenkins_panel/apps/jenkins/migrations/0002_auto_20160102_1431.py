# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('jenkins', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='params',
            field=models.TextField(null=True, editable=False, blank=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='name',
            field=models.CharField(max_length=32, validators=[django.core.validators.RegexValidator(b'^[a-z]+[a-z-]*[a-z]?$')]),
        ),
    ]
