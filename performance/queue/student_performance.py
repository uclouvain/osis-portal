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
from csv import excel
import json
from frontoffice.queue.queue_listener import PerformanceClient
import datetime
from django.utils.datetime_safe import datetime as safe_datetime

UPDATE_DELTA_HOURS = 12


def callback(json_data):
    try:
        json_data = json.loads(json_data.decode("utf-8"))
        registration_id = extract_student_from_json(json_data)
        academic_year = extract_academic_year_from_json(json_data)
        acronym = extract_acronym_from_json(json_data)
        save(registration_id, academic_year, acronym, json_data)
    except Exception:
        pass


def extract_student_from_json(json_data):
    registration_id = json_data["etudiant"]["noma"]
    return registration_id


def extract_academic_year_from_json(json_data):
    academic_year = json_data["monAnnee"]["anac"]
    return int(academic_year)


def extract_acronym_from_json(json_data):
    acronym = json_data["monAnnee"]["monOffre"]["offre"]["sigleComplet"]
    return acronym


def generate_message(registration_id, academic_year, acronym):
    message = dict()
    message['registration_id'] = registration_id
    message["acronym"] = acronym
    message["academic_year"] = str(academic_year)
    return json.dumps(message)


def fetch_and_save(registration_id, academic_year, acronym):
    data = fetch_json_data(registration_id, academic_year, acronym)
    obj = None
    if data:
        obj = save(registration_id, academic_year, acronym, data)
    return obj


def fetch_json_data(registration_id, academic_year, acronym):
    message = generate_message(registration_id, academic_year, acronym)
    client = PerformanceClient()
    json_data = client.call(message)
    json_student_perf = None
    if json_data:
        json_student_perf = json.loads(json_data.decode("utf-8"))
    return json_student_perf


def get_expiration_date():
    now = safe_datetime.now()
    timedelta = datetime.timedelta(hours=UPDATE_DELTA_HOURS)
    expiration_date = now + timedelta
    return expiration_date


def get_creation_date():
    today = safe_datetime.now()
    return today


def save(registration_id, academic_year, acronym, json_data):
    from performance.models.student_performance import update_or_create
    update_date = get_expiration_date()
    creation_date = get_creation_date()
    fields = {"data": json_data, "update_date": update_date, "creation_date": creation_date}
    try:
        obj = update_or_create(registration_id, academic_year, acronym, fields)
    except Exception:
        obj = None
    return obj

