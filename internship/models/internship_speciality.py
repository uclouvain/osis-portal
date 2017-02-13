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
from django.contrib import admin
from django.db import models


class InternshipSpecialityAdmin(admin.ModelAdmin):
    list_display = ('learning_unit', 'name', 'acronym', 'mandatory', 'order_postion')
    fieldsets = ((None, {'fields': ('learning_unit', 'name', 'acronym', 'mandatory', 'order_postion')}),)
    raw_id_fields = ('learning_unit',)


class InternshipSpeciality(models.Model):
    learning_unit = models.ForeignKey('base.LearningUnit')
    name = models.CharField(max_length=125, blank=False, null=False)
    acronym = models.CharField(max_length=125, blank=False, null=False)
    mandatory = models.BooleanField(default=False)
    order_postion = models.IntegerField(default=0)

    def __str__(self):
        return self.name


def search(**kwargs):
    kwargs = {k: v for k, v in kwargs.items() if v}
    return InternshipSpeciality.objects.filter(**kwargs).select_related("learning_unit").order_by('acronym', 'name')


def search_order_by_position(**kwargs):
    kwargs = {k: v for k, v in kwargs.items() if v}
    return InternshipSpeciality.objects.filter(**kwargs).select_related("learning_unit").order_by('order_postion')


def find_all():
    return InternshipSpeciality.objects.all().select_related("learning_unit").order_by('acronym', 'name')


def find_by_id(speciality_id):
    return InternshipSpeciality.objects.get(pk=speciality_id)


def find_non_mandatory():
    return InternshipSpeciality.objects.filter(mandatory=False)\
                                       .select_related("learning_unit")\
                                       .order_by('acronym', 'name')
