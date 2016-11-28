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
from django.db import models
from django.contrib import admin
from osis_common.models.serializable_model import SerializableModel


class EducationTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'adhoc')


class EducationType(SerializableModel):
    EDUCATION_TYPE = (('TRANSITION','Transition'),
            ('QUALIFICATION','Qualification'),
            ('ANOTHER', 'Autre'))

    external_id = models.CharField(max_length=100, blank=True, null=True)
    type = models.CharField(max_length=20, choices=EDUCATION_TYPE)
    name = models.CharField(max_length=100)
    adhoc = models.BooleanField(default=False)

    def __str__(self):
        return self.name


def find_by_id(an_id):
    return EducationType.objects.get(pk=an_id)


def find_education_type_by_adhoc(a_type, an_adhoc_type):
    return EducationType.objects.filter(type=a_type, adhoc=an_adhoc_type).order_by('name')


def find_by_name(a_name):
    return EducationType.objects.filter(name=a_name, adhoc=True).first()