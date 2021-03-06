# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-01-10 10:50
from __future__ import unicode_literals

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_modif_last_name_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='LearningUnitComponent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ('external_id', models.CharField(blank=True, max_length=100, null=True)),
                ('type', models.CharField(blank=True, choices=[('LECTURING', 'LECTURING'), ('PRACTICAL_EXERCISES', 'PRACTICAL_EXERCISES')], db_index=True, max_length=25, null=True)),
                ('duration', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
            ],
            options={
                'permissions': (('can_access_learningunit', 'Can access learning unit'),),
            },
        ),
        migrations.CreateModel(
            name='LearningUnitEnrollment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ('external_id', models.CharField(blank=True, max_length=100, null=True)),
                ('changed', models.DateTimeField(null=True)),
                ('date_enrollment', models.DateField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='LearningUnitYear',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ('external_id', models.CharField(blank=True, max_length=100, null=True)),
                ('acronym', models.CharField(db_index=True, max_length=15)),
                ('title', models.CharField(max_length=255)),
                ('credits', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('weight', models.IntegerField(blank=True, null=True)),
                ('team', models.BooleanField(default=False)),
                ('academic_year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.AcademicYear')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='learningunitenrollment',
            name='learning_unit_year',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.LearningUnitYear'),
        ),
        migrations.AddField(
            model_name='learningunitenrollment',
            name='offer_enrollment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.OfferEnrollment'),
        ),
        migrations.AddField(
            model_name='learningunitcomponent',
            name='learning_unit_year',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.LearningUnitYear'),
        ),
    ]
