##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2017 Université catholique de Louvain (http://www.uclouvain.be)
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
import datetime
from django.db import models
from django.contrib.postgres.fields import JSONField
from django.contrib import admin


class ExamEnrollmentFormAdmin(admin.ModelAdmin):
    list_display = ('registration_id', 'offer_year_id', 'updated_date', )
    fieldsets = ((None, {'fields': ('registration_id', 'offer_year_id', 'updated_date', 'form')}),)
    search_fields = ['registration_id']
    actions = ['resend_messages_to_queue']


class ExamEnrollmentForm(models.Model):
    registration_id = models.CharField(max_length=10, unique=True)
    offer_year_id = models.BigIntegerField(unique=True)
    updated_date = models.DateTimeField(auto_now=False, blank=False, null=False)
    form = JSONField()

    def __str__(self):
        return "{}{}".format(self.registration_id, self.offer_year_id)


def insert_or_update_form(registration_id, offer_year_id, form):
    exam_enrollment_form_object, created = ExamEnrollmentForm.objects.update_or_create(
        registration_id=registration_id,
        offer_year_id=offer_year_id,
        defaults={"form": form, "updated_date": datetime.datetime.now()}
    )
    return exam_enrollment_form_object


def search(registration_id=None, offer_year_id=None, min_date=None):
    out = None
    queryset = ExamEnrollmentForm.objects
    if registration_id:
        queryset = queryset.filter(registration_id=registration_id)
    if offer_year_id:
        queryset = queryset.filter(offer_year_id=offer_year_id)
    if min_date:
        queryset = queryset.filter(updated_date__gte=min_date)
    if registration_id or offer_year_id or min_date:
        out = queryset
    return out
