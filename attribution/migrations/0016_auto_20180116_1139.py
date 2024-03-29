# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2018-01-16 10:39
from __future__ import unicode_literals

from django.core.exceptions import FieldError, FieldDoesNotExist
from django.db import migrations
from django.utils import timezone


def set_deleted_new_field(apps, schema_editor):
    attribution = apps.get_app_config('attribution')
    default_datetime = timezone.now()
    for model_class in attribution.get_models():
        try:
            model_class.objects.filter(deleted=True).update(deleted_new=default_datetime)
        except (FieldError, FieldDoesNotExist):
            continue


class Migration(migrations.Migration):

    dependencies = [
        ('attribution', '0015_attribution_deleted_new'),
    ]

    operations = [
        migrations.RunPython(set_deleted_new_field, migrations.RunPython.noop),
    ]
