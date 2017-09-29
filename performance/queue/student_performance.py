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
import datetime

from django.conf import settings
from psycopg2._psycopg import OperationalError as PsycopOperationalError, InterfaceError as  PsycopInterfaceError
from django.db.utils import OperationalError as DjangoOperationalError, InterfaceError as DjangoInterfaceError
from django.utils.datetime_safe import datetime as safe_datetime
from django.db import connection

from frontoffice.queue.queue_listener import PerformanceClient
from base.models import academic_year as mdl_academic_year
from osis_common.models.queue_exception import QueueException

logger = logging.getLogger(settings.DEFAULT_LOGGER)
queue_exception_logger = logging.getLogger(settings.QUEUE_EXCEPTION_LOGGER)


def callback(json_data):
    try:
        json_data_dict = json.loads(json_data.decode("utf-8"))
        registration_id = extract_student_from_json(json_data_dict)
        academic_year = extract_academic_year_from_json(json_data_dict)
        acronym = extract_acronym_from_json(json_data_dict)
        save_consumed(registration_id, academic_year, acronym, json_data_dict)
    except (PsycopOperationalError, PsycopInterfaceError, DjangoOperationalError, DjangoInterfaceError) as ep:
        trace = traceback.format_exc()
        try:
            data = json.loads(json_data.decode("utf-8"))
            queue_exception = QueueException(queue_name=settings.QUEUES.get('QUEUES_NAME').get('PERFORMANCE'),
                                             message=data,
                                             exception_title='[Catched and retried] - {}'.format(type(ep).__name__),
                                             exception=trace)
            queue_exception_logger.error(queue_exception.to_exception_log())
        except Exception:
            logger.error(trace)
            log_trace = traceback.format_exc()
            logger.warning('Error during queue logging and retry:\n {}'.format(log_trace))
        connection.close()
        callback(json_data)
    except Exception as e:
        trace = traceback.format_exc()
        try:
            data = json.loads(json_data.decode("utf-8"))
            queue_exception = QueueException(queue_name=settings.QUEUES.get('QUEUES_NAME').get('PERFORMANCE'),
                                             message=data,
                                             exception_title=type(e).__name__,
                                             exception=trace)
            queue_exception_logger.error(queue_exception.to_exception_log())
        except Exception:
            logger.error(trace)
            log_trace = traceback.format_exc()
            logger.warning('Error during queue logging :\n {}'.format(log_trace))


def update_exp_date_callback(json_data):
    try:
        json_data_dict = json.loads(json_data.decode("utf-8"))
        registration_id = json_data_dict.get("registrationId")
        academic_year = json_data_dict.get("academicYear")
        acronym = json_data_dict.get("acronym")
        new_exp_date = json_data_dict.get("expirationDate")
        update_expiration_date(registration_id, academic_year, acronym, new_exp_date)
    except (PsycopOperationalError, PsycopInterfaceError, DjangoOperationalError, DjangoInterfaceError) as ep:
        trace = traceback.format_exc()
        try:
            data = json.loads(json_data.decode("utf-8"))
            queue_exception = QueueException(queue_name=settings.QUEUES.get('QUEUES_NAME').get('PERFORMANCE_UPDATE_EXP_DATE'),
                                             message=data,
                                             exception_title='[Catched and retried] - {}'.format(type(ep).__name__),
                                             exception=trace)
            queue_exception_logger.error(queue_exception.to_exception_log())
        except Exception:
            logger.error(trace)
            log_trace = traceback.format_exc()
            logger.warning('Error during queue logging and retry:\n {}'.format(log_trace))
        connection.close()
        update_exp_date_callback(json_data)
    except Exception as e:
        trace = traceback.format_exc()
        try:
            data = json.loads(json_data.decode("utf-8"))
            queue_exception = QueueException(queue_name=settings.QUEUES.get('QUEUES_NAME').get('PERFORMANCE_UPDATE_EXP_DATE'),
                                             message=data,
                                             exception_title=type(e).__name__,
                                             exception=trace)
            queue_exception_logger.error(queue_exception.to_exception_log())
        except Exception:
            log_trace = traceback.format_exc()
            logger.warning('Error during queue logging :\n {}'.format(log_trace))
            logger.error(trace)


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
    obj = None
    try:
        data = fetch_json_data(registration_id, academic_year, acronym)
        if data:
            try:
                obj = save_fetched(registration_id, academic_year, acronym, data)
            except (PsycopOperationalError, PsycopInterfaceError, DjangoOperationalError, DjangoInterfaceError) as ep:
                trace = traceback.format_exc()
                try:
                    data = generate_message(registration_id, academic_year, acronym)
                    queue_exception = QueueException(queue_name=settings.QUEUES.get('QUEUES_NAME').get('STUDENT_PERFORMANCE'),
                                                     message=data,
                                                     exception_title='[Catched and retried] - {}'.format(type(ep).__name__),
                                                     exception=trace)
                    queue_exception_logger.error(queue_exception.to_exception_log())
                except Exception:
                    logger.error(trace)
                    log_trace = traceback.format_exc()
                    logger.warning('Error during queue logging and retry:\n {}'.format(log_trace))
                connection.close()
                obj = save_fetched(registration_id, academic_year, acronym, data)
    except Exception as e:
        trace = traceback.format_exc()
        try:
            data = generate_message(registration_id, academic_year, acronym)
            queue_exception = QueueException(queue_name=settings.QUEUES.get('QUEUES_NAME').get('STUDENT_PERFORMANCE'),
                                             message=data,
                                             exception_title=type(e).__name__,
                                             exception=trace)
            queue_exception_logger.error(queue_exception.to_exception_log())
        except Exception:
            logger.error(trace)
            log_trace = traceback.format_exc()
            logger.warning('Error during queue logging :\n {}'.format(log_trace))
    return obj


