# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-04-07 12:55
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('internship', '0023_reset_internship_id_seq'),
    ]

    operations = [
        migrations.RenameField(
            model_name='periodinternshipplaces',
            old_name='internship',
            new_name='internship_offer',
        ),
    ]