##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2021 Université catholique de Louvain (http://www.uclouvain.be)
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
import time
import traceback
from typing import Dict

import pika
from django.conf import settings
from django.db import OperationalError as DjangoOperationalError, InterfaceError as DjangoInterfaceError, connection
from django.utils import timezone
from psycopg2 import OperationalError as PsycopOperationalError, InterfaceError as PsycopInterfaceError

from base import models as mdl_base
from base.models.student import Student
from exam_enrollment.models import exam_enrollment_request
from exam_enrollment.models.exam_enrollment_request import ExamEnrollmentRequest

logger = logging.getLogger(settings.DEFAULT_LOGGER)
queue_exception_logger = logging.getLogger(settings.QUEUE_EXCEPTION_LOGGER)


def get_request_timeout() -> int:
    if hasattr(settings, 'QUEUES') and settings.QUEUES:
        return settings.QUEUES.get("QUEUES_TIMEOUT").get("EXAM_ENROLLMENT_FORM_RESPONSE")
    return settings.DEFAULT_QUEUE_TIMEOUT


def _get_rabbit_settings():
    credentials = pika.PlainCredentials(settings.QUEUES.get('QUEUE_USER'),
                                        settings.QUEUES.get('QUEUE_PASSWORD'))
    rabbit_settings = pika.ConnectionParameters(settings.QUEUES.get('QUEUE_URL'),
                                                settings.QUEUES.get('QUEUE_PORT'),
                                                settings.QUEUES.get('QUEUE_CONTEXT_ROOT'),
                                                credentials)
    return rabbit_settings


def _create_channel(connect, queue_name):
    channel = connect.channel()
    channel.queue_declare(queue=queue_name, durable=True)
    return channel


def get_exam_enroll_request(acronym: str, request_timeout, stud: Student) -> ExamEnrollmentRequest:
    fetch_date_limit = timezone.now() - timezone.timedelta(seconds=request_timeout)
    return exam_enrollment_request.get_by_student_and_offer_year_acronym_and_fetch_date(
        stud, acronym, fetch_date_limit
    )


def insert_or_update_document_from_queue(body):
    try:
        json_data = body.decode("utf-8")
        data = json.loads(json_data)
        registration_id = data.get('registration_id')
        acronym = data.get('offer_year_acronym')
        if registration_id:
            a_student = mdl_base.student.find_by_registration_id(registration_id)
            exam_enrollment_request.insert_or_update_document(acronym, a_student, json_data)
    except (PsycopOperationalError, PsycopInterfaceError, DjangoOperationalError, DjangoInterfaceError):
        queue_exception_logger.error('Postgres Error during insert_or_update_document_from_queue => retried')
        trace = traceback.format_exc()
        queue_exception_logger.error(trace)
        connection.close()
        time.sleep(1)
        insert_or_update_document_from_queue(body)
    except Exception:
        logger.warning('(Not PostgresError) during insert_or_update_document_from_queue')
        trace = traceback.format_exc()
        logger.error(trace)


def ask_queue_for_exam_enrollment_form(message: Dict):
    connect = pika.BlockingConnection(_get_rabbit_settings())
    queue_name = settings.QUEUES.get('QUEUES_NAME').get('EXAM_ENROLLMENT_FORM_REQUEST')
    channel = _create_channel(connect, queue_name)
    message_published = channel.basic_publish(
        exchange='',
        routing_key=queue_name,
        body=json.dumps(message)
    )
    connect.close()
    return message_published
