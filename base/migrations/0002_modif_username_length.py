# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-09-28 15:49
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL("alter table auth_user alter column username type varchar(254);")
    ]
