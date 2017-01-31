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
import logging
import traceback
from django.conf import settings
from frontoffice.queue.queue_listener import PerformanceClient
import datetime
from django.utils.datetime_safe import datetime as safe_datetime
from base.models import academic_year as mdl_academic_year

logger = logging.getLogger(settings.DEFAULT_LOGGER)


def callback(json_data):
    try:
        json_data = json.loads(json_data.decode("utf-8"))
        registration_id = extract_student_from_json(json_data)
        academic_year = extract_academic_year_from_json(json_data)
        acronym = extract_acronym_from_json(json_data)
        save(registration_id, academic_year, acronym, json_data)
    except Exception as e:
        logger.error('Error callback performance : {}'.format(e))
        pass


def update_exp_date_callback(json_data):
    try:
        json_data = json.loads(json_data.decode("utf-8"))
        registration_id = json_data.get("registrationId")
        academic_year = json_data.get("academicYear")
        acronym = json_data.get("acronym")
        new_exp_date = json_data.get("expirationDate")
        update_expiration_date(registration_id, academic_year, acronym, new_exp_date)
    except Exception as e:
        logger.error('Error callback update_exp_date performance : {}'.format(e))
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
    try:
        message = generate_message(registration_id, academic_year, acronym)
        client = PerformanceClient()
        json_data = client.call(message)
        json_student_perf = None
        if json_data:
            json_student_perf = json.loads(json_data.decode("utf-8"))
    except Exception:
        json_student_perf = None
        trace = traceback.format_exc()
        logger.error(trace)
    return json_student_perf


def get_expiration_date(academic_year):
    now = safe_datetime.now()
    current_academic_year = mdl_academic_year.current_academic_year()
    current_year = current_academic_year.year if current_academic_year else None
    timedelta = datetime.timedelta(hours=settings.PERFORMANCE_CONFIG.get('UPDATE_DELTA_HOURS_CURRENT_ACADEMIC_YEAR')
                                   if current_year == academic_year
                                   else settings.PERFORMANCE_CONFIG.get('UPDATE_DELTA_HOURS_NON_CURRENT_ACADEMIC_YEAR'))
    expiration_date = now + timedelta
    return expiration_date


def get_creation_date():
    today = safe_datetime.now()
    return today


def save(registration_id, academic_year, acronym, json_data):
    from performance.models.student_performance import update_or_create
    if json_data.get("expirationDate"):
        update_date = json_data.pop("expirationDate")
        update_date = datetime.datetime.fromtimestamp(update_date / 1e3)
    else:
        update_date = get_expiration_date(academic_year)
    creation_date = get_creation_date()
    fields = {"data": json_data, "update_date": update_date, "creation_date": creation_date}
    try:
        obj = update_or_create(registration_id, academic_year, acronym, fields)
    except Exception:
        obj = None
    return obj


def get_performances_by_registration_id_and_offer(registration_id, academic_year, acronym):
    from performance.models.student_performance import search
    return search(registration_id=registration_id,
                  academic_year=academic_year,
                  acronym=acronym)


def get_performances_by_offer(acronym, academic_year):
    from performance.models.student_performance import find_by_acronym_and_academic_year
    return find_by_acronym_and_academic_year(acronym=acronym, academic_year=academic_year)


def update_expiration_date(registration_id, academic_year, acronym, new_exp_date):
    if registration_id and registration_id != 'null':
        performances_to_update = get_performances_by_registration_id_and_offer(registration_id=registration_id,
                                                                               academic_year=academic_year,
                                                                               acronym=acronym)
    else:
        performances_to_update = get_performances_by_offer(acronym=acronym, academic_year=academic_year)

    for performance in performances_to_update:
        if new_exp_date and new_exp_date != 'null':
            performance.update_date = datetime.datetime.fromtimestamp(new_exp_date / 1e3)
            performance.save()
