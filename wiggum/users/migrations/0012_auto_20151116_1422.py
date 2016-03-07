# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_auto_20151023_1228'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(max_length=50, blank=True, verbose_name='First name'),
        ),
        migrations.AlterField(
            model_name='user',
            name='last_name',
            field=models.CharField(max_length=50, blank=True, verbose_name='Last name'),
        ),
        migrations.AlterField(
            model_name='user',
            name='sfa_token',
            field=models.UUIDField(unique=True, verbose_name='SFA token', default=uuid.uuid4, editable=False),
        ),
    ]
