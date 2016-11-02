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

from django.contrib import admin
from django.db import models


class ApplicationDocumentFileAdmin(admin.ModelAdmin):
    list_display = ('application', 'document_file')


class ApplicationDocumentFile(models.Model):
    application = models.ForeignKey('Application')
    document_file = models.ForeignKey('osis_common.documentFile')


def search(application=None, description=None):
    out = None
    queryset = ApplicationDocumentFile.objects.order_by('document_file__creation_date')
    if application:
        queryset = queryset.filter(application=application)
    if description:
        queryset = queryset.filter(document_file__description=description)
    if application or description:
        out = queryset
    return out


def find_first(application=None, description=None):
    results = search(application, description)
    if results.exists():
        return results[0]
    return None


def find_by_document(document_file):
    return ApplicationDocumentFile.objects.filter(document_file=document_file)


def find_document_by_application_and_description(application, description):
    queryset = ApplicationDocumentFile.objects\
        .filter(application=application)\
        .filter(document_file__description=description)\
        .order_by('document_file__creation_date')
    return [application_document_file.document_file for application_document_file in queryset]
