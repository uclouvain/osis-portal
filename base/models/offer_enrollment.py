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
from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from attribution.models.enums import offer_enrollment_state
from base.models.offer_year import OfferYear
from osis_common.models.serializable_model import SerializableModel, SerializableModelAdmin


class OfferEnrollmentAdmin(SerializableModelAdmin):
    list_display = ('offer_year', 'student', 'date_enrollment', 'enrollment_state')
    fieldsets = ((None, {'fields': ('offer_year', 'student', 'date_enrollment', 'enrollment_state')}),)
    raw_id_fields = ('offer_year', 'student')
    search_fields = ['offer_year__acronym', 'student__person__first_name', 'student__person__last_name',
                     'student__registration_id', 'enrollment_state']


class OfferEnrollment(SerializableModel):
    external_id = models.CharField(max_length=100, blank=True, null=True)
    date_enrollment = models.DateField()
    offer_year = models.ForeignKey(OfferYear)
    student = models.ForeignKey('Student')
    enrollment_state = models.CharField(max_length=15, choices=offer_enrollment_state.STATES, blank=True, null=True)

    def __str__(self):
        return u"%s - %s" % (self.student, self.offer_year)


def find_by_student(a_student):
    return OfferEnrollment.objects.filter(student=a_student)


def find_by_student_offer(a_student, offer_year):
    try:
        return OfferEnrollment.objects.get(student=a_student, offer_year=offer_year)
    except ObjectDoesNotExist:
        return None


def find_by_student_academic_year(a_student, an_academic_year):
    return OfferEnrollment.objects.filter(student=a_student, offer_year__academic_year=an_academic_year)
