# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def forwards_func(apps, schema_editor):
    # We get the model from the versioned app registry;
    # if we directly import it, it'll be the wrong version
    LearningUnit = apps.get_model("base", "LearningUnit")
    db_alias = schema_editor.connection.alias
    learning_unit_internship, created = \
        LearningUnit.objects.using(db_alias).get_or_create(acronym="WMDS2333", defaults={'title': 'Stages'})

    Speciality = apps.get_model("internship", "InternshipSpeciality")
    Speciality.objects.using(db_alias).get_or_create(acronym="STAGE PERSONNEL",
                                                     defaults={"name": "Stage personnel",
                                                               "learning_unit": learning_unit_internship})
    Speciality.objects.using(db_alias).get_or_create(acronym="STAGE A L'ETRANGER",
                                                     defaults={"name": "Stage à l'étranger",
                                                               "learning_unit": learning_unit_internship})


class Migration(migrations.Migration):

    dependencies = [
        ('internship', '0005_auto_20170226_1225'),
    ]

    operations = [
        migrations.RunPython(forwards_func),
    ]