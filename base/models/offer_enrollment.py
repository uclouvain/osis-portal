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

from base.models.enums import offer_enrollment_state
from osis_common.models.serializable_model import SerializableModel, SerializableModelAdmin


class OfferEnrollmentAdmin(SerializableModelAdmin):
    list_display = ('education_group_year', 'student', 'date_enrollment', 'enrollment_state',)
    fieldsets = ((None, {'fields': ('education_group_year', 'student', 'date_enrollment', 'enrollment_state',)}),)
    raw_id_fields = ('education_group_year', 'student', )
    search_fields = ['education_group_year__acronym', 'student__person__first_name', 'student__person__last_name',
                     'student__registration_id', 'enrollment_state']


class OfferEnrollment(SerializableModel):
    external_id = models.CharField(max_length=100, blank=True, null=True)
    date_enrollment = models.DateField()
    student = models.ForeignKey('Student', on_delete=models.PROTECT)
    enrollment_state = models.CharField(max_length=15, choices=offer_enrollment_state.STATES, blank=True, null=True)
    education_group_year = models.ForeignKey('EducationGroupYear', on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.student} - {self.education_group_year}"
