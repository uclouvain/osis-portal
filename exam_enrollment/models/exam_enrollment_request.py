##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2017 Université catholique de Louvain (http://www.uclouvain.be)
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
import json
from django.contrib import admin
from django.contrib.postgres.fields import JSONField
from django.core.exceptions import ObjectDoesNotExist
from django.db import models


class ExamEnrollmentRequestdAdmin(admin.ModelAdmin):
    list_display = ('student',)
    fieldsets = ((None, {'fields': ('student', 'document')}),)
    search_fields = ['student__registration_id']
    raw_id_fields = ('student',)


class ExamEnrollmentRequest(models.Model):
    student = models.ForeignKey('base.Student')
    document = JSONField()

    def __str__(self):
        return "{}".format(self.student)


def insert_or_update_document(student, document):
    exam_enrollment_request_object, created = ExamEnrollmentRequest.objects.update_or_create(
        student=student, defaults={"document": document})
    return exam_enrollment_request_object


def pop_document(student):
    try:
        exam_enrollments_request = ExamEnrollmentRequest.objects.get(student=student)
        document = json.loads(exam_enrollments_request.document)
        exam_enrollments_request.delete()
        return document
    except ObjectDoesNotExist:
        return None
