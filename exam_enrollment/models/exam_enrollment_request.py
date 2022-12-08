##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2022 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.contrib import admin
from django.db import models
from django.db.models import JSONField

from base.models.student import Student
from osis_common.utils.models import get_object_or_none


class ExamEnrollmentRequestdAdmin(admin.ModelAdmin):
    list_display = ('student', 'offer_year_acronym', 'fetch_date')
    fieldsets = ((None, {'fields': ('student', 'document', 'offer_year_acronym', 'fetch_date')}),)
    readonly_fields = ('fetch_date',)
    search_fields = [
        'student__registration_id',
        'student__person__last_name',
        'student__person__first_name',
        'offer_year_acronym'
    ]
    raw_id_fields = ('student',)


class ExamEnrollmentRequest(models.Model):
    student = models.ForeignKey('base.Student', on_delete=models.CASCADE)
    offer_year_acronym = models.CharField(max_length=15)
    document = JSONField()
    fetch_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student}"

    class Meta:
        unique_together = ('student', 'offer_year_acronym',)


def insert_or_update_document(acronym, student, document):
    exam_enrollment_request_object, created = ExamEnrollmentRequest.objects.update_or_create(
        offer_year_acronym=acronym, student=student, defaults={"document": document})
    return exam_enrollment_request_object


def get_by_student_and_offer_year_acronym_and_fetch_date(student: Student, offer_year_acronym: str, fetch_date_limit):
    return get_object_or_none(
        ExamEnrollmentRequest,
        student=student,
        offer_year_acronym=offer_year_acronym,
        fetch_date__gte=fetch_date_limit
    )
