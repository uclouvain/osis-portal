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
from osis_common.models.serializable_model import SerializableModelAdmin, SerializableModel
from django.db import models


class OrganizationAdmin(SerializableModelAdmin):
    list_display = ('name', 'acronym', 'reference', 'type', 'cohort')
    fieldsets = ((None, {'fields': ('name', 'acronym', 'reference', 'website', 'type')}),)
    search_fields = ['acronym', 'name']


class Organization(SerializableModel):
    name = models.CharField(max_length=255)
    cohort = models.ForeignKey('internship.Cohort', null=False)
    acronym = models.CharField(max_length=15, blank=True)
    website = models.URLField(max_length=255, blank=True, null=True)
    reference = models.CharField(max_length=30, blank=True, null=True)
    type = models.CharField(max_length=30, blank=True, null=True, default="service partner")

    def __str__(self):
        return u"%s" % self.name

    def save(self, *args, **kwargs):
        self.acronym = self.name[:14]
        super(Organization, self).save(*args, **kwargs)


def search(name):
    return Organization.objects.filter(name__contains=name)
