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

from django.conf import settings
from django.db import connection
from django.db.utils import OperationalError as DjangoOperationalError, InterfaceError as DjangoInterfaceError
from psycopg2._psycopg import OperationalError as PsycopOperationalError, InterfaceError as  PsycopInterfaceError

from attribution.models import attribution_new


logger = logging.getLogger(settings.DEFAULT_LOGGER)
queue_exception_logger = logging.getLogger(settings.QUEUE_EXCEPTION_LOGGER)


def insert_or_update_document_from_queue(body):
    try:
        json_data = body.decode("utf-8")
        data_list = json.loads(json_data)
        for data in data_list:
            _insert_or_update_document_from_queue(data)
    except (PsycopOperationalError, PsycopInterfaceError, DjangoOperationalError, DjangoInterfaceError):
        queue_exception_logger.exception('Postgres Error during insert_or_update_document_from_queue => retried')
        connection.close()
        time.sleep(1)
        insert_or_update_document_from_queue(body)
    except Exception:
        logger.exception('(Not PostgresError) during insert_or_update_document_from_queue')


def _insert_or_update_document_from_queue(data):
    global_id = data.get('global_id')
    if global_id:
        attributions_data = data.get('attributions', [])
        attribution_new.insert_or_update_attributions(global_id, attributions_data)