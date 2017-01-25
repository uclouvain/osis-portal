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
from base.models.enums import component_type
from osis_common.models.serializable_model import SerializableModel
from django.core.exceptions import ObjectDoesNotExist


class LearningUnitComponentAdmin(admin.ModelAdmin):
    list_display = ('learning_unit_year', 'type', 'duration')
    fieldsets = ((None, {'fields': ('learning_unit_year', 'type', 'duration')}),)
    raw_id_fields = ('learning_unit_year', )
    search_fields = ['learning_unit_year__acronym']


class LearningUnitComponent(SerializableModel):
    external_id = models.CharField(max_length=100, blank=True, null=True)
    learning_unit_year = models.ForeignKey('LearningUnitYear')
    type = models.CharField(max_length=25, blank=True, null=True, choices=component_type.COMPONENT_TYPES, db_index=True)
    duration = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return u"%s - %s" % (self.type, self.learning_unit_year)

    class Meta:
        permissions = (
            ("can_access_learningunit", "Can access learning unit"),
        )


def search(a_learning_unit_year=None, a_type=None):
    queryset = LearningUnitComponent.objects

    if a_learning_unit_year:
        queryset = queryset.filter(learning_unit_year=a_learning_unit_year)

    if a_type:
        queryset = queryset.filter(type=a_type)
    return queryset


def find_by_learning_year_type(a_learning_unit_year=None, a_type=None):
    if a_learning_unit_year and a_type:
        try:
            return LearningUnitComponent.objects.get(learning_unit_year=a_learning_unit_year,
                                                     type=a_type)
        except ObjectDoesNotExist:
            return None
    return None



