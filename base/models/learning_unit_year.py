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
    list_display = ('acronym', 'title', 'academic_year', 'weight')
    fieldsets = ((None, {'fields': ('academic_year', 'acronym', 'title', 'weight', 'team')}),)
    list_filter = ('academic_year__year',)
    search_fields = ['acronym']


class LearningUnitYear(SerializableModel):
    external_id = models.CharField(max_length=100, blank=True, null=True)
    acronym = models.CharField(max_length=15, db_index=True)
    title = models.CharField(max_length=255)
    credits = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    weight = models.IntegerField(blank=True, null=True)
    academic_year = models.ForeignKey('AcademicYear')
    team = models.BooleanField(default=False)


    def __str__(self):
        return u"%s - %s" % (self.academic_year, self.acronym)


def find_by_id(learning_unit_year_id):
    return LearningUnitYear.objects.get(pk=learning_unit_year_id)