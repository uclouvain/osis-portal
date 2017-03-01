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
from osis_common.models.serializable_model import SerializableModelAdmin, SerializableModel


class InternshipStudentAffectationStatAdmin(SerializableModelAdmin):
    list_display = ('student', 'organization', 'speciality', 'period', 'choice', 'cost', 'consecutive_month',
                    'type_of_internship')
    fieldsets = ((None, {'fields': ('student', 'organization', 'speciality', 'period', 'choice', 'cost',
                                    'consecutive_month', 'type_of_internship')}),)
    raw_id_fields = ('student', 'organization', 'speciality', 'period')


class InternshipStudentAffectationStat(SerializableModel):
    student = models.ForeignKey('base.Student')
    organization = models.ForeignKey('internship.Organization')
    speciality = models.ForeignKey('internship.InternshipSpeciality')
    period = models.ForeignKey('internship.Period')
    choice = models.CharField(max_length=1, blank=False, null=False, default='0')
    cost = models.IntegerField(blank=False, null=False)
    consecutive_month = models.BooleanField(default=False, null=False)
    type_of_internship = models.CharField(max_length=1, blank=False, null=False, default='N')


def search(student=None):
    return InternshipStudentAffectationStat.objects.filter(student=student).order_by('period__date_start')