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


class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'iso_code', 'nationality', 'european_union', 'dialing_code', 'cref_code')
    fieldsets = ((None, {'fields': ('iso_code', 'name', 'nationality', 'european_union', 'dialing_code', 'cref_code')}),)
    ordering = ('name',)
    search_fields = ['name']


class Country(models.Model):
    iso_code = models.CharField(max_length=2, unique=True)
    name = models.CharField(max_length=80, unique=True)
    nationality = models.CharField(max_length=80, blank=True, null=True)
    european_union = models.BooleanField(default=False)
    dialing_code = models.CharField(max_length=3, blank=True, null=True)
    cref_code = models.CharField(max_length=3, blank=True, null=True)

    def __str__(self):
        return self.name

    def find_countries():
        return Country.objects.all().order_by('name')

    def find_by_id(country_id):
        return Country.objects.get(pk=country_id)


class LanguageAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    ordering = ('code',)
    search_fields = ['code', 'name']
    fieldsets = ((None, {'fields': ('code', 'name')}),)


class Language(models.Model):
    code = models.CharField(max_length=4, unique=True)
    name = models.CharField(max_length=80, unique=True)

    def __str__(self):
        return self.name

    def find_by_id(a_language_id):
        return Language.objects.get(pk=a_language_id)


    def find_languages(self):
        return Language.objects.all().order_by('name')


    def find_languages_excepted(list):
        return Language.objects.exclude(name__in=list)
