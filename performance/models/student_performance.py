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
from django.contrib.postgres.fields import JSONField
from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from base.models.serializable_model import SerializableModel
from frontoffice.queue.queue_listener import DocumentClient
import datetime
import json


class StudentPerformanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'offer_year')
    list_filter = ('student__registration_id',)
    fieldsets = ((None, {'fields': ('student', 'offer_year')}),)


class StudentPerformance(SerializableModel):
    student = models.ForeignKey('base.Student')
    offer_year = models.ForeignKey('base.OfferYear')
    data = JSONField()  # TODO discuss about db_index
    expiration_date = models.DateField()

    def __str__(self):
        return


def search(student=None, offer_year=None):
    """
        Search students by optional arguments. At least one argument should be informed
        otherwise it returns empty.
    """
    has_criteria = False
    student_performances = StudentPerformance.objects
    if student:
        student_performances.filter(student=student)
        has_criteria = True
    if offer_year:
        student_performances.filter(offer_year=offer_year)
        has_criteria = True

    if has_criteria:
        return student_performances
    else:
        return None


def find_by_student_and_offer_year(student, offer_year):
    try:
        result = StudentPerformance.objects.get(student=student, offer_year=offer_year)
    except ObjectDoesNotExist:
        result = None
    return result


def find_or_fetch(student, offer_year):
    result = find_by_student_and_offer_year(student, offer_year)
    if result is None:
        result = fetch_and_save(student, offer_year)
    elif has_expired(result):
        fetch_and_update(result)
    return result


def fetch_and_save(student, offer_year):
    obj = fetch_student_performance(student, offer_year)
    if obj:
        obj.save()
    return obj


def fetch_and_update(student_performance):
    student = student_performance.student
    offer_year = student_performance.offer_year
    message = str(student) + "_" + str(offer_year)
    json_data = fetch_json_data(message)
    if json_data:
        student_performance.data = json_data
        student_performance.expiration_date = get_expiration_date()
        student_performance.save()


def fetch_student_performance(student, offer_year):
    message = str(student) + "_" + str(offer_year)
    json_data = fetch_json_data(message)
    obj = None
    if json_data:
        obj = StudentPerformance(student=student, offer_year=offer_year, data=json_data,
                                 expiration_date=get_expiration_date())
    return obj


def fetch_json_data(message):
    STUDENT_PERFORMANCE_QUEUE_NAME = "STUDENT_PERFORMANCE_QUEUE"
    client = DocumentClient(STUDENT_PERFORMANCE_QUEUE_NAME)
    json_data = client.call(message)  # TODO Can take a long time
    json_student_perf = None
    if json_data:
        json_student_perf = json.loads(json_data.decode("utf-8"))
    return json_student_perf


def has_expired(student_performance):
    today = datetime.date.today()
    expiration_date = student_performance.expiration_date
    return expiration_date < today


def get_expiration_date():
    today = datetime.date.today()
    timedelta = datetime.timedelta(days=2)
    expiration_date = today + timedelta
    return expiration_date

