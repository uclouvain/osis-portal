##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2018 Université catholique de Louvain (http://www.uclouvain.be)
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
from datetime import datetime

from dateutil import parser
from django.conf import settings
from django.db import connection
from django.db.utils import OperationalError as DjangoOperationalError, InterfaceError as DjangoInterfaceError
from psycopg2._psycopg import OperationalError as PsycopOperationalError, InterfaceError as PsycopInterfaceError

from attribution.models import attribution_new as mdl_attribution_new
from attribution.models.attribution_new import AttributionNew

DELETE_OPERATION = "delete"
UPDATE_OPERATION = "update"
ERROR_EPC_FIELD = "error"
LEARNING_CONTAINER_YEAR_PREFIX_EXTERNAL_ID = "osis.learning_container_year_"
TUTOR_PREFIX_EXTERNAL_ID = "osis.tutor_"

logger = logging.getLogger(settings.DEFAULT_LOGGER)
queue_exception_logger = logging.getLogger(settings.QUEUE_EXCEPTION_LOGGER)


def process_message(body):
    """
        Callback of APPLICATION_RESPONSE queue
    :param json_data:
    :return:
    """
    try:
        json_data = body.decode("utf-8")
        new_applications = json.loads(json_data)
        _update_applications_list(new_applications)
    except (PsycopOperationalError, PsycopInterfaceError, DjangoOperationalError, DjangoInterfaceError):
        queue_exception_logger.exception('Postgres Error during process tutor application message => retried')
        connection.close()
        time.sleep(1)
        process_message(body)
    except Exception as e:
        logger.exception('(Not PostgresError) during process tutor application message. Cannot update ')
        logger.exception(str(e))


def _update_applications_list(new_applications):
    for new_application in new_applications:
        global_id = new_application.get('global_id')
        attribution_new = mdl_attribution_new.find_by_global_id(global_id)
        if attribution_new:
            _manage_exisisting_attribution_new(attribution_new, new_application)
        else:
            attribution_new = AttributionNew(global_id=global_id,
                                             applications=new_application.get('tutor_applications'))
            attribution_new.save()


def _manage_exisisting_attribution_new(attribution_new, new_application):
    applications_list = list(attribution_new.applications) if attribution_new.applications else []
    if not applications_list:
        applications_list = new_application.get('tutor_applications', [])
    else:
        for application in new_application['tutor_applications']:
            _manage_new_applications(application, applications_list)
    _merge_applications_list(applications_list, attribution_new)


def _manage_new_applications(application, applications_list):
    existing_application = next((data for data in applications_list if
                                 data.get("year") == application.get("year") and data.get(
                                     "acronym") == application.get("acronym")), None)
    if existing_application:
        if _check_if_update(application, existing_application):
            applications_list.append(application)
            applications_list.remove(existing_application)
        else:
            applications_list.append(existing_application)
            applications_list.remove(existing_application)
    else:
        applications_list.append(application)


def _check_if_update(application, existing_application):
    if "pending" not in existing_application:
        return True
    elif existing_application["pending"] == UPDATE_OPERATION and \
            _get_updated_at_time(existing_application) < _get_updated_at_time(application):
        return True


def _get_updated_at_time(application):
    updated_at_value = application.get("updated_at")
    if isinstance(updated_at_value, float):
        return datetime.fromtimestamp(updated_at_value)
    return parser.parse(updated_at_value)


def _merge_applications_list(applications_list, attribution_new):
    attribution_new.applications = applications_list
    attribution_new.save()
