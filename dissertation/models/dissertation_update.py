##############################################################################
#
# OSIS stands for Open Student Information System. It's an application
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
from osis_common.models.serializable_model import SerializableModel
from django.contrib import admin
from django.db import models
from base import models as mdl
from dissertation.models import dissertation

JUSTIFICATION_LINK = "_set_to_"
INVISIBLE_JUSTIFICATION_KEYWORDS = ('auto_add_jury',
                                    'manager_add_jury',
                                    'manager_creation_dissertation',
                                    'manager_delete_jury',
                                    'manager_edit_dissertation',
                                    'manager_set_active_false',
                                    'teacher_add_jury',
                                    'teacher_delete_jury',
                                    'teacher_set_active_false'
                                    )


class DissertationUpdateAdmin(admin.ModelAdmin):
    list_display = ('dissertation', 'author', 'status_from', 'status_to', 'person', 'created')
    raw_id_fields = ('person', 'dissertation')
    search_fields = ('uuid', 'dissertation', 'author', 'person')


class DissertationUpdate(SerializableModel):
    status_from = models.CharField(max_length=12, choices=dissertation.STATUS_CHOICES, default='DRAFT')
    status_to = models.CharField(max_length=12, choices=dissertation.STATUS_CHOICES, default='DRAFT')
    created = models.DateTimeField(auto_now_add=True)
    justification = models.TextField(default='')
    person = models.ForeignKey('base.Person')
    dissertation = models.ForeignKey(dissertation.Dissertation)

    @property
    def author(self):
        return self.dissertation.author

    def __str__(self):
        desc = "%s / %s >> %s / %s" % (self.dissertation.title, self.status_from, self.status_to, str(self.created))
        return desc


def search_by_dissertation(memory):
    queryset = DissertationUpdate.objects.filter(dissertation=memory).order_by('created')
    for keyword in INVISIBLE_JUSTIFICATION_KEYWORDS:
        queryset = queryset.exclude(justification__contains=keyword)
    return queryset


def add(request, memory, old_status, justification=None):
    person = mdl.person.find_by_user(request.user)
    update = DissertationUpdate()
    update.status_from = old_status
    update.status_to = memory.status
    if justification:
        update.justification = justification
    else:
        update.justification = "%s%s%s" % (person, JUSTIFICATION_LINK, memory.status)
    update.person = person
    update.dissertation = memory
    update.save()
