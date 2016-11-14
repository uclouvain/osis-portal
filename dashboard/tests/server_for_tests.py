##############################################################################
#
# OSIS stands for Open Student Information System. It's an application
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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import pika


class ServerRPCForTest(object):
    def __init__(self, queue_name, response_to_send, key):
        self.response = response_to_send
        self.queue_name = queue_name
        self.key = key
        self.initialize_server()

    def initialize_server(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
                host='localhost'))
        channel = self.connection.channel()
        channel.queue_declare(queue=self.queue_name)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(self.on_request, queue=self.queue_name)
        channel.start_consuming()

    def generate_response(self):
        return self.response

    def on_request(self, ch, method, props, body):
        if body.decode("utf-8") == self.key:
            response = self.generate_response()
            ch.basic_publish(exchange='',
                             routing_key=props.reply_to,
                             properties=pika.BasicProperties(correlation_id=props.correlation_id),
                             body=response)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        self.connection.close()


def launch_server_rpc(queue_name, response_to_send, key):
    ServerRPCForTest(queue_name=queue_name, response_to_send=response_to_send, key=key)
