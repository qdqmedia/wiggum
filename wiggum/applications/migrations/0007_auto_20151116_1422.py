# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0006_auto_20151019_1501'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='theme',
            field=models.CharField(max_length=50, choices=[('clancy', 'clancy')], verbose_name='App associated theme', default='clancy'),
        ),
    ]
