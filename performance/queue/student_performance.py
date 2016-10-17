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
import json
from frontoffice.queue.queue_listener import DocumentClient
import datetime

STUDENT_PERFORMANCE_QUEUE_NAME = "STUDENT_PERFORMANCE_QUEUE"


def fetch_and_save(student, offer_year):
    obj = fetch_student_performance(student, offer_year)
    if obj:
        obj.save()
    return obj


def fetch_and_update(student_performance):
    student = student_performance.student
    offer_year = student_performance.offer_year
    obj = fetch_student_performance(student, offer_year)
    if obj:
        student_performance.data = obj.data
        student_performance.update_date = get_expiration_date()
        student_performance.creation_date = get_creation_date()
        student_performance.save()
    return student_performance


def fetch_student_performance(student, offer_year):
    message = str(student) + "_" + str(offer_year)
    json_data = fetch_json_data(message)
    obj = None
    if json_data:
        from performance.models.student_performance import StudentPerformance
        obj = StudentPerformance(student=student, offer_year=offer_year, data=json_data,
                                 update_date=get_expiration_date())
    return obj


def fetch_json_data(message):
    client = DocumentClient(STUDENT_PERFORMANCE_QUEUE_NAME)
    json_data = client.call(message)
    json_student_perf = None
    if json_data:
        json_student_perf = json.loads(json_data.decode("utf-8"))
    return json_student_perf


def get_expiration_date():
    today = datetime.date.today()
    timedelta = datetime.timedelta(days=2)
    expiration_date = today + timedelta
    return expiration_date


def get_creation_date():
    today = datetime.datetime.today()
    return today
