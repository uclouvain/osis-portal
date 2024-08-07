# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-01-12 13:32
from __future__ import unicode_literals

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0005_auto_20170110_1050'),
    ]

    operations = [
        migrations.CreateModel(
            name='LearningUnit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ('external_id', models.CharField(blank=True, max_length=100, null=True)),
                ('acronym', models.CharField(max_length=15)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
            ],
            options={
                'permissions': (('can_access_learningunit', 'Can access learning unit'),),
            },
        ),
        migrations.AddField(
            model_name='learningunityear',
            name='in_charge',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='learningunityear',
            name='vacant',
            field=models.BooleanField(default=False),
        ),
    ]
