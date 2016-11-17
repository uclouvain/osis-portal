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
from frontoffice.queue.queue_listener import PerformanceClient
import datetime
from django.utils import timezone

UPDATE_DELTA = 12

def callback(json_data):
    try:
        json_data = json.loads(json_data.decode("utf-8"))
        student = extract_student_from_json(json_data)
        offer_year = extract_offer_year_from_json(json_data)
        save(student, offer_year, json_data)
    except RuntimeError:
        pass


def extract_student_from_json(json_data):
    from base.models import student as mdl_std
    registration_id = json_data["registration_id"]
    student = mdl_std.find_by_registration_id(registration_id)
    return student


def extract_offer_year_from_json(json_data):
    from base.models import academic_year as mdl_academic_yr
    from base.models import offer_year as mdl_offer_yr
    year = json_data["academic_years"][0]["anac"]
    academic_year = mdl_academic_yr.find_by_year(year)
    acronym = json_data["academic_years"][0]["programs"][0]["acronym"]
    offer_year = mdl_offer_yr.find_by_acronym_academic_year(acronym, academic_year)
    return offer_year


def generate_message(student, offer_year):
    message = {}
    message['noma'] = student.registration_id
    message["sigle"] = offer_year.acronym
    message["anac"] = str(offer_year.academic_year.year)
    return str(message)


def fetch_and_save(student, offer_year):
    data = fetch_json_data(student, offer_year)
    obj = None
    if data:
        obj = save(student, offer_year, data)
    return obj


def fetch_json_data(student, offer_year):
    message = generate_message(student, offer_year)
    client = PerformanceClient()
    json_data = client.call(message)
    json_student_perf = None
    if json_data:
        json_student_perf = json.loads(json_data.decode("utf-8"))
    return json_student_perf


def get_expiration_date():
    now = timezone.now()
    timedelta = datetime.timedelta(hours=UPDATE_DELTA)
    expiration_date = now + timedelta
    return expiration_date


def get_creation_date():
    today = datetime.datetime.today()
    return today


def save(student, offer_year, json_data):
    from performance.models.student_performance import update_or_create
    update_date = get_expiration_date()
    creation_date = get_creation_date()
    fields = {"data": json_data, "update_date": update_date, "creation_date": creation_date}
    obj = update_or_create(student, offer_year, fields)
    return obj

