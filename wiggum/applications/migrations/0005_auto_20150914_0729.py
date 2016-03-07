# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0004_application_theme'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='theme',
            field=models.CharField(max_length=50, verbose_name='app associated theme', choices=[('eq', 'eq'), ('default', 'default')], default='default'),
        ),
    ]
