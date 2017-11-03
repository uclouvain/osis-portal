##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2017 Université catholique de Louvain (http://www.uclouvain.be)
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
from osis_common.models.serializable_model import SerializableModel, SerializableModelAdmin
from django.db import models


class LearningContainerYearAdmin(SerializableModelAdmin):
    list_display = ('academic_year', 'acronym', 'title')
    fieldsets = ((None, {'fields': ('academic_year', 'acronym', 'title',)}),)
    search_fields = ['acronym']
    list_filter = ('academic_year',)


class LearningContainerYear(SerializableModel):
    external_id = models.CharField(max_length=100, blank=True, null=True)
    changed = models.DateTimeField(null=True, auto_now=True)
    acronym = models.CharField(max_length=10)
    academic_year = models.ForeignKey('AcademicYear')
    title = models.CharField(max_length=255)
    title_english = models.CharField(max_length=250, blank=True, null=True)

    def __str__(self):
        return u"%s - %s" % (self.acronym, self.title)


def find_by_id(id):
    try:
        return LearningContainerYear.objects.get(id=id)
    except LearningContainerYear.DoesNotExist:
        return None


def search(*args, **kwargs):
    qs = LearningContainerYear.objects.all()

    if "id" in kwargs:
        if isinstance(kwargs['id'], list):
            qs = qs.filter(id__in=kwargs['id'])
        else:
            qs = qs.filter(acronym__icontains=kwargs['id'])

    if "acronym" in kwargs:
        if isinstance(kwargs['acronym'], list):
            qs = qs.filter(acronym__in=kwargs['acronym'])
        else:
            qs = qs.filter(acronym__icontains=kwargs['acronym'])

    if "academic_year" in kwargs:
        qs = qs.filter(academic_year=kwargs['academic_year'])

    return qs
