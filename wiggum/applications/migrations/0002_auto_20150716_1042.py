# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators
import applications.utils


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='name',
            field=models.CharField(unique=True, max_length=100, default=None, verbose_name='application name'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='application',
            name='token',
            field=models.CharField(validators=[django.core.validators.RegexValidator('^[a-fA-F0-9]{32}$', 'Key should be hexadecimal and length 32')], max_length=32, unique=True, default=applications.utils.generate_api_key, verbose_name='application token'),
        ),
    ]
