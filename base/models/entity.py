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
from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Case, When, Q, F
from django.utils import timezone

from base.models.enums import entity_type
from osis_common.models.serializable_model import SerializableModel, SerializableModelAdmin


class EntityAdmin(SerializableModelAdmin):
    list_display = ('id', 'organization')
    search_fields = ['organization__acronym', 'organization__name']
    readonly_fields = ('organization',)


class Entity(SerializableModel):
    organization = models.ForeignKey('Organization', blank=True, null=True)
    changed = models.DateTimeField(null=True, auto_now=True)


    class Meta:
        verbose_name_plural = "entities"

    def __str__(self):
        return "{0} - {1}".format(self.id, self.external_id)
