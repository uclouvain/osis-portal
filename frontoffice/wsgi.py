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

import sys
import logging

import os
import dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if 'test' in sys.argv:
    os.environ.setdefault('TESTING', 'True')
dotenv.read_dotenv(os.path.join(BASE_DIR, '.env'))
sys.path.extend(os.environ.get('EXTRA_SYS_PATHS').split()) if os.environ.get('EXTRA_SYS_PATHS') else None

from django.core.wsgi import get_wsgi_application
from pika.exceptions import ConnectionClosed, AMQPConnectionError, ChannelClosed


SETTINGS_FILE = os.environ.get('DJANGO_SETTINGS_MODULE', 'frontoffice.settings.local')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", SETTINGS_FILE)

try:
    application = get_wsgi_application()
except KeyError as ke:
    print("Error loading application.")
    print("The following environment var is not defined : {}".format(str(ke)))
    print("Check the following possible causes :")
    print(" - You don't have a .env file. You can copy .env.example to .env to use default")
    print(" - Mandatory variables are not defined in your .env file.")
    sys.exit("SettingsKeyError")
except ImportError as ie:
    print("Error loading application : {}".format(str(ie)))
    print("Check the following possible causes :")
    print(" - The DJANGO_SETTINGS_MODULE defined in your .env doesn't exist")
    print(" - No DJANGO_SETTINGS_MODULE is defined and the default 'frontoffice.settings.local' doesn't exist ")
    sys.exit("DjangoSettingsError")


from performance.queue.student_performance import callback as perf_callback, update_exp_date_callback

from django.conf import settings
LOGGER = logging.getLogger(settings.DEFAULT_LOGGER)

if hasattr(settings, 'QUEUES') and settings.QUEUES:
    from osis_common.queue import queue_listener as common_queue_listener, callbacks as common_callback
    # migration queue used to migrate data between osis ans osis_portal
    try:
        common_queue_listener.SynchronousConsumerThread(settings.QUEUES.get('QUEUES_NAME').get('MIGRATIONS_TO_CONSUME'),
                                                        common_callback.process_message).start()
    except (ConnectionClosed, ChannelClosed, AMQPConnectionError, ConnectionError) as e:
        LOGGER.exception("Couldn't connect to the QueueServer")

    # Queues used by performance app
    if 'performance' in settings.INSTALLED_APPS:
        # Thread in which is running the listening of the queue used to received student points
        try:
            common_queue_listener.SynchronousConsumerThread(settings.QUEUES.get('QUEUES_NAME').get('PERFORMANCE'),
                                                     perf_callback).start()
        except (ConnectionClosed, ChannelClosed, AMQPConnectionError, ConnectionError) as e:
            LOGGER.exception("Couldn't connect to the QueueServer")

        # Thread in wich is running the listening of the queue used to update the expiration date of the students points
        try:
            common_queue_listener.SynchronousConsumerThread(settings.QUEUES.get('QUEUES_NAME').get('PERFORMANCE_UPDATE_EXP_DATE'),
                                                            update_exp_date_callback).start()
        except (ConnectionClosed, ChannelClosed, AMQPConnectionError, ConnectionError) as e:
            LOGGER.exception("Couldn't connect to the QueueServer")

    # Thread in wich is running the listening of the queue used to receive the json of scores_sheets from osis
    if 'assessments' in settings.INSTALLED_APPS:
        from assessments.views.score_encoding import insert_or_update_document_from_queue
        try:
            common_queue_listener.SynchronousConsumerThread(
                settings.QUEUES.get('QUEUES_NAME').get('SCORE_ENCODING_PDF_RESPONSE'),
                insert_or_update_document_from_queue).start()
        except (ConnectionClosed, ChannelClosed, AMQPConnectionError, ConnectionError) as e:
            LOGGER.exception("Couldn't connect to the QueueServer")

    if 'exam_enrollment' in settings.INSTALLED_APPS:
        from exam_enrollment.views.exam_enrollment import insert_or_update_document_from_queue
        try:
            common_queue_listener.SynchronousConsumerThread(
                settings.QUEUES.get('QUEUES_NAME').get('EXAM_ENROLLMENT_FORM_RESPONSE'),
                insert_or_update_document_from_queue).start()
        except (ConnectionClosed, ChannelClosed, AMQPConnectionError, ConnectionError) as e:
            LOGGER.exception("Couldn't connect to the QueueServer")

    if 'attribution' in settings.INSTALLED_APPS:
        from attribution.business.attribution_json import insert_or_update_document_from_queue
        try:
            common_queue_listener.SynchronousConsumerThread(
                settings.QUEUES.get('QUEUES_NAME').get('ATTRIBUTION_RESPONSE'),
                insert_or_update_document_from_queue).start()
        except (ConnectionClosed, ChannelClosed, AMQPConnectionError, ConnectionError) as e:
            LOGGER.exception("Couldn't connect to the QueueServer")