def fetch_json_data(registration_id, academic_year, acronym):
    json_student_perf = None
    json_data = None
    message = generate_message(registration_id, academic_year, acronym)
    if hasattr(settings, 'QUEUES') and settings.QUEUES:
        client = PerformanceClient()
        json_data = client.call(message)
    if json_data:
        try:
            json_student_perf = json.loads(json_data.decode("utf-8"))
        except ValueError:
            return None
    return json_student_perf


def get_expiration_date(academic_year, consumed):
    now = safe_datetime.now()
    current_academic_year = mdl_academic_year.current_academic_year()
    current_year = current_academic_year.year if current_academic_year else None
    timedelta = get_time_delta(academic_year, consumed, current_year)
    expiration_date = now + timedelta
    return expiration_date


def get_time_delta(academic_year, consumed, current_year):
    if consumed and current_year == academic_year:
        update_delta_hours = settings.PERFORMANCE_CONFIG.get('UPDATE_DELTA_HOURS_AFTER_CONSUMPTION')
    elif current_year == academic_year:
        update_delta_hours = settings.PERFORMANCE_CONFIG.get('UPDATE_DELTA_HOURS_CURRENT_ACADEMIC_YEAR')
    else:
        update_delta_hours = settings.PERFORMANCE_CONFIG.get('UPDATE_DELTA_HOURS_NON_CURRENT_ACADEMIC_YEAR')
    timedelta = datetime.timedelta(hours=update_delta_hours)
    return timedelta


def get_creation_date():
    today = safe_datetime.now()
    return today


def save_consumed(registration_id, academic_year, acronym, json_data):
    default_update_date = get_expiration_date(academic_year=academic_year, consumed=True)
    return save(registration_id, academic_year, acronym, json_data, default_update_date)


def save_fetched(registration_id, academic_year, acronym, json_data):
    default_update_date = get_expiration_date(academic_year=academic_year, consumed=False)
    return save(registration_id, academic_year, acronym, json_data, default_update_date)


def save(registration_id, academic_year, acronym, json_data, default_update_date):
    from performance.models.student_performance import update_or_create
    expiration_date = json_data.pop("expirationDate", None)
    if expiration_date:
        update_date = datetime.datetime.fromtimestamp(expiration_date / 1e3)
    else:
        update_date = default_update_date
    authorized = json_data.pop("authorized", False)
    session_locked = json_data.pop("sessionMonth", None)
    offer_registration_state = json_data.pop("etatInscr", None)
    creation_date = get_creation_date()
    fields = {"data": json_data,
              "update_date": update_date,
              "creation_date": creation_date,
              "authorized": authorized,
              "session_locked": session_locked,
              "offer_registration_state": offer_registration_state}
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
