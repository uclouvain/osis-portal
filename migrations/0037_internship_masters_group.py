# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def add_init_internship_masters_group(apps, schema_editor):
    # create group
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    internship_masters_group, created = Group.objects.get_or_create(name='internship_masters')
    if created:
        # Add permissions to access internship
        access_internships_perm = Permission.objects.get(codename='can_access_internship', content_type__model='internshipoffer')
        internship_masters_group.permissions.add(access_internships_perm)


class Migration(migrations.Migration):

    dependencies = [
        ('internship', '0036_auto_20190724_0957'),
    ]

    operations = [
        # migrations.RunPython(add_init_internship_masters_group),
    ]
