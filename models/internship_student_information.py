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
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.translation import gettext_lazy as _

from internship.services.internship import InternshipAPIService
from osis_common.models.serializable_model import SerializableModelAdmin, SerializableModel


class InternshipStudentInformationAdmin(SerializableModelAdmin):
    list_display = (
        'person', 'location', 'postal_code', 'city', 'country', 'email', 'phone_mobile', 'contest', 'cohort'
    )
    fieldsets = ((None, {
        'fields': ('person', 'location', 'postal_code', 'city', 'country', 'email', 'phone_mobile',
                   'contest', 'cohort')
    }),)
    raw_id_fields = ('person', 'cohort')
    list_filter = ['cohort']
    search_fields = ['person__user__username', 'person__last_name', 'person__first_name']


class InternshipStudentInformation(SerializableModel):
    TYPE_CHOICE = (('SPECIALIST', _('Specialist')),
                   ('GENERALIST', _('Generalist')))
    person = models.ForeignKey('base.Person', on_delete=models.PROTECT)
    location = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, blank=True, null=True)
    phone_mobile = models.CharField(max_length=100, blank=True, null=True)
    contest = models.CharField(max_length=124, choices=TYPE_CHOICE, null=True, blank=True)
    cohort = models.ForeignKey('internship.Cohort', on_delete=models.CASCADE)

    def __str__(self):
        return u"%s" % self.person


def find_by_user_in_cohort(user, cohort):
    try:
        return InternshipStudentInformation.objects.get(person__user=user, cohort=cohort)
    except ObjectDoesNotExist:
        return None


def find_by_person_in_cohort(cohort_id, person):
    return InternshipAPIService.get_internship_student_information_by_person_and_cohort(
        cohort_name=cohort_id, person=person
    )
    # return InternshipStudentInformation.objects.filter(cohort_id=cohort_id, person_id=person_id)


def find_by_person(person):
    return InternshipStudentInformation.objects.filter(person=person)


def exists_by_person(person):
    return InternshipStudentInformation.objects.filter(person=person).exists()
