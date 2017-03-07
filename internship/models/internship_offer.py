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
from django.core.exceptions import ObjectDoesNotExist
from osis_common.models.serializable_model import SerializableModelAdmin, SerializableModel


class InternshipOfferAdmin(SerializableModelAdmin):
    list_display = ('organization', 'speciality', 'title', 'maximum_enrollments', 'master', 'selectable')
    fieldsets = ((None, {'fields': ('organization', 'speciality', 'title', 'maximum_enrollments', 'master',
                                    'selectable')}),)
    raw_id_fields = ('organization', 'speciality')
    search_fields = ['organization__name', 'speciality__name']


class InternshipOffer(SerializableModel):
    organization = models.ForeignKey('internship.Organization')
    speciality = models.ForeignKey('internship.InternshipSpeciality', null=True)
    title = models.CharField(max_length=255)
    maximum_enrollments = models.IntegerField()
    master = models.CharField(max_length=100, blank=True, null=True)
    selectable = models.BooleanField(default=True)

    def __str__(self):
        return u"%s" % self.title

    class Meta:
        permissions = (
            ("is_internship_manager", "Is Internship Manager"),
            ("can_access_internship", "Can access internships"),
        )


def find_by_speciality(speciality):
    return InternshipOffer.objects.filter(speciality=speciality)


def find_by_pk(a_pk):
    try:
        return InternshipOffer.objects.get(pk=a_pk)
    except ObjectDoesNotExist:
        return None

