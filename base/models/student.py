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
from django.contrib import messages
from django.contrib.auth.models import Group
from django.db import models

from base.models import person as model_person
from osis_common.models.serializable_model import SerializableModel, SerializableModelAdmin
from osis_common.utils.models import get_object_or_none

logger = logging.getLogger(settings.DEFAULT_LOGGER)


class StudentAdmin(SerializableModelAdmin):
    actions = ['add_to_group']
    list_display = ('person', 'registration_id', 'email')
    fieldsets = ((None, {'fields': ('registration_id', 'person')}),)
    raw_id_fields = ('person', )
    search_fields = ['person__first_name', 'person__last_name', 'registration_id']
    
    def add_to_group(self, request, queryset):
        group_name = "students"
        try:
            group = Group.objects.get(name=group_name)
            count = 0
            for student in queryset:
                user = student.person.user
                if user and not user.groups.filter(name=group_name).exists():
                    user.groups.add(group)
                    count += 1
            self.message_user(request, f"{count} users added to the group '{group_name}'.", level=messages.SUCCESS)

        except Group.DoesNotExist:
            self.message_user(request, f"Group {group_name} doesn't exist.", level=messages.ERROR)


class Student(SerializableModel):
    registration_id = models.CharField(max_length=10, unique=True)
    person = models.ForeignKey('Person', on_delete=models.PROTECT)

    def email(self):
        return self.person.user.email if self.person.user else self.person.email

    def __str__(self):
        return f"{self.person} ({self.registration_id})"


def find_by_registration_id(registration_id):
    return get_object_or_none(
        Student,
        registration_id=registration_id
    )


def find_by_person(a_person):
    return get_object_or_none(
        Student,
        person=a_person
    )


def find_by_user(a_user):
    person = model_person.find_by_user(a_user)
    return find_by_person(person)
