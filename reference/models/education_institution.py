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
from reference.models import country
from reference.enums import education_institution_type, education_institution_national_comunity as nat_community
from base.models.serializable_model import SerializableModel


class EducationInstitutionAdmin(admin.ModelAdmin):
    list_display = ('name', 'institution_type', 'country', 'adhoc')


class EducationInstitution(SerializableModel):
    name = models.CharField(max_length=100)
    institution_type = models.CharField(max_length=25, choices=education_institution_type.INSTITUTION_TYPES)
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=255)
    country = models.ForeignKey('reference.Country', blank=True, null=True)
    national_community = models.CharField(max_length=20, choices=nat_community.NATIONAL_COMMUNITY_TYPES, blank=True, null=True)
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


def find_countries():
    return EducationInstitution.objects.filter(country__isnull=False).exclude(country__iso_code="BE").distinct('country')


def find_by_country(a_country):
    return EducationInstitution.objects.filter(country=a_country).distinct('city').order_by('city')


def find_by_city(a_city):
    return EducationInstitution.objects.filter(city=a_city).order_by('name')


def find_by_country_city_name(a_country, a_city, a_name):
    return EducationInstitution.objects.filter(country=a_country, city=a_city, name=a_name, adhoc=False).first()


def find_by_institution_type_iso_code(an_institution_type, iso_code,an_adhoc):
    return EducationInstitution.objects.filter(adhoc=an_adhoc,
                                               institution_type=an_institution_type,
                                               country__iso_code=iso_code)


def find_by_isocode_type(an_iso_code, an_institution_type, an_adhoc):
    return EducationInstitution.objects.filter(country__iso_code=an_iso_code,
                                               institution_type=an_institution_type,
                                               adhoc=an_adhoc).distinct('city').order_by('city')


def find_by_institution_city_type_iso_code(a_city, an_institution_type, iso_code, an_adhoc):
    return EducationInstitution.objects.filter(city=a_city,
                                               adhoc=an_adhoc,
                                               institution_type=an_institution_type,
                                               country__iso_code=iso_code).order_by('name')


def find_by_city_isocode(a_city, iso_code):
    return EducationInstitution.objects.filter(city=a_city, country__iso_code=iso_code).order_by('name')


def find_by_not_isocode_type(an_iso_code, an_institution_type, an_adhoc):
    return EducationInstitution.objects.filter(institution_type=an_institution_type, adhoc=an_adhoc)\
        .exclude(country__iso_code=an_iso_code).distinct('city').order_by('city')


def find_by_institution_type_not_isocode(an_institution_type, iso_code, an_adhoc):
    return EducationInstitution.objects.filter(adhoc=an_adhoc, institution_type=an_institution_type)\
        .exclude(country__iso_code=iso_code)


def find_countries_by_type_excluding_country(an_institution_type, an_adhoc, iso_code_excluded):
    return EducationInstitution.objects.all().filter(institution_type=an_institution_type, adhoc=an_adhoc)\
        .exclude(country__iso_code=iso_code_excluded).distinct('country')


def find_by_city_not_isocode(a_city, iso_code, a_type):
    return EducationInstitution.objects.filter(city=a_city, adhoc=False, institution_type=a_type)\
        .exclude(country__iso_code=iso_code).order_by('name')


def find_education_institution_by_adhoc_type_not_isocode(adhoc_type, a_type, an_iso_code):
    return EducationInstitution.objects.filter(adhoc=adhoc_type, institution_type=a_type)\
        .exclude(country__iso_code=an_iso_code).order_by('name')


def find_education_institution_by_country_adhoc_type(a_country_id, adhoc_type, a_type):
    a_country = country.find_by_id(a_country_id)
    return EducationInstitution.objects\
        .filter(adhoc=adhoc_type, institution_type=a_type, country__iso_code=a_country.iso_code).order_by('name')


def find_by_city_country(a_city, a_country):
    return EducationInstitution.objects.filter(city=a_city, country=a_country).order_by('name')


def find_cities_by_type_excluding_country(an_institution_type, an_adhoc, iso_code_excluded):
    return EducationInstitution.objects.all().filter(institution_type=an_institution_type, adhoc=an_adhoc)\
        .exclude(country__iso_code=iso_code_excluded).distinct('city')


def find_one_by_city(a_city):
    return EducationInstitution.objects.filter(city=a_city).first()


def find_postal_codes_by_isocode_type(an_iso_code, an_institution_type, an_adhoc):
    return EducationInstitution.objects.filter(country__iso_code=an_iso_code,
                                               institution_type=an_institution_type,
                                               adhoc=an_adhoc).distinct('postal_code').order_by('postal_code')


def find_by_institution_postal_code_type_iso_code(a_postal_code, an_institution_type, iso_code, an_adhoc):
    return EducationInstitution.objects.filter(postal_code=a_postal_code,
                                               adhoc=an_adhoc,
                                               institution_type=an_institution_type,
                                               country__iso_code=iso_code).order_by('name')


def search(an_iso_code=None, an_institution_type=None, an_adhoc=None, a_city=None, a_postal_code=None):
    out = None
    queryset = EducationInstitution.objects.order_by('name')
    if an_iso_code:
        queryset = queryset.filter(country__iso_code=an_iso_code)
    if an_institution_type:
        queryset = queryset.filter(institution_type=an_institution_type)
    if an_adhoc is not None:
        queryset = queryset.filter(adhoc=False)
    if a_city:
        queryset = queryset.filter(city=a_city)
    if a_postal_code:
        queryset = queryset.filter(postal_code=a_postal_code)
    if an_iso_code or an_institution_type or an_adhoc or a_city or a_postal_code:
        out = queryset.order_by('name')
    return out


def find_cities(an_iso_code=None, an_institution_type=None, an_adhoc=None,  a_postal_code=None):
    return EducationInstitution.objects.filter(country__iso_code=an_iso_code,
                                               institution_type=an_institution_type,
                                               adhoc=an_adhoc,
                                               postal_code=a_postal_code).distinct('city').order_by('city')