##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
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

from base.models.enums import vacant_declaration_type, learning_container_type
from osis_common.models.serializable_model import SerializableModel, SerializableModelAdmin


class LearningContainerYearAdmin(SerializableModelAdmin):
    list_display = ('learning_container', 'academic_year', 'acronym', 'container_type', 'common_title')
    fieldsets = ((None, {'fields': ('learning_container', 'academic_year', 'acronym', 'container_type', 'common_title',
                                    'team', 'is_vacant', 'type_declaration_vacant', 'common_title_english')}),)
    search_fields = ['acronym']
    raw_id_fields = ('learning_container', )
    list_filter = ('academic_year', 'is_vacant',)


class LearningContainerYear(SerializableModel):
    external_id = models.CharField(max_length=100, blank=True, null=True)
    changed = models.DateTimeField(null=True, auto_now=True)
    acronym = models.CharField(max_length=10)
    academic_year = models.ForeignKey('AcademicYear', on_delete=models.PROTECT)
    learning_container = models.ForeignKey('LearningContainer', null=True, on_delete=models.PROTECT)
    container_type = models.CharField(max_length=20, choices=learning_container_type.CONTAINER_TYPE, null=True)
    common_title = models.CharField(max_length=255, blank=True, null=True)
    common_title_english = models.CharField(max_length=250, blank=True, null=True)
    team = models.BooleanField(default=False)
    is_vacant = models.BooleanField(default=False)
    type_declaration_vacant = models.CharField(max_length=100, blank=True, null=True,
                                               choices=vacant_declaration_type.DECLARATION_TYPE)

    requirement_entity = models.ForeignKey(
        to="base.Entity",
        null=True, blank=False,
        related_name='requirement_entities',
        on_delete=models.PROTECT,
    )
    allocation_entity = models.ForeignKey(
        to="base.Entity",
        null=True, blank=True,
        related_name='allocation_entities',
        on_delete=models.PROTECT,
    )
    additional_entity_1 = models.ForeignKey(
        to="base.Entity",
        null=True, blank=True,
        related_name='additional_entities_1',
        on_delete=models.PROTECT,
    )
    additional_entity_2 = models.ForeignKey(
        to="base.Entity",
        null=True, blank=True,
        related_name='additional_entities_2',
        on_delete=models.PROTECT,
    )

    @property
    def in_charge(self):
        return self.container_type and self.container_type in learning_container_type.IN_CHARGE_TYPES

    def __str__(self):
        return u"%s - %s" % (self.acronym, self.common_title)


def find_by_id(id):
    try:
        return LearningContainerYear.objects.get(id=id)
    except LearningContainerYear.DoesNotExist:
        return None


def find_by_acronym(acronym, academic_year=None):
    qs = LearningContainerYear.objects.filter(acronym=acronym)
    if academic_year:
        qs = qs.filter(academic_year=academic_year)
    return qs.select_related('academic_year')


# TODO :: remove this function and use querysets in Class based views
def search(*args, **kwargs):
    qs = LearningContainerYear.objects.all()

    if "id" in kwargs:
        if isinstance(kwargs['id'], list):
            qs = qs.filter(id__in=kwargs['id'])
        else:
            qs = qs.filter(id=kwargs['id'])

    if "acronym" in kwargs:
        if isinstance(kwargs['acronym'], list):
            qs = qs.filter(acronym__in=kwargs['acronym'])
        else:
            qs = qs.filter(acronym__icontains=kwargs['acronym'])

    if "academic_year" in kwargs:
        qs = qs.filter(academic_year=kwargs['academic_year'])

    return qs.select_related('academic_year')
