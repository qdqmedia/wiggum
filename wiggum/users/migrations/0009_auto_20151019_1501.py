# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuid
import django.core.validators
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_user_external_service'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'verbose_name': 'User', 'verbose_name_plural': 'Users'},
        ),
        migrations.AlterField(
            model_name='projectpermission',
            name='active',
            field=models.BooleanField(verbose_name='Project permission active', default=True),
        ),
        migrations.AlterField(
            model_name='projectpermission',
            name='description',
            field=models.TextField(verbose_name='Project permission description', blank=True),
        ),
        migrations.AlterField(
            model_name='projectpermission',
            name='key',
            field=models.CharField(verbose_name='Project permission key', max_length=200, unique=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='active',
            field=models.BooleanField(verbose_name='Active', default=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='date_joined',
            field=models.DateTimeField(verbose_name='Date joined', default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(error_messages={'unique': 'A user with that email already exists.'}, verbose_name='Email address', max_length=200, unique=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='external_service',
            field=models.CharField(verbose_name='External service', max_length=50, blank=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(verbose_name='First name', max_length=30, blank=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='last_name',
            field=models.CharField(verbose_name='Last name', max_length=30, blank=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='password_reset_token',
            field=models.UUIDField(editable=False, verbose_name='Password reset token', unique=True, default=uuid.uuid4),
        ),
        migrations.AlterField(
            model_name='user',
            name='password_reset_token_expire',
            field=models.DateTimeField(verbose_name='Password reset token', default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(verbose_name='Username', max_length=39, validators=[django.core.validators.RegexValidator('^[a-zA-Z0-9][a-zA-Z0-9A-Z\\-]*[a-zA-Z0-9]+$', 'Username may only contain alphanumeric characters or single hyphens, and cannot begin or end with a hyphen')], help_text='Required. 39 characters or fewer.  alphanumeric characters or single hyphens, and cannot begin or end with a hyphen', error_messages={'unique': 'A user with that username already exists.'}, unique=True),
        ),
    ]
