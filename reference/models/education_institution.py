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


class EducationInstitutionAdmin(admin.ModelAdmin):
    list_display = ('name', 'adhoc')


class EducationInstitution(models.Model):
    INSTITUTION_TYPE = (('SECONDARY', 'Secondaire'),
                        ('UNIVERSITY', 'University'))

    NATIONAL_COMMUNITY_TYPES = (
        ('FRENCH', 'Communauté française de Belgique'),
        ('GERMAN', 'Communauté germanophone'),
        ('DUTCH', 'Communauté flamande'),
        )
    name = models.CharField(max_length=100)
    institution_type = models.CharField(max_length=20, choices=INSTITUTION_TYPE)
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=255)
    country = models.ForeignKey('reference.Country', blank=True, null=True)
    national_community = models.CharField(max_length=20, choices=NATIONAL_COMMUNITY_TYPES, blank=True, null=True)
    adhoc = models.BooleanField(default=False)

    def __str__(self):
        return self.name


def find_by_id(an_education_institution_id):
    return EducationInstitution.objects.get(pk=an_education_institution_id)


def find_education_institution_by_adhoc(adhoc_type):
    return EducationInstitution.objects.filter(adhoc=adhoc_type).order_by('name')


def find_by_name_city_postal_code(a_name, a_city, a_postal_code, a_national_community):
    return EducationInstitution.objects.filter(adhoc=True,
                                               name__iexact=a_name,
                                               city__iexact=a_city,
                                               postal_code__iexact=a_postal_code,
                                               national_community=a_national_community).first()


def find_by_institution_type(an_institution_type, an_adhoc):
    return EducationInstitution.objects.filter(adhoc=an_adhoc,
                                               institution_type=an_institution_type)


def find_by_institution_type_national_community(an_institution_type, a_national_community, an_adhoc):
    return EducationInstitution.objects.filter(adhoc=an_adhoc,
                                               institution_type=an_institution_type,
                                               national_community=a_national_community)
