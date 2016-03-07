# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_auto_20150728_0620'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='password_reset_token',
            field=models.UUIDField(unique=True, default=uuid.uuid4, editable=False, verbose_name='password reset token'),
        ),
    ]
