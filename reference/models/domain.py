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

from reference.enums import domain_type
from osis_common.models.serializable_model import SerializableModel
from . import decree


class DomainAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'decree', 'type')
    fieldsets = ((None, {'fields': ('name', 'parent', 'decree', 'type')}),)
    search_fields = ['name']


class Domain(SerializableModel):
    external_id = models.CharField(max_length=100, blank=True, null=True)
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', null=True, blank=True)
    decree = models.ForeignKey('Decree', null=True, blank=True)
    type = models.CharField(max_length=50, choices=domain_type.TYPES, default=domain_type.UNKNOWN)
    national = models.BooleanField(default=False) # True if is Belgian else False
    reference = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return self.name

    @property
    def sub_domains(self):
        """
        To find children
        """
        return Domain.objects.filter(parent=self)


def find_by_id(an_id):
    return Domain.objects.get(pk=an_id)


def find_current_domains():
    current_decree = decree.find_current_decree()
    return Domain.objects.filter(decree=current_decree)\
                         .filter(type=domain_type.UNIVERSITY)\
                         .filter(parent__isnull=True)\
                         .order_by("name")


def find_all_subdomains():
    return Domain.objects.exclude(parent=None)


def find_subdomains_by_domain_id(a_domain_id):
    return Domain.objects.filter(parent=a_domain_id)


