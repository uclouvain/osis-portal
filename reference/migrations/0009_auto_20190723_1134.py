# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2019-07-23 09:34
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('reference', '0008_auto_20180727_1013'),
    ]

    operations = [
        migrations.AlterField(
            model_name='domain',
            name='decree',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT,
                                    to='reference.Decree'),
        ),
        migrations.AlterField(
            model_name='domain',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT,
                                    to='reference.Domain'),
        ),
    ]
