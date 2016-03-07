# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('password', models.CharField(verbose_name='password', max_length=128)),
                ('last_login', models.DateTimeField(null=True, verbose_name='last login', blank=True)),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, verbose_name='username', validators=[django.core.validators.RegexValidator('^[a-zA-Z0-9][a-zA-Z0-9A-Z\\-]*[a-zA-Z0-9]+$', 'Username may only contain alphanumeric characters or single hyphens, and cannot begin or end with a hyphen')], unique=True, help_text='Required. 39 characters or fewer.  alphanumeric characters or single hyphens, and cannot begin or end with a hyphen', max_length=39)),
                ('email', models.EmailField(error_messages={'unique': 'A user with that email already exists.'}, verbose_name='email address', unique=True, blank=True, max_length=200)),
                ('first_name', models.CharField(verbose_name='first name', blank=True, max_length=30)),
                ('last_name', models.CharField(verbose_name='last name', blank=True, max_length=30)),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
        ),
        migrations.CreateModel(
            name='ProjectPermission',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('key', models.CharField(verbose_name='project permission key', unique=True, max_length=200)),
                ('description', models.TextField(verbose_name='project permission description', blank=True)),
                ('active', models.BooleanField(default=True, verbose_name='project permission active')),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='project_permissions',
            field=models.ManyToManyField(to='users.ProjectPermission'),
        ),
    ]
