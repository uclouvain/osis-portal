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
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.postgres.fields import JSONField


class ScoreEncodingAdmin(admin.ModelAdmin):
    list_display = ('global_id',)
    fieldsets = ((None, {'fields': ('global_id', 'document')}),)
    search_fields = ['global_id']


class ScoreEncoding(models.Model):
    global_id = models.CharField(max_length=10, unique=True)
    document = JSONField()

    def __str__(self):
        return u"%s" % self.global_id


def find_by_global_id(global_id):
    try:
        return ScoreEncoding.objects.get(global_id=global_id)
    except ObjectDoesNotExist:
        return None


def insert_or_update_document(global_id, document):
    score_encoding_object, created = ScoreEncoding.objects.update_or_create(
        global_id=global_id, defaults={"document": document}
    )
    return score_encoding_object

