# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20150715_1229'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='active',
            field=models.BooleanField(verbose_name='active', default=True),
        ),
    ]
