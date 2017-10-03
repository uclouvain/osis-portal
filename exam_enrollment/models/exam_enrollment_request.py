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
from django.db import models
from django.contrib.postgres.fields import JSONField
from pika.exceptions import ChannelClosed, ConnectionClosed
from osis_common.queue import queue_sender
from django.conf import settings
from django.contrib import admin, messages
from django.core.exceptions import ObjectDoesNotExist


class ExamEnrollmentRequestdAdmin(admin.ModelAdmin):
    list_display = ('offer_enrollment', )
    fieldsets = ((None, {'fields': ('offer_enrollment', 'document')}),)
    search_fields = ['offer_enrollment__student__registration_id', 'offer_enrollment__offer_year__acronym']
    raw_id_fields = ('offer_enrollment', )


class ExamEnrollmentRequest(models.Model):
    offer_enrollment = models.ForeignKey('base.OfferEnrollment', on_delete=models.CASCADE)
    document = JSONField()

    def __str__(self):
        return "{}".format(self.offer_enrollment)


def insert_or_update_document(an_offer_enrollment, document):
    exam_enrollment_object, created = ExamEnrollmentSubmitted.objects.update_or_create(
        offer_enrollment=an_offer_enrollment, defaults={"document": document})
    return exam_enrollment_object


def find_by_offer_enrollment(offer_enrollment):
    try:
        exam_enrollments_request = ExamEnrollmentRequest.objects.get(offer_enrollment=offer_enrollment)
        return exam_enrollments_request
    except ObjectDoesNotExist:
        return None

