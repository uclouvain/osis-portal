# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2019-04-05 15:18
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0048_auto_20190405_1523'),
    ]

    operations = [
        migrations.RunSQL(
            """               
                update base_learningcomponentyear
                set learning_unit_year_id = luc.learning_unit_year_id 
                from base_learningunitcomponent as luc
                where luc.learning_component_year_id = base_learningcomponentyear.id
            """
        ),
    ]
