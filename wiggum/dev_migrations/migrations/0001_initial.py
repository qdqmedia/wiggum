# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

from users.models import User, ProjectPermission
from applications.models import Application


def create_permissions(apps, schema_editor):
    permissions = (
        {"description": "App test permission for reading",
         "key": "app.test.read"},

        {"description": "Test app write permission",
         "key": "app.test.write"},)

    for p in permissions:
        ProjectPermission(
            key=p["key"],
            description=p["description"]).save()


def create_users(apps, schema_editor):
    users = (
        {"username": "admin",
         "first_name": "Guybrush",
         "last_name": "Threepwood",
         "email": "admin@wiggum.io",
         "password": "admin",
         "project_permissions": [
            "wiggum.all",
            "wiggum.impersonate",
            "app.test.read",
            "app.test.write", ]},

        {"username": "batman",
         "last_name": "Wayne",
         "first_name": "Bruce",
         "email": "dark_knight@dccomics.com",
         "password": "batman",
         "project_permissions": [
            "app.test.read",
            "app.test.write", ]},

        {"username": "spiderman",
         "last_name": "Parker",
         "first_name": "Peter",
         "email": "spidy@marvelcomics.com",
         "password": "spiderman",
         "project_permissions": [
            "app.test.read", ]}, )

    # Get applications
    permissions = {}
    for p in ProjectPermission.objects.all():
        permissions[p.key] = p

    # Save users
    for u in users:
        user = User(
            username=u["username"],
            first_name=u["first_name"],
            last_name=u["last_name"],
            email=u["email"],)
        user.save()

        user.set_password(u["password"])
        for up in u["project_permissions"]:
            user.project_permissions.add(permissions[up])

        user.save()


def create_apps(apps, schema_editor):
    apps = (
        {"theme": "clancy",
         "description": "",
         "name": "App1"},

        {"theme": "clancy",
         "description": "",
         "name": "App2"},

        {"theme": "clancy",
            "description": "",
            "name": "App3"},)

    for a in apps:
        Application(
            name=a["name"],
            description=a["description"]).save()


class Migration(migrations.Migration):

    dependencies = [
        ('users', "0012_auto_20151116_1422"),
        ('applications', "0007_auto_20151116_1422"), ]

    operations = [
        migrations.RunPython(create_permissions),
        migrations.RunPython(create_users),
        migrations.RunPython(create_apps), ]
