# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_wiggum_permission_data'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='user',
            managers=[
                ('objects', users.models.UserManager()),
            ],
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(unique=True, max_length=200, verbose_name='email address', error_messages={'unique': 'A user with that email already exists.'}),
        ),
    ]
