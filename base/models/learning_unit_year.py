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


class LearningUnitYearAdmin(admin.ModelAdmin):
    list_display = ('acronym', 'title', 'academic_year', 'weight', 'learning_unit', 'vacant')
    fieldsets = ((None, {'fields': ('academic_year', 'acronym', 'title', 'weight', 'learning_unit', 'team', 'vacant',
                                    'in_charge')}),)
    list_filter = ('academic_year__year', 'vacant')
    search_fields = ['acronym']


class LearningUnitYear(SerializableModel):
    external_id = models.CharField(max_length=100, blank=True, null=True)
    acronym = models.CharField(max_length=15, db_index=True)
    title = models.CharField(max_length=255)
    credits = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    weight = models.IntegerField(blank=True, null=True)
    academic_year = models.ForeignKey('AcademicYear')
    learning_unit = models.ForeignKey('LearningUnit', blank=True, null=True)
    team = models.BooleanField(default=False)
    vacant = models.BooleanField(default=False)
    in_charge = models.BooleanField(default=False)

    def __str__(self):
        return u"%s - %s" % (self.academic_year, self.acronym)


def search(academic_year_id=None, acronym=None, a_learning_unit=None, title=None):
    queryset = LearningUnitYear.objects

    if academic_year_id:
        queryset = queryset.filter(academic_year=academic_year_id)

    if acronym:
        queryset = queryset.filter(acronym__iexact=acronym)

    if a_learning_unit:
        queryset = queryset.filter(learning_unit=a_learning_unit)

    return queryset

def search_order_by_acronym(academic_year_id=None):
    return search(academic_year_id).order_by('acronym')


def find_by_id(learning_unit_year_id):
    return LearningUnitYear.objects.get(pk=learning_unit_year_id)


def find_first(an_academic_year=None, a_learning_unit=None):
    return LearningUnitYear.objects.filter(academic_year=an_academic_year, learning_unit=a_learning_unit).first()