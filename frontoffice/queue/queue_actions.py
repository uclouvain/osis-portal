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

from couchbase import Couchbase
from pprint import pprint
import json
import logging
from django.conf import settings
import pika
from frontoffice.settings import QUEUE_URL, QUEUE_USER, QUEUE_PASSWORD, QUEUE_PORT, QUEUE_CONTEXT_ROOT

logger = logging.getLogger(settings.DEFAULT_LOGGER)


def couchbase_insert(json_datas):
    cb = Couchbase.connect(bucket='default')
    data = json.loads(json_datas.decode("utf-8"))
    key = "{0}-{1}".format(
        data['id'],
        data['name'].replace(' ', '_').lower()
    )
    logger.debug('inserting datas in couchDB...')
    cb.set(key, data)
    logger.debug('Done.')
    logger.debug('getting datas just inserted in couchDB...')
    result = cb.get(key)
    pprint(result.value, indent=4)
    logger.debug('Done.')
    logger.debug('deleting datas just inserted in couchDB...')
    cb.delete(key)
    logger.debug('Done.')


def send_message(queue_name, message):
    """
    Send the message in the queue passed in parameter.
    :param queue_name: the name of the queue in which we have to send the JSON message.
    :param message: Must be a dictionnary !
    """
    credentials = pika.PlainCredentials(QUEUE_USER, QUEUE_PASSWORD)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(QUEUE_URL, QUEUE_PORT, QUEUE_CONTEXT_ROOT, credentials))
    channel = connection.channel()
    channel.queue_declare(queue=queue_name)
    channel.basic_publish(exchange='',
                          routing_key=queue_name,
                          body=json.dumps(message),
                          properties=pika.BasicProperties(content_type='application/json'))
    connection.close()
