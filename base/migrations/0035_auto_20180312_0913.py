# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2018-03-12 08:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0034_auto_20180205_1053'),
    ]

    operations = [
        migrations.AlterField(
            model_name='learningcontaineryear',
            name='common_title',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
