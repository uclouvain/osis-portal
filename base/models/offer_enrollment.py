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

from base.models.offer_year import OfferYear
from osis_common.models.serializable_model import SerializableModel


class OfferEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('offer_year', 'student', 'date_enrollment')
    fieldsets = ((None, {'fields': ('offer_year','student','date_enrollment')}),)
    raw_id_fields = ('offer_year', 'student')
    search_fields = ['offer_year__acronym', 'student__person__first_name', 'student__person__last_name']


class OfferEnrollment(SerializableModel):
    external_id = models.CharField(max_length=100, blank=True, null=True)
    date_enrollment = models.DateField()
    offer_year = models.ForeignKey(OfferYear)
    student = models.ForeignKey('Student')

    def __str__(self):
        return u"%s - %s" % (self.student, self.offer_year)


def find_by_student(a_student):
    return OfferEnrollment.objects.filter(student=a_student)


def find_by_student_ordered(a_student):
    return find_by_student(a_student).order_by("-offer_year__academic_year__year")


def find_by_student_offer(a_student, offer_year):
    return OfferEnrollment.objects.filter(student=a_student, offer_year=offer_year)
