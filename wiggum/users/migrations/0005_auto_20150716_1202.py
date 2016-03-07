# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_user_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='project_permissions',
            field=models.ManyToManyField(blank=True, to='users.ProjectPermission'),
        ),
    ]
