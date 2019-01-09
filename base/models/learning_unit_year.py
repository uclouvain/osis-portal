##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2018 Université catholique de Louvain (http://www.uclouvain.be)
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

from base.models.enums import learning_unit_year_subtypes
from osis_common.models.serializable_model import SerializableModel, SerializableModelAdmin


class LearningUnitYearAdmin(SerializableModelAdmin):
    list_display = ('acronym', 'specific_title', 'academic_year', 'weight', 'learning_unit', )
    fieldsets = ((None, {'fields': ('academic_year', 'acronym', 'specific_title', 'weight', 'learning_unit',
                 'learning_container_year', 'subtype')}),)
    list_filter = ('academic_year__year', 'subtype',)
    search_fields = ['acronym']
    raw_id_fields = ('learning_unit', 'learning_container_year')


class LearningUnitYear(SerializableModel):
    external_id = models.CharField(max_length=100, blank=True, null=True)
    acronym = models.CharField(max_length=15, db_index=True)
    specific_title = models.CharField(max_length=255, blank=True, null=True)
    credits = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    weight = models.IntegerField(blank=True, null=True)
    academic_year = models.ForeignKey('AcademicYear')
    learning_container_year = models.ForeignKey('LearningContainerYear', blank=True, null=True)
    learning_unit = models.ForeignKey('LearningUnit', blank=True, null=True)
    subtype = models.CharField(max_length=50, blank=True, null=True,
                               choices=learning_unit_year_subtypes.LEARNING_UNIT_YEAR_SUBTYPES)

    class Meta:
        unique_together = (('learning_unit', 'academic_year'), ('acronym', 'academic_year'))

    def __str__(self):
        return u"%s - %s" % (self.academic_year, self.acronym)

    @property
    def in_charge(self):
        return self.learning_container_year and self.learning_container_year.in_charge

    @property
    def vacant(self):
        return self.learning_container_year and self.learning_container_year.is_vacant

    @property
    def team(self):
        return self.learning_container_year and self.learning_container_year.team

    @property
    def complete_title(self):
        return ' '.join(filter(None, [self.learning_container_year.common_title, self.specific_title]))


def search(academic_year_id=None, acronym=None, learning_container_year_id=None, a_learning_unit=None):
    queryset = LearningUnitYear.objects

    if academic_year_id:
        queryset = queryset.filter(academic_year=academic_year_id)

    if acronym:
        queryset = queryset.filter(acronym__icontains=acronym)

    if learning_container_year_id is not None:
        if isinstance(learning_container_year_id, list):
            queryset = queryset.filter(learning_container_year__in=learning_container_year_id)
        elif learning_container_year_id:
            queryset = queryset.filter(learning_container_year=learning_container_year_id)

    if a_learning_unit:
        queryset = queryset.filter(learning_unit=a_learning_unit)

    return queryset


def search_order_by_acronym(academic_year_id=None):
    return search(academic_year_id).order_by('acronym')


def find_by_id(learning_unit_year_id):
    return LearningUnitYear.objects.select_related("academic_year",
                                                   "learning_unit")\
        .get(pk=learning_unit_year_id)


def find_first(an_academic_year=None, a_learning_unit=None):
    return LearningUnitYear.objects.filter(academic_year=an_academic_year, learning_unit=a_learning_unit).first()


def find_by_acronym(acronym, academic_year):
    return LearningUnitYear.objects.select_related("academic_year",
                                                   "learning_unit").\
        filter(acronym__startswith=acronym, academic_year=academic_year)


def find_by_learning_container_year(learning_container_yr_id):
    return LearningUnitYear.objects.filter(learning_container_year=learning_container_yr_id)


def find_first_by_learning_container_year(learning_container_yr_id):
    return find_by_learning_container_year(learning_container_yr_id).first()


def find_first_by_exact_acronym(academic_year_id, acronym):
    return search(academic_year_id, acronym, None, None).first()


def get_full_by_learning_container_year_id(learning_container_year_id):
    return LearningUnitYear.objects.get(learning_container_year__id=learning_container_year_id,
                                        subtype=learning_unit_year_subtypes.FULL)


def find_by_learning_container_yr_and_subtype(learning_container_yr_id, a_subtype):
    return LearningUnitYear.objects.filter(learning_container_year=learning_container_yr_id, subtype=a_subtype)
