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


class AttestationStatus(models.Model):

    student = models.ForeignKey('Student')
    attestation_type = models.CharField(max_length=30, choices=attestation_type.ATTESTATION_TYPES)
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
    list_display = ('student', 'type', 'printed', 'available', 'update_date', 'creation_date')
    fieldsets = ((None, {'fields': ('student', 'type', 'printed', 'available', 'update_date','creation_date')}), )
    list_filter = ('type',)
    raw_id_fields = ('student',)
    search_fields = ['student__registartion_id', 'student__last_name', 'type']


def find_by_registration_id_and_type(registration_id, a_type):
    try:
        return AttestationStatus.objects.get(student__registration_id=registration_id, attestation_type=a_type)
    except ObjectDoesNotExist:
        return None


def find_by_student(student):
    return AttestationStatus.objects.filter(student=student)
