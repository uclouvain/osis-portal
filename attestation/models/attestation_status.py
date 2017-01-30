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
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from attestation.models.enums import attestation_type
from django.utils import timezone
from attestation.queues import student_attestation

class AttestationStatus(models.Model):

    student = models.ForeignKey('Student')
    type = models.CharField(max_length=30, choices=attestation_type.ATTESTATION_TYPES)
    printed = models.BooleanField(default=False)
    available = models.BooleanField(default=False)
    creation_date = models.DateTimeField(editable=False)
    update_date = models.DateTimeField()

    class Meta:
        unique_together = ('student', 'type')

    def save(self, *args, **kwargs):
        if not self.id:
            self.creation_date = timezone.now()
        return super(AttestationStatus, self).save(*args, **kwargs)


class AttestationStatusAdmin(admin.ModelAdmin):
    list_display = ('student', 'type', 'printed', 'available', 'update_date','creation_date')
    fieldsets = ((None, {'fields': ('student', 'type', 'printed', 'available', 'update_date','creation_date')}), )
    raw_id_fields = ('student',)
    search_fields = ['student__registartion_id', 'student__last_name', 'type']


def save_data_from_json(json_attestation_statuses):
    attestation_statuses = json_attestation_statuses.get("")
    for attestation_status_dict in attestation_statuses:
        registration_id = attestation_status_dict.get('registration_id')
        type = attestation_status_dict.get('type')





def has_to_be_updated(attestation_statuses):
    pass


def get_or_fetch(registration_id):
    attestation_statuses = AttestationStatus.objects.filter(student__registration_id=registration_id)
    if not attestation_statuses or has_to_be_updated(attestation_statuses):
        json_attestation_statuses = student_attestation.fetch_json_attestation_statuses(registration_id)
        if json_attestation_statuses:
            attestation_statuses = save_data_from_json(json_attestation_statuses)
    return attestation_statuses


def get_by_registration_id_and_type(registration_id, type):
    try:
        return AttestationStatus.objects.get(student__registration_id=registration_id, type=type)
    except ObjectDoesNotExist:
        return None