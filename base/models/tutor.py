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
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from base.models import person as model_person
from osis_common.models.serializable_model import SerializableModel, SerializableModelAdmin

logger = logging.getLogger(settings.DEFAULT_LOGGER)


class TutorAdmin(SerializableModelAdmin):
    list_display = ('external_id', 'person', 'changed')
    fieldsets = ((None, {'fields': ('external_id','person',)}),)
    raw_id_fields = ('person', )
    search_fields = ['person__first_name', 'person__last_name']


class Tutor(SerializableModel):
    external_id = models.CharField(max_length=100, blank=True, null=True)
    changed = models.DateTimeField(null=True)
    person = models.OneToOneField('Person')

    def __str__(self):
        return u"%s" % self.person


def find_by_person(a_person):
    try:
        tutor = Tutor.objects.get(person=a_person)
        return tutor
    except ObjectDoesNotExist:
        return None


def find_by_user(a_user):
    try:
        pers = model_person.find_by_user(a_user)
        tutor = Tutor.objects.get(person=pers)
        return tutor
    except ObjectDoesNotExist:
        return None


def is_tutor(a_user):
    if find_by_user(a_user):
        return True
    return False


def find_by_person_global_id(global_id):
    try:
        return Tutor.objects.get(person__global_id=global_id) if global_id is not None else None
    except ObjectDoesNotExist:
        return None


def find_by_id(tutor_id):
    try:
        return Tutor.objects.select_related("person").get(pk=tutor_id)
    except ObjectDoesNotExist:
        return None
