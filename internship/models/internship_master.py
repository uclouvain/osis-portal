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
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from osis_common.models.serializable_model import SerializableModelAdmin, SerializableModel


class InternshipMasterAdmin(SerializableModelAdmin):
    list_display = ('reference', 'organization', 'first_name', 'last_name', 'civility', 'type_mastery', 'speciality')
    fieldsets = ((None, {'fields': ('reference', 'organization', 'first_name', 'last_name', 'civility', 'type_mastery',
                                    'speciality')}),)
    raw_id_fields = ('organization',)


class InternshipMaster(SerializableModel):
    CIVILITY_CHOICE = (('PROFESSOR', _('PROFESSOR')),
                       ('DOCTOR', _('DOCTOR')))
    TYPE_CHOICE = (('SPECIALIST', _('SPECIALIST')),
                   ('GENERALIST', _('GENERALIST')))

    organization = models.ForeignKey('internship.Organization', null=True)
    first_name = models.CharField(max_length=50, blank=True, null=True, db_index=True)
    last_name = models.CharField(max_length=50, blank=True, null=True, db_index=True)
    reference = models.CharField(max_length=50, blank=True, null=True)
    civility = models.CharField(max_length=50, blank=True, null=True, choices=CIVILITY_CHOICE)
    type_mastery = models.CharField(max_length=50, blank=True, null=True, choices=TYPE_CHOICE)
    speciality = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return u"%s" % self.reference


def search(name="", speciality="", organization=None):
    query = InternshipMaster.objects
    has_criteria = False
    if name:
        query = query.filter(Q(first_name__contains=name) | Q(last_name__contains=name))
        has_criteria = True

    if speciality:
        query = query.filter(speciality=speciality)
        has_criteria = True

    if organization:
        query = query.filter(organization=organization)
        has_criteria = True

    if has_criteria:
        return query
    else:
        return None


def get_all_specialities():
    return list(InternshipMaster.objects.values_list('speciality', flat=True).distinct('speciality').
                order_by('speciality'))


