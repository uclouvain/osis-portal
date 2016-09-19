# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.exceptions import FieldDoesNotExist

from django.db import migrations
import uuid


def set_uuid_field(apps, schema_editor):
    """
    Set a random uuid value to all existing rows in all models containing an 'uuid' attribute in database.
    """
    base = apps.get_app_config('reference')
    for model_class in base.get_models():
        ids = model_class.objects.values_list('id', flat=True)
        if ids:
            for pk in ids:
                try:
                    model_class.objects.filter(pk=pk).update(uuid=uuid.uuid4())
                except FieldDoesNotExist:
                    break


class Migration(migrations.Migration):

    dependencies = [
        ('reference', '0003_auto_20160919_0938'),
    ]

    operations = [
        migrations.RunPython(set_uuid_field),
    ]
