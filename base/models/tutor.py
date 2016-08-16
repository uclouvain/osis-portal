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
from django.contrib import admin
from base.models import person as model_person

logger = logging.getLogger(settings.DEFAULT_LOGGER)


class TutorAdmin(admin.ModelAdmin):
    list_display = ('person', 'changed')
    fieldsets = ((None, {'fields': ('person',)}),)
    raw_id_fields = ('person', )
    search_fields = ['person__first_name', 'person__last_name']


class TutorManager(models.Manager):
    def get_by_natural_key(self, global_id):
        return self.get(person__global_id=global_id)


class Tutor(models.Model):

    objects = TutorManager()

    external_id = models.CharField(max_length=100, blank=True, null=True)
    changed = models.DateTimeField(null=True)
    person = models.OneToOneField('Person')

    def __str__(self):
        return u"%s" % self.person

    def save_from_osis_migration(self):
        try:
            tutor = find_by_person_global_id(self.person.global_id)
            person = model_person.find_by_global_id(self.person.global_id)
            if tutor.person.id != person.id:
                logger.info(''.join(['Update tutor with person : ', self.person.global_id]))
                tutor.person = person
                tutor.save()
        except Tutor.DoesNotExist:
            logger.info(''.join(['New Tutor with person : ', self.person.global_id]))
            person = model_person.find_by_global_id(self.person.global_id)
            self.person = person
            self.pk = None
            self.save()

    def natural_key(self):
        return (self.person.global_id, )

    natural_key.dependencies = ['base.person']

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
    return Tutor.objects.get(person__global_id=global_id)