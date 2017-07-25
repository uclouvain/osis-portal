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
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import Group
from base.models import person as model_person
from osis_common.models.serializable_model import SerializableModel, SerializableModelAdmin

logger = logging.getLogger(settings.DEFAULT_LOGGER)


class StudentAdmin(SerializableModelAdmin):
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
            self.message_user(request, "{} users added to the group '{}'.".format(count, group_name), level=messages.SUCCESS)
        except Group.DoesNotExist:
            self.message_user(request, "Group {} doesn't exist.".format(group_name), level=messages.ERROR)


class Student(SerializableModel):
    registration_id = models.CharField(max_length=10, unique=True)
    person = models.ForeignKey('Person')

    def email(self):
        if self.person.user:
            return self.person.user.email
        else:
            return self.person.email

    def __str__(self):
        return u"%s (%s)" % (self.person, self.registration_id)


def find_by_registration_id(registration_id):
    try:
        return Student.objects.get(registration_id=registration_id)
    except ObjectDoesNotExist:
        return None


def search(registration_id=None, person_name=None, person_username=None, person_first_name=None, full_registration=None):
    """
    Search students by optional arguments. At least one argument should be informed
    otherwise it returns empty.
    """
    has_criteria = False
    queryset = Student.objects

    if registration_id:
        if full_registration:
            queryset = queryset.filter(registration_id=registration_id)
        else:
            queryset = queryset.filter(registration_id__icontains=registration_id)
        has_criteria = True

    if person_name:
        queryset = queryset.filter(person__last_name__icontains=person_name)
        has_criteria = True

    if person_username:
        queryset = queryset.filter(person__user=person_username)
        has_criteria = True

    if person_first_name:
        queryset = queryset.filter(person__first_name__icontains=person_first_name)
        has_criteria = True

    if has_criteria:
        return queryset
    else:
        return None


def find_by_person(a_person):
    try:
        student = Student.objects.get(person=a_person)
        return student
    except ObjectDoesNotExist:
        return None


def find_by_user(a_user):
    person = model_person.find_by_user(a_user)
    return find_by_person(person)


def is_student(a_user):
    if find_by_user(a_user):
        return True
    return False
