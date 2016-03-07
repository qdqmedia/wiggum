# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import applications.utils
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0005_auto_20150914_0729'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='active',
            field=models.BooleanField(verbose_name='Application active', default=True),
        ),
        migrations.AlterField(
            model_name='application',
            name='description',
            field=models.TextField(verbose_name='Application description', blank=True),
        ),
        migrations.AlterField(
            model_name='application',
            name='name',
            field=models.CharField(verbose_name='Application name', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='application',
            name='theme',
            field=models.CharField(verbose_name='App associated theme', max_length=50, choices=[('clancy', 'clancy'), ], default='clancy'),
        ),
        migrations.AlterField(
            model_name='application',
            name='token',
            field=models.CharField(verbose_name='Application token', max_length=32, validators=[django.core.validators.RegexValidator('^[a-fA-F0-9]{32}$', 'Key should be hexadecimal and length 32')], unique=True, default=applications.utils.generate_api_key),
        ),
    ]
