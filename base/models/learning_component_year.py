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
from base.models.enums import learning_component_year_type
from django.db import models
from osis_common.models.auditable_serializable_model import AuditableSerializableModel, AuditableSerializableModelAdmin


class LearningComponentYearAdmin(AuditableSerializableModelAdmin):
    list_display = ('learning_container_year', 'acronym', 'type', 'volume_declared_vacant',)
    fieldsets = ((None, {'fields': ('learning_container_year', 'acronym', 'type', 'volume_declared_vacant',)}),)
    search_fields = ['acronym', 'learning_container_year__acronym']
    raw_id_fields = ('learning_container_year',)
    list_filter = ('learning_container_year__academic_year',)


class LearningComponentYear(AuditableSerializableModel):
    external_id = models.CharField(max_length=100, blank=True, null=True)
    changed = models.DateTimeField(null=True, auto_now=True)
    learning_container_year = models.ForeignKey('LearningContainerYear')
    acronym = models.CharField(max_length=4, blank=True, null=True)
    type = models.CharField(max_length=30, choices=learning_component_year_type.LEARNING_COMPONENT_YEAR_TYPES,
                            blank=True, null=True, db_index=True)
    volume_declared_vacant = models.DecimalField(max_digits=6, decimal_places=1, blank=True, null=True)

    def __str__(self):
        return u"%s - %s" % (self.acronym, self.learning_container_year.acronym)


def search(*args, **kwargs):
    qs = LearningComponentYear.objects.all()

    if "learning_container_year" in kwargs:
        if isinstance(kwargs['learning_container_year'], list):
            qs = qs.filter(learning_container_year__in=kwargs['learning_container_year'])
        else:
            qs = qs.filter(learning_container_year=kwargs['learning_container_year'])

    return qs.select_related('learning_container_year')\
             .order_by('learning_container_year__acronym')
