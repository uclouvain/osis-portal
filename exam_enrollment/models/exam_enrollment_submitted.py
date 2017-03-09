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


class ExamEnrollmentSubmittedAdmin(admin.ModelAdmin):
    list_display = ('offer_enrollment', )
    fieldsets = ((None, {'fields': ('offer_enrollment', 'document')}),)
    search_fields = ['offer_enrollment']
    raw_id_fields = ('offer_enrollment', )
    actions = ['resend_messages_to_queue']

    def resend_messages_to_queue(self, request, queryset):
        counter = 0
        for record in queryset:
            try:
                queue_sender.send_message(settings.QUEUES.get('QUEUES_NAME').get('EXAM_ENROLLMENT_FORM_SUBMISSION'),
                                          record.document)
                counter += 1
            except (ChannelClosed, ConnectionClosed):
                self.message_user(request,
                                  'Message %s not sent to %s.' % (record.pk, record.queue_name),
                                  level=messages.ERROR)
        self.message_user(request, "{} message(s) sent.".format(counter), level=messages.SUCCESS)


class ExamEnrollmentSubmitted(models.Model):
    offer_enrollment = models.ForeignKey('base.OfferEnrollment')
    document = JSONField()

    def __str__(self):
        return "{}".format(self.offer_enrollment)


def insert_or_update_document(an_offer_enrollment, document):
    exam_enrollment_object, created = ExamEnrollmentSubmitted.objects.update_or_create(
        offer_enrollment=an_offer_enrollment, defaults={"document": document}
    )
    return exam_enrollment_object

