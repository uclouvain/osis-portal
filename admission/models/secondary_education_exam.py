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
from django.db import models
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from osis_common.models.serializable_model import SerializableModel


class SecondaryEducationExamAdmin(admin.ModelAdmin):
    list_display = ('type', 'result', 'exam_date', 'institution')


class SecondaryEducationExam(SerializableModel):
    RESULT_TYPE = (('LOW', 'Moins de 65%'),
                   ('MIDDLE', 'entre 65% et 75%'),
                   ('HIGH', 'plus de 75%'),
                   ('NO_RESULT', 'pas encore de résultat'))

    LOCAL_LANGUAGE_EXAM_RESULT_TYPE = (('SUCCEED', _('succeeded')),
                                       ('FAILED', _('failed')),
                                       ('ENROLLMENT_IN_PROGRESS', _('demanded_result')))

    EXAM_TYPES = (('ADMISSION', _('admission')),
                  ('LANGUAGE', _('language')),
                  ('PROFESSIONAL', _('professional')))

    secondary_education = models.ForeignKey('SecondaryEducation')
    admission_exam_type = models.ForeignKey('AdmissionExamType', blank=True, null=True)
    type = models.CharField(max_length=20, choices=EXAM_TYPES)
    exam_date = models.DateField(blank=True, null=True)
    institution = models.CharField(max_length=100, blank=True, null=True)
    result = models.CharField(max_length=30, choices=RESULT_TYPE+LOCAL_LANGUAGE_EXAM_RESULT_TYPE, blank=True, null=True)

    def __str__(self):
        return self.institution


def search(pk=None, secondary_education_id=None, type=None):
    queryset = SecondaryEducationExam.objects

    if pk:
        queryset = queryset.filter(id=pk)

    if secondary_education_id:
        queryset = queryset.filter(secondary_education_id=secondary_education_id)

    if type:
        queryset = queryset.filter(type=type)

    return queryset


def find_by_type(secondary_education_id=None, type=None):
    results = search(None, secondary_education_id, type)
    if results and results.exists():
        return results[0]
    return None


def find_by_secondary_education(secondary_education=None):
    results = search(None, secondary_education, None)
    if results and results.exists():
        return results[0]
    return None

