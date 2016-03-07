# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0002_auto_20150716_1042'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='project_permissions',
            field=models.ManyToManyField(blank=True, to='users.ProjectPermission'),
        ),
    ]
