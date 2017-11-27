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
from django.db import models
from django.db.models import Prefetch

from base.models.enums import entity_container_year_link_type
from osis_common.models.auditable_serializable_model import AuditableSerializableModel, AuditableSerializableModelAdmin


class EntityContainerYearAdmin(AuditableSerializableModelAdmin):
    list_display = ('external_id', 'learning_container_year', 'entity', 'type')
    fieldsets = ((None, {'fields': ('entity', 'learning_container_year', 'type')}),)
    search_fields = ['learning_container_year__acronym', 'type']
    list_filter = ('learning_container_year__academic_year',)
    raw_id_fields = ('entity', 'learning_container_year')


class EntityContainerYear(AuditableSerializableModel):
    external_id = models.CharField(max_length=255, blank=True, null=True)
    changed = models.DateTimeField(null=True, auto_now=True)
    entity = models.ForeignKey('Entity')
    learning_container_year = models.ForeignKey('LearningContainerYear')
    type = models.CharField(max_length=35, choices=entity_container_year_link_type.ENTITY_CONTAINER_YEAR_LINK_TYPES)

    class Meta:
        unique_together = ('entity', 'learning_container_year', 'type',)

    def __str__(self):
        return u"%s - %s - %s" % (self.entity, self.learning_container_year, self.type)
