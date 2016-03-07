# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def create_wiggum_permissions(apps, schema_editor):
    permissions = (
        ('wiggum.impersonate', "Add impersonate permission"),)

    ProjectPermission = apps.get_model("users", "ProjectPermission")
    for i in permissions:
        ProjectPermission(key=i[0], description=i[1]).save()


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_auto_20151019_1501'),
    ]

    operations = [
        migrations.RunPython(create_wiggum_permissions),
    ]
