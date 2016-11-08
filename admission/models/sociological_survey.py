##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2016 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
"""
Model containing the sociological background of an applicant.
This contains informations on the numbers of sisters and brothers,
father and mother's profession and so on.
"""
from django.db import models
from django.contrib import admin
from admission.models.enums import education, professional_activity
from osis_common.models.serializable_model import SerializableModel


class SociologicalSurveyAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'student_professional_activity', 'student_profession')


class SociologicalSurvey(SerializableModel):
    applicant = models.OneToOneField('Applicant', on_delete=models.CASCADE, primary_key=True)

    number_brothers_sisters = models.IntegerField(default=0)

    father_is_deceased = models.BooleanField(default=False)
    father_education = models.CharField(max_length=40, choices=education.EDUCATION_TYPE_CHOICES, blank=True, null=True)
    father_profession = models.ForeignKey('Profession', blank=True, null=True, related_name="father_profession")

    mother_is_deceased = models.BooleanField(default=False)
    mother_education = models.CharField(max_length=40, choices=education.EDUCATION_TYPE_CHOICES, blank=True, null=True)
    mother_profession = models.ForeignKey('Profession', blank=True, null=True, related_name="mother_profession")

    student_professional_activity = models.CharField(max_length=40,
                                                     choices=professional_activity.PROFESSIONAL_ACTIVITY_CHOICES,
                                                     blank=True, null=True)
    student_profession = models.ForeignKey('Profession', blank=True, null=True, related_name="student_profession")

    conjoint_professional_activity = models.CharField(max_length=40,
                                                      choices=professional_activity.PROFESSIONAL_ACTIVITY_CHOICES,
                                                      blank=True, null=True)
    conjoint_profession = models.ForeignKey('Profession', blank=True, null=True, related_name="conjoint_profession")

    paternal_grandfather_profession = models.ForeignKey('Profession', blank=True, null=True,
                                                        related_name='paternal_grandfather_profession')
    maternal_grandfather_profession = models.ForeignKey('Profession', blank=True, null=True,
                                                        related_name="maternal_grandfather_profession")
