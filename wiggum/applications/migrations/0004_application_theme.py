# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0003_auto_20150716_1206'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='theme',
            field=models.CharField(default='default', verbose_name='app associated theme', max_length=50, choices=[('default', 'default')]),
        ),
    ]
