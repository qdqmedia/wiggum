# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0007_auto_20151116_1422'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='theme',
            field=models.CharField(verbose_name='App associated theme', max_length=50, default='clancy', choices=[]),
        ),
    ]
