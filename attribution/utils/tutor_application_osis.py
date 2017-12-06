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
import json
import logging
import time
from psycopg2._psycopg import OperationalError as PsycopOperationalError, InterfaceError as PsycopInterfaceError
from django.db import connection
from django.db.utils import OperationalError as DjangoOperationalError, InterfaceError as DjangoInterfaceError
from django.conf import settings
from attribution.models import attribution_new as mdl_attribution_new


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
        for application in new_applications:
            global_id = application.get('global_id')
            operation = application.get('operation')
            attribution_new = mdl_attribution_new.find_by_global_id(global_id)
            if attribution_new:
                tutor_applications = attribution_new.applications[0]['tutor_applications']
                if attribution_new.applications == "{}":
                    attribution_new.applications = new_applications
                    attribution_new.save()
                    test = "Insert"
                else:

                    elif tutor_applications == application.get('tutor_applications') and operation == "update":

                else:
                    test = "No"
                print(test)
    except (PsycopOperationalError, PsycopInterfaceError, DjangoOperationalError, DjangoInterfaceError):
        queue_exception_logger.exception('Postgres Error during process tutor application message => retried')
        connection.close()
        time.sleep(1)
        process_message(body)
    except Exception:
        logger.exception('(Not PostgresError) during process tutor application message. Cannot update ')
