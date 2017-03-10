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

UPDATE_DELAY = 24

class ExamEnrollmentFormAdmin(admin.ModelAdmin):
    list_display = ('offer_enrollment', 'updated_date', )
    fieldsets = ((None, {'fields': ('offer_enrollment', 'form')}),)
    search_fields = ['offer_enrollment__student__registration_id', 'offer_enrollment__offer_year__acronym']
    raw_id_fields = ('offer_enrollment', )
    actions = ['resend_messages_to_queue']


class ExamEnrollmentForm(models.Model):
    offer_enrollment = models.ForeignKey('base.OfferEnrollment')
    updated_date = models.DateTimeField(auto_now=True)
    form = JSONField()

    def __str__(self):
        return "{}".format(self.offer_enrollment)


def insert_or_update_form(an_offer_enrollment, form):
    exam_enrollment_form_object, created = ExamEnrollmentForm.objects.update_or_create(
        offer_enrollment=an_offer_enrollment,
        defaults={"form": form}
    )
    return exam_enrollment_form_object


def get_form(an_offer_enrollment):
    min_date = datetime.datetime.now() - datetime.timedelta(hours=UPDATE_DELAY)
    return ExamEnrollmentForm.objects.filter(offer_enrollment=an_offer_enrollment,updated_date__gte=min_date).first()

