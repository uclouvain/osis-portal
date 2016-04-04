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
import uuid
from uuid import UUID
from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist


class PersonAdmin(admin.ModelAdmin):
    list_display = ['user']
    fieldsets = ((None, {'fields': ['user']}),)


class Person(models.Model):
    activation_code = models.UUIDField(default=uuid.uuid4, editable=False, blank=True, null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return u"%s" % (self.user)


def find_by_user(user):
    try:
        person_result = Person.objects.filter(user__id=user.id).first()
    except ObjectDoesNotExist:
        return None
    return person_result


def find_by_activation_code(activation_code):
    if is_uuid4(activation_code):
        try:
            return Person.objects.filter(activation_code=activation_code).first()
        except ObjectDoesNotExist:
            return None
    else:
        return None


def is_uuid4(activ_code):
    """
    Validate that a UUID string is in fact a valid uuid4. Happily, the uuid module does the actual checking for us.
    It is vital that the 'version' kwarg be passed to the UUID() call, otherwise any 32-character hex string is
    considered valid.
    """
    try:
        UUID(activ_code, version=4)
    except ValueError:
        # If it's a value error, then the string
        # is not a valid hex code for a UUID.
        return False
    return True


def find_by_id(id):
    try:
        return Person.objects.get(pk=id)
    except ObjectDoesNotExist:
        return None
