# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-01-19 15:42
from __future__ import unicode_literals

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0006_auto_20170112_1332'),
    ]

    operations = [
        migrations.CreateModel(
            name='AcademicCalendar',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ('title', models.CharField(blank=True, max_length=50, null=True)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('reference', models.CharField(blank=True, max_length=25, null=True)),
                ('academic_year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.AcademicYear')),
            ],
            options={
                'permissions': (('can_access_academic_calendar', 'Can access academic calendar'),),
            },
        ),
    ]