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

import os,sys
import logging
from django.conf import settings
from django.core.wsgi import get_wsgi_application
from frontoffice.queue import callbacks
from frontoffice.queue import queue_listener
from performance.queue import callbacks as perf_callbacks
from pika.exceptions import ConnectionClosed, AMQPConnectionError, ChannelClosed

LOGGER = logging.getLogger(settings.DEFAULT_LOGGER)

# The two following lines are mandatory for working with mod_wsgi on the servers
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..' )
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../frontoffice')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "frontoffice.settings")

application = get_wsgi_application()

# Thread in which is running the listening of the queue used to migrate data (from Osis to Osis-portal)
queue_for_migration = 'osis_portal' # Data from Osis to insert/update/delete in Osis-portal
try:
    queue_listener.SynchronousConsumerThread(queue_for_migration, callbacks.insert_or_update).start()
except (ConnectionClosed, ChannelClosed, AMQPConnectionError, ConnectionError) as e:
    LOGGER.exception("Couldn't connect to the QueueServer")

# Thread in which is running the listening of the queue used to print exams scores of students
queue_for_performancce = 'performance'
try:
    queue_listener.listen_queue(queue_for_performancce, perf_callbacks.couchbase_insert_or_update)
except (ConnectionClosed, ChannelClosed, AMQPConnectionError, ConnectionError) as e:
    LOGGER.exception("Couldn't connect to the QueueServer")
