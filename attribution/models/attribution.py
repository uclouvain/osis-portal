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
from osis_common.models.serializable_model import SerializableModel
from attribution.models.enums import function


class AttributionAdmin(admin.ModelAdmin):
    list_display = ('tutor', 'function', 'learning_unit_year')
    list_filter = ('function',)
    fieldsets = ((None, {'fields': ('learning_unit_year', 'tutor', 'function', 'start_date', 'end_date')}),)
    raw_id_fields = ('learning_unit_year', 'tutor')
    search_fields = ['tutor__person__first_name', 'tutor__person__last_name', 'learning_unit_year__acronym']


class Attribution(SerializableModel):
    external_id = models.CharField(max_length=100, blank=True, null=True)
    function = models.CharField(max_length=15, blank=True, null=True, choices=function.FUNCTIONS, db_index=True)
    learning_unit_year = models.ForeignKey('base.LearningUnitYear', blank=True, null=True, default=None)
    tutor = models.ForeignKey('base.Tutor')
    start_date = models.DateField(auto_now=False, blank=True, null=True, auto_now_add=False)
    end_date = models.DateField(auto_now=False, blank=True, null=True, auto_now_add=False)

    def __str__(self):
        return u"%s - %s" % (self.tutor.person, self.function)


def find_by_id(an_id):
    return Attribution.objects.get(pk=an_id)


def search(tutor=None, learning_unit_year=None):
    queryset = Attribution.objects

    if tutor:
        queryset = queryset.filter(tutor=tutor)

    if learning_unit_year:
        queryset = queryset.filter(learning_unit_year=learning_unit_year)

    return queryset.select_related('tutor', 'learning_unit_year')


def find_by_tutor_year(tutor=None, an_academic_year=None):
    queryset = Attribution.objects

    if tutor:
        queryset = queryset.filter(tutor=tutor)

    if an_academic_year:
        queryset = queryset.filter(learning_unit_year__academic_year=an_academic_year)

    return queryset.select_related('tutor', 'learning_unit_year')


def find_by_tutor_year_order_by_acronym_fonction(tutor=None, an_academic_year=None):
    results = find_by_tutor_year(tutor,an_academic_year )
    return results.order_by('learning_unit_year__acronym', 'function')


def find_distinct_years(a_tutor):
    return Attribution.objects.filter(tutor=a_tutor).order_by('-learning_unit_year__academic_year__year')\
        .values_list('learning_unit_year__academic_year__year',flat=True).distinct()


def find_by_tutor_dates(a_tutor, a_start_date, an_end_date):
    return Attribution.objects.filter(end_date=an_end_date, tutor=a_tutor)
