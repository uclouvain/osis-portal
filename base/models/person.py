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
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

from osis_common.models.serializable_model import SerializableModel, SerializableModelAdmin

logger = logging.getLogger(settings.DEFAULT_LOGGER)


class PersonAdmin(SerializableModelAdmin):
    list_display = ('first_name', 'middle_name', 'last_name', 'username', 'email', 'gender', 'global_id',
                    'changed')
    search_fields = ['first_name', 'middle_name', 'last_name', 'user__username', 'email', 'global_id']
    fieldsets = ((None, {'fields': ('user', 'global_id', 'gender', 'first_name', 'middle_name',
                                    'last_name', 'email', 'phone', 'phone_mobile', 'language')}),)
    raw_id_fields = ('user',)


class Person(SerializableModel):
    GENDER_CHOICES = (
        ('F', _('Female')),
        ('H', _('Male')),
        ('X', _('Other')))

    external_id = models.CharField(max_length=100, blank=True, default='')
    changed = models.DateTimeField(null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    global_id = models.CharField(max_length=10, blank=True, null=True, db_index=True, unique=True)
    gender = models.CharField(max_length=1, blank=True, choices=GENDER_CHOICES, default='')
    first_name = models.CharField(max_length=50, blank=True, default='', db_index=True)
    middle_name = models.CharField(max_length=50, blank=True, default='')
    last_name = models.CharField(max_length=50, blank=True, default='', db_index=True)
    email = models.EmailField(max_length=255, default='')
    phone = models.CharField(max_length=30, blank=True, default='')
    phone_mobile = models.CharField(max_length=30, blank=True, default='')
    language = models.CharField(max_length=30, choices=settings.LANGUAGES, default=settings.LANGUAGE_CODE)
    birth_date = models.DateField(blank=True, null=True)

    def username(self):
        return None if self.user is None else self.user.username

    def __str__(self):
        first_name = self.first_name or ""
        last_name = f"{self.last_name}," if self.last_name else ""
        return f"{last_name.upper()} {first_name}"

    class Meta:
        permissions = (
            ("is_tutor", "Is tutor"),
            ("is_student", "Is student"),
            ("is_administrator", "Is administrator"),
            ("is_internship_master", "Is internship master"),
            ("is_faculty_administrator", "Is faculty administrator"),
            ("can_access_administration", "Can access administration"),
            # temporary pass internship perm before internship configuration endpoint is available
            ("can_access_internship", "Can access internship"),
        )


def find_by_user(user):
    return Person.objects.filter(user=user).first()


def change_language(user, new_language):
    languages_supported = [x[0] for x in settings.LANGUAGES]
    if new_language and new_language in languages_supported:
        person = Person.objects.get(user=user)
        person.language = new_language
        person.save()


def find_by_global_id(global_id):
    return Person.objects.filter(global_id=global_id).first() if global_id else None
