# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.management.sql import emit_post_migrate_signal
from django.db import migrations


def add_init_internship_masters_group(apps, schema_editor):
    # create group
    db_alias = schema_editor.connection.alias
    emit_post_migrate_signal(2, False, db_alias)
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    internship_masters_group, created = Group.objects.get_or_create(name='internship_masters')
    if created:
        # Add permissions to access internship
        access_internships_perm = Permission.objects.get(codename='can_access_internship')
        internship_masters_group.permissions.add(access_internships_perm)
        # Add permissions is_internship_master
        is_master_perm = Permission.objects.get(codename='is_internship_master')
        internship_masters_group.permissions.add(is_master_perm)


class Migration(migrations.Migration):

    dependencies = [
        ('internship', '0036_auto_20190724_0957'),
    ]

    operations = [
        migrations.RunPython(add_init_internship_masters_group),
    ]
