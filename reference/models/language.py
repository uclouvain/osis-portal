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


class LanguageAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'recognized')
    ordering = ('code',)
    search_fields = ['code', 'name']
    fieldsets = ((None, {'fields': ('code', 'name', 'recognized')}),)


class Language(models.Model):
    code = models.CharField(max_length=4, unique=True)
    name = models.CharField(max_length=80, unique=True)
    recognized = models.BooleanField(default=False)

    def __str__(self):
        return self.name


def find_by_id(a_language_id):
    return Language.objects.get(pk=a_language_id)


def find_languages():
    return Language.objects.all().order_by('name')


def find_languages_by_recognized(a_recognized_state):
    return Language.objects.filter(recognized=a_recognized_state)
