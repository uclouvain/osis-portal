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
import logging

from django.conf import settings
from django.db import models

from osis_common.models.serializable_model import SerializableModel, SerializableModelAdmin
from osis_common.utils.models import get_object_or_none

logger = logging.getLogger(settings.DEFAULT_LOGGER)


class TutorAdmin(SerializableModelAdmin):
    list_display = ('external_id', 'person', 'changed')
    fieldsets = ((None, {'fields': ('external_id', 'person',)}),)
    raw_id_fields = ('person',)
    search_fields = ['person__first_name', 'person__last_name']


class Tutor(SerializableModel):
    external_id = models.CharField(max_length=100, blank=True, null=True)
    changed = models.DateTimeField(null=True)
    person = models.OneToOneField('Person', on_delete=models.CASCADE)

    class Meta:
        permissions = (
            ("can_access_attribution_application", "Can access attribution application"),
            ("can_access_attribution", "Can access attribution"),
        )

    def __str__(self):
        return f"{self.person}"


def find_by_person(a_person):
    return get_object_or_none(
        Tutor,
        person=a_person
    )


def find_by_person_global_id(global_id):
    return get_object_or_none(
        Tutor,
        person__global_id=global_id
    ) if global_id is not None else None


def find_by_id(tutor_id):
    return get_object_or_none(
        Tutor.objects.select_related('person'),
        pk=tutor_id,
    )
