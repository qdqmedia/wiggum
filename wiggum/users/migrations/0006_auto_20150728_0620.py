# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid
from django.db import models, migrations
import django.utils.timezone


def gen_uuid(apps, schema_editor):
    UserModel = apps.get_model('users', 'User')
    for row in UserModel.objects.all():
        row.password_reset_token = uuid.uuid4()
        row.save()


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_auto_20150716_1202'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='password_reset_token',
            field=models.UUIDField(null=True, unique=True, editable=False, verbose_name='password reset token'),
        ),

        migrations.RunPython(gen_uuid, reverse_code=migrations.RunPython.noop),

        migrations.AlterField(
            model_name='user',
            name='password_reset_token',
            field=models.UUIDField(unique=True, editable=False, verbose_name='password reset token'),
        ),

        migrations.AddField(
            model_name='user',
            name='password_reset_token_expire',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='password reset token'),
        ),
    ]
