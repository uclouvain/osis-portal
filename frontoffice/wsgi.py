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

import os
import sys
import logging
from django.core.wsgi import get_wsgi_application
from pika.exceptions import ConnectionClosed, AMQPConnectionError, ChannelClosed
import dotenv

# The two following lines are mandatory for working with mod_wsgi on the servers
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..' )
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../frontoffice')

dotenv.read_dotenv()

SETTINGS_FILE = os.environ.get('DJANGO_SETTINGS_MODULE', 'frontoffice.settings.local')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", SETTINGS_FILE)

application = get_wsgi_application()

from osis_common.queue import queue_listener as common_queue_listener, callbacks as common_callback
from performance.queue.student_performance import callback as perf_callback, update_exp_date_callback

from django.conf import settings
LOGGER = logging.getLogger(settings.DEFAULT_LOGGER)

if hasattr(settings, 'QUEUES'):
    # Thread in which is running the listening of the queue used to migrate data (from Osis to Osis-portal)
    try:
        common_queue_listener.SynchronousConsumerThread(settings.QUEUES.get('QUEUES_NAME').get('MIGRATIONS_TO_CONSUME'),
                                                        common_callback.process_message).start()
    except (ConnectionClosed, ChannelClosed, AMQPConnectionError, ConnectionError) as e:
        LOGGER.exception("Couldn't connect to the QueueServer")

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
