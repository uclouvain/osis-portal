# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2019-05-15 16:25
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0054_populate_repartition_volumes'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='entitycomponentyear',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='entitycomponentyear',
            name='entity_container_year',
        ),
        migrations.RemoveField(
            model_name='entitycomponentyear',
            name='learning_component_year',
        ),
        migrations.DeleteModel(
            name='EntityComponentYear',
        ),
    ]
