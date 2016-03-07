# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_auto_20150729_0842'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='external_service',
            field=models.CharField(max_length=50, verbose_name='external service', blank=True),
        ),
    ]
