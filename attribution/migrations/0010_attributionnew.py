# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-10-23 15:07
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attribution', '0009_attribution_deleted'),
    ]

    operations = [
        migrations.CreateModel(
            name='AttributionNew',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('global_id', models.CharField(max_length=10, unique=True)),
                ('attributions', django.contrib.postgres.fields.jsonb.JSONField()),
                ('applications', django.contrib.postgres.fields.jsonb.JSONField()),
            ],
        ),
    ]