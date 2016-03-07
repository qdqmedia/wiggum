# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuid
import django.utils.timezone

def gen_uuid(apps, schema_editor):
    UserModel = apps.get_model('users', 'User')
    for row in UserModel.objects.all():
        row.sfa_token = uuid.uuid4()
        row.save()


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_auto_wiggum_permission_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='sfa_token',
            field=models.UUIDField(null=True, editable=False, unique=True, verbose_name='SFA token'),
        ),

        migrations.RunPython(gen_uuid, reverse_code=migrations.RunPython.noop),

        migrations.AlterField(
            model_name='user',
            name='sfa_token',
            field=models.UUIDField(editable=False, unique=True, verbose_name='SFA token'),
        ),

        migrations.AddField(
            model_name='user',
            name='sfa_token_expire',
            field=models.DateTimeField(verbose_name='SFA token expiration', default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='user',
            name='password_reset_token_expire',
            field=models.DateTimeField(verbose_name='Password reset token expiration', default=django.utils.timezone.now),
        ),
    ]
