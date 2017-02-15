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
from osis_common.models.serializable_model import SerializableModel, SerializableModelAdmin
from attribution.models.enums import function as function_enum
from django.core.exceptions import ObjectDoesNotExist


class TutorApplicationAdmin(SerializableModelAdmin):
    list_display = ('tutor', 'function', 'learning_unit_year')
    list_filter = ('function',)
    fieldsets = ((None, {'fields': ('learning_unit_year', 'tutor', 'function')}),)
    raw_id_fields = ('learning_unit_year', 'tutor')
    search_fields = ['tutor__person__first_name', 'tutor__person__last_name', 'learning_unit_year__acronym']


class TutorApplication(SerializableModel):
    external_id = models.CharField(max_length=100, blank=True, null=True)
    function = models.CharField(max_length=35, blank=True, null=True, choices=function_enum.FUNCTIONS, db_index=True)
    learning_unit_year = models.ForeignKey('base.LearningUnitYear', blank=True, null=True, default=None)
    tutor = models.ForeignKey('base.Tutor')
    remark = models.TextField(blank=True, null=True)
    course_summary = models.TextField(blank=True, null=True)

    class Meta:
        permissions = (
            ("can_access_attribution_application", "Can access attribution application"),
        )

    def __str__(self):
        return u"%s - %s" % (self.tutor.person, self.function)


def find_by_id(a_tutor_application_id):
    return TutorApplication.objects.get(id=a_tutor_application_id)


def search(tutor=None, learning_unit_year=None, function=None):
    queryset = TutorApplication.objects

    if tutor:
        queryset = queryset.filter(tutor=tutor)

    if learning_unit_year:
        queryset = queryset.filter(learning_unit_year=learning_unit_year)

    if function:
        queryset = queryset.filter(function=function)

    return queryset.select_related('tutor', 'learning_unit_year')


def find_by_dates_tutor(a_start_year, an_end_year, a_tutor):
    return TutorApplication.objects.filter(start_year__gte=a_start_year,
                                           end_year__lte=an_end_year,
                                           tutor=a_tutor).order_by('learning_unit_year__acronym', 'id')


def find_tutor_by_tutor_year(a_tutor, an_academic_year):
    if a_tutor and an_academic_year:
        try:
            return TutorApplication.objects.filter(tutor=a_tutor,
                                                   learning_unit_year__academic_year=an_academic_year)
        except ObjectDoesNotExist:
            return None
    return None
