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
from base.enums.organization_type import TYPES as ORGANIZATION_TYPES


class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'acronym', 'website', 'reference', 'type')
    fieldsets = ((None, {'fields': ('name', 'acronym', 'reference', 'website', 'type')}),)
    search_fields = ['acronym']


class Organization(models.Model):
    external_id = models.CharField(max_length=100, blank=True, null=True)
    name = models.CharField(max_length=255)
    acronym = models.CharField(max_length=15)
    website = models.URLField(max_length=255, blank=True, null=True)
    reference = models.CharField(max_length=30, blank=True, null=True)
    type = models.CharField(max_length=30, blank=True, null=True, choices=ORGANIZATION_TYPES, default='UNKNOWN')

    def __str__(self):
        return self.name


def find_by_id(organization_id):
    return Organization.objects.get(pk=organization_id)


def search(acronym=None, name=None, type=None, reference=None):
    out = None
    queryset = Organization.objects

    if acronym:
        queryset = queryset.filter(acronym=acronym)

    if name:
        queryset = queryset.filter(name=name)

    if type:
        queryset = queryset.filter(type=type)

    if reference:
        queryset = queryset.filter(reference=reference)

    if acronym or name or type or reference:
        out = queryset

    return out
