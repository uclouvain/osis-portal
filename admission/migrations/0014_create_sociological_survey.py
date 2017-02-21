# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('admission', '0013_sociological_survey_delete'),
    ]

    operations = [
        migrations.CreateModel(
            name='SociologicalSurvey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('applicant', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, serialize=False, to='admission.Applicant')),
                ('number_brothers_sisters', models.IntegerField(default=0)),
                ('father_is_deceased', models.BooleanField(default=False)),
                ('father_education', models.CharField(blank=True, choices=[('UNKNOWN', 'UNKNOWN'), ('PRIMARY', 'PRIMARY'), ('SECONDARY_INFERIOR', 'SECONDARY_INFERIOR'), ('SECONDARY_SUPERIOR', 'SECONDARY_SUPERIOR'), ('SUPERIOR_NON_UNIVERSITY', 'SECONDARY_SUPERIOR'), ('UNIVERSITY', 'UNIVERSITY')], max_length=40, null=True)),
                ('mother_is_deceased', models.BooleanField(default=False)),
                ('mother_education', models.CharField(blank=True, choices=[('UNKNOWN', 'UNKNOWN'), ('PRIMARY', 'PRIMARY'), ('SECONDARY_INFERIOR', 'SECONDARY_INFERIOR'), ('SECONDARY_SUPERIOR', 'SECONDARY_SUPERIOR'), ('SUPERIOR_NON_UNIVERSITY', 'SECONDARY_SUPERIOR'), ('UNIVERSITY', 'UNIVERSITY')], max_length=40, null=True)),
                ('student_professional_activity', models.CharField(blank=True, choices=[('NO_PROFESSION', 'NO_PROFESSION'), ('PART_TIME', 'PART_TIME'), ('FULL_TIME', 'FULL_TIME')], max_length=40, null=True)),
                ('conjoint_professional_activity', models.CharField(blank=True, choices=[('NO_PROFESSION', 'NO_PROFESSION'), ('PART_TIME', 'PART_TIME'), ('FULL_TIME', 'FULL_TIME')], max_length=40, null=True)),
                ('conjoint_profession', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='conjoint_profession', to='admission.Profession')),
                ('father_profession', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='father_profession', to='admission.Profession')),
                ('maternal_grandfather_profession', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='maternal_grandfather_profession', to='admission.Profession')),
                ('mother_profession', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='mother_profession', to='admission.Profession')),
                ('paternal_grandfather_profession', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='paternal_grandfather_profession', to='admission.Profession')),
                ('student_profession', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='student_profession', to='admission.Profession')),
            ],
        ),
    ]
