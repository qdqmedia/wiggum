# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import applications.utils
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_user_active'),
    ]

    operations = [
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('token', models.CharField(default=applications.utils.generate_api_key, unique=True, validators=[django.core.validators.RegexValidator('^[a-fA-F0-9]{32}$', 'Key should be hexadecimal and length 32')], verbose_name='app token', max_length=32)),
                ('description', models.TextField(blank=True, verbose_name='application description')),
                ('active', models.BooleanField(default=True, verbose_name='application active')),
                ('project_permissions', models.ManyToManyField(to='users.ProjectPermission')),
            ],
        ),
    ]
