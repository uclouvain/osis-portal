
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
from django.db import models
from django.contrib import admin


class OfferYearDomainAdmin(admin.ModelAdmin):
    list_display = ('domain', 'offer_year')
    fieldsets = ((None, {'fields': ('domain', 'offer_year')}),)
    raw_id_fields = ('domain', 'offer_year')
    search_fields = ['domain__name', 'offer_year__acronym']

<<<<<<< HEAD:admission/models/offer_year_domain.py
=======
from couchbase import Couchbase
from pprint import pprint
import json
import logging
from django.conf import settings
import pika
from frontoffice.settings import QUEUE_URL, QUEUE_USER, QUEUE_PASSWORD, QUEUE_PORT, QUEUE_CONTEXT_ROOT
>>>>>>> 99caff2e71419785740131cce077b9617c6627cf:frontoffice/queue/queue_actions.py

class OfferYearDomain(models.Model):
    external_id = models.CharField(max_length=100, blank=True, null=True)
    domain = models.ForeignKey('reference.Domain', blank=True, null=True)
    offer_year = models.ForeignKey('base.OfferYear', blank=True, null=True)

    def __str__(self):
        return u"%s - %s" % (self.domain, self.offer_year)

<<<<<<< HEAD:admission/models/offer_year_domain.py
=======
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
>>>>>>> 99caff2e71419785740131cce077b9617c6627cf:frontoffice/queue/queue_actions.py
