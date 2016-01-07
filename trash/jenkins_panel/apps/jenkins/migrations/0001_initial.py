# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('signature', models.CharField(max_length=64, editable=False)),
                ('label', models.CharField(max_length=64)),
                ('name', models.CharField(max_length=32, validators=[django.core.validators.RegexValidator(b'^[a-z]+[a-z-]+[a-z]&')])),
                ('description', models.TextField(max_length=64, null=True, blank=True)),
                ('parents', models.CharField(max_length=64)),
                ('nodes', models.CharField(max_length=64)),
            ],
            options={
                'verbose_name': '\u041f\u0440\u043e\u0435\u043a\u0442',
                'verbose_name_plural': '\u041f\u0440\u043e\u0435\u043a\u0442\u044b',
            },
        ),
        migrations.CreateModel(
            name='View',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=64)),
                ('description', models.TextField()),
            ],
            options={
                'verbose_name': '\u0412\u0438\u0434 (\u0433\u0440\u0443\u043f\u043f\u0430)',
                'verbose_name_plural': '\u0412\u0438\u0434\u044b (\u0433\u0440\u0443\u043f\u043f\u044b)',
            },
        ),
    ]
