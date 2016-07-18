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
import uuid
from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User


class DocumentFileAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'content_type', 'creation_date', 'size')
    fieldsets = ((None, {'fields': ('file_name', 'content_type', 'creation_date', 'storage_duration', 'file',
                                    'physical_name', 'physical_extension', 'description', 'user', 'document_type',
                                    'size')}),)
    readonly_fields = ('creation_date', 'physical_name')
    search_fields = ('file_name', 'user')


class DocumentFile(models.Model):
    CONTENT_TYPE_CHOICES = (('APPLICATION_CSV', 'application/csv'),
                            ('APPLICATION_DOC', 'application/doc'),
                            ('APPLICATION_PDF', 'application/pdf'),
                            ('APPLICATION_XLS', 'application/xls'),
                            ('APPLICATION_XLSX', 'application/xlsx'),
                            ('APPLICATION_XML', 'application/xml'),
                            ('APPLICATION_ZIP', 'application/zip'),
                            ('IMAGE_JPEG', 'image/jpeg'),
                            ('IMAGE_GIF', 'image/gif'),
                            ('IMAGE_PNG', 'image/png'),
                            ('TEXT_HTML', 'text/html'),
                            ('TEXT_PLAIN', 'text/plain'),)

    DESCRIPTION_CHOICES = (('ID_CARD', 'identity_card'),
                           ('LETTER_MOTIVATION', 'letter_motivation'),)

    file_name = models.CharField(max_length=100)
    content_type = models.CharField(max_length=50, choices=CONTENT_TYPE_CHOICES, default='APPLICATION_PDF')
    creation_date = models.DateTimeField(auto_now_add=True, editable=False)
    storage_duration = models.IntegerField()
    file = models.FileField(upload_to='/'.join(['uploads']))
    physical_name = models.UUIDField(default=uuid.uuid4, editable=False)
    physical_extension = models.CharField(max_length=10)
    description = models.CharField(max_length=50, choices=DESCRIPTION_CHOICES, default='LETTER_MOTIVATION')
    user = models.ForeignKey(User)
    document_type = models.CharField(max_length=100, null=True, blank=True)
    size = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.file_name


def find_by_id(document_file_id):
    return DocumentFile.objects.get(pk=document_file_id)
