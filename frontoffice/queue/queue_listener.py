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
import pika
import uuid
from pika.exceptions import ConnectionClosed
from django.conf import settings
import threading
import logging

logger = logging.getLogger(settings.DEFAULT_LOGGER)
DEFAULT_TIMEOUT = 30


class Client(object):

    def __init__(self, queue_name, call_timeout=DEFAULT_TIMEOUT):
        self.paper_sheet_queue = queue_name
        credentials = pika.PlainCredentials(settings.QUEUES.get('QUEUE_USER'),
                                            settings.QUEUES.get('QUEUE_PASSWORD'))
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(settings.QUEUES.get('QUEUE_URL'),
                                                                            settings.QUEUES.get('QUEUE_PORT'),
                                                                            settings.QUEUES.get('QUEUE_CONTEXT_ROOT'),
                                                                            credentials))
        self.timed_out = False
        self.connection.add_timeout(call_timeout, self.on_timed_out)
        self.channel = self.connection.channel()

        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(self.on_response, no_ack=True,
                                   queue=self.callback_queue)

    def on_timed_out(self):
        self.timed_out = True

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, message):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(exchange='',
                                   routing_key=self.paper_sheet_queue,
                                   properties=pika.BasicProperties(
                                       reply_to=self.callback_queue,
                                       correlation_id=self.corr_id,
                                       content_type='application/json'),
                                   body=message)
        while self.response is None and not self.timed_out:
            self.connection.process_data_events()
        return self.response


class ScoresSheetClient(Client):
    def __init__(self):
        queue_name = settings.QUEUES.get('QUEUES_NAME').get('PAPER_SHEET')
        score_sheet_timeout = settings.QUEUES.get('RPC_QUEUES_TIMEOUT').get('PAPER_SHEET')
        super(ScoresSheetClient, self).__init__(queue_name=queue_name, call_timeout=score_sheet_timeout)


class PerformanceClient(Client):
    def __init__(self):
        queue_name = settings.QUEUES.get('QUEUES_NAME').get('STUDENT_PERFORMANCE')
        performance_timeout = settings.QUEUES.get('RPC_QUEUES_TIMEOUT').get('STUDENT_PERFORMANCE')
        super(PerformanceClient, self).__init__(queue_name=queue_name, call_timeout=performance_timeout)


class AttestationListClient(Client):
    def __init__(self):
        queue_name = settings.QUEUES.get('QUEUES_NAME').get('ATTESTATION_LIST')
        super(AttestationListClient, self).__init__(queue_name=queue_name)


class AttestationClient(Client):
    def __init__(self):
        queue_name = settings.QUEUES.get('QUEUES_NAME').get('ATTESTATION')
        super(AttestationListClient, self).__init__(queue_name=queue_name)


class SynchronousConsumerThread(threading.Thread):
    def __init__(self, queue_name, callback, *args, **kwargs):
        super(SynchronousConsumerThread, self).__init__(*args, **kwargs)

        self._queue_name = queue_name
        self.callback = callback
        self.daemon = True

    def run(self):
        listen_queue_synchronously(self._queue_name, self.callback)


def listen_queue_synchronously(queue_name, callback, counter=3):

    def on_message(channel, method_frame, header_frame, body):
        callback(body)
        channel.basic_ack(delivery_tag=method_frame.delivery_tag)

    if counter == 0:
        return # Stop the function
    logger.debug("Connecting to {0} (queue name = {1})...".format(settings.QUEUES.get('QUEUE_URL'), queue_name))
    credentials = pika.PlainCredentials(settings.QUEUES.get('QUEUE_USER'), settings.QUEUES.get('QUEUE_PASSWORD'))
    connection = pika.BlockingConnection(pika.ConnectionParameters(settings.QUEUES.get('QUEUE_URL'),
                                                                   settings.QUEUES.get('QUEUE_PORT'),
                                                                   settings.QUEUES.get('QUEUE_CONTEXT_ROOT'),
                                                                   credentials))
    logger.debug("Connection opened.")
    logger.debug("Creating a new channel...")
    channel = connection.channel()
    logger.debug("Channel opened.")
    logger.debug("Declaring queue (if it doesn't exist yet)...")
    channel.queue_declare(queue=queue_name,
                          durable=True,
                          # exclusive=False,
                          # auto_delete=False,
                          )
    logger.debug("Queue declared.")
    # channel.basic_qos(prefetch_count=1)
    logger.debug("Declaring on message callback...")
    channel.basic_consume(on_message, queue_name)
    logger.debug("Done.")
    try:
        logger.debug("Ready to synchronously consume messages")
        channel.start_consuming()
        counter = 3
    except KeyboardInterrupt:
        channel.stop_consuming()
    except ConnectionClosed:
        listen_queue_synchronously(queue_name, callback, counter - 1)
    connection.close()


def listen_queue(queue_name, callback):
    """
    Create a thread in which a queue is created (from the queue name passed in parameter) and listened.
    :param queue_name: The name of the queue to create and to listen.
    :param callback: The action to perform when a message is consumed. (It is a function).
    """
    if not callable(callback) :
        raise Exception("Error ! The second parameter of listen_queue MUST BE a function !")
    connection_parameters = {
        'queue_name' : queue_name,
        'queue_url' : settings.QUEUES.get('QUEUE_URL'),
        'queue_user' : settings.QUEUES.get('QUEUE_USER'),
        'queue_password' : settings.QUEUES.get('QUEUE_PASSWORD'),
        'queue_port' : settings.QUEUES.get('QUEUE_PORT'),
        'queue_context_root' : settings.QUEUES.get('QUEUE_CONTEXT_ROOT'),
        'exchange' : queue_name,
        'routing_key' : '',
    }
    consumer_thread = ConsumerThread(connection_parameters, callback)
    try:
        consumer_thread.daemon = True
        consumer_thread.start()
    except KeyboardInterrupt :
        consumer_thread.stop()


class ConsumerThread(threading.Thread):
    def __init__(self, connection_parameters, callback, *args, **kwargs):
        super(ConsumerThread, self).__init__(*args, **kwargs)

        self._queue_name = connection_parameters['queue_name']
        self._queue_url = connection_parameters['queue_url']
        self._queue_user = connection_parameters['queue_user']
        self._queue_password = connection_parameters['queue_password']
        self._queue_port = connection_parameters['queue_port']
        self._queue_context_root = connection_parameters['queue_context_root']
        self._exchange = connection_parameters['exchange']
        self._routing_key = connection_parameters['routing_key']
        self.callback_func = callback

    # Not necessarily a method.
    def callback_func(self, channel, method, properties, body):
        logger.debug("{} received '{}'".format(self.name, body))

    def run(self):
        connection_parameters = {
            'queue_name' : self._queue_name,
            'queue_url' : self._queue_url,
            'queue_user' : self._queue_user,
            'queue_password' : self._queue_password,
            'queue_port' : self._queue_port,
            'queue_context_root' : self._queue_context_root,
            'exchange' : self._exchange,
            'routing_key' : self._routing_key,
        }
        example = ExampleConsumer(connection_parameters=connection_parameters, callback=self.callback_func)
        example.run()


class ExampleConsumer(object):
    """
    This is an example consumer that will handle unexpected interactions
    with RabbitMQ such as channel and connection closures.

    If RabbitMQ closes the connection, it will reopen it. You should
    look at the output, as there are limited reasons why the connection may
    be closed, which usually are tied to permission related issues or
    socket timeouts.

    If the channel is closed, it will indicate a problem with one of the
    commands that were issued and that should surface in the output as well.
    """
    EXCHANGE = None
    EXCHANGE_TYPE = 'topic'
    ROUTING_KEY = None

    def __init__(self, connection_parameters=None, callback = None):
        """
        Create a new instance of the consumer class, passing in the AMQP
        URL used to connect to RabbitMQ.

        :param str amqp_url: The AMQP url to connect with
        """
        self._connection = None
        self._channel = None
        self._closing = False
        self._consumer_tag = None
        self._connection_parameters = connection_parameters
        self.EXCHANGE = connection_parameters['exchange']
        self.ROUTING_KEY = connection_parameters['routing_key']
        self.callback_func = callback

    def connect(self):
        """
        This method connects to RabbitMQ, returning the connection handle.
        When the connection is established, the on_connection_open method
        will be invoked by pika.

        :rtype: pika.SelectConnection
        """
        logger.debug('Connecting to %s' % (self._connection_parameters['queue_url']))
        credentials = pika.PlainCredentials(self._connection_parameters['queue_user'], self._connection_parameters['queue_password'])
        return pika.SelectConnection(pika.ConnectionParameters(self._connection_parameters['queue_url'],
                                                               self._connection_parameters['queue_port'],
                                                               self._connection_parameters['queue_context_root'],
                                                               credentials),
                                     self.on_connection_open,
                                     stop_ioloop_on_close=False)

    def on_connection_open(self, unused_connection):
        """
        This method is called by pika once the connection to RabbitMQ has
        been established. It passes the handle to the connection object in
        case we need it, but in this case, we'll just mark it unused.

        :type unused_connection: pika.SelectConnection
        """
        logger.debug('Connection opened')
        self.add_on_connection_close_callback()
        self.open_channel()

    def add_on_connection_close_callback(self):
        """
        This method adds an on close callback that will be invoked by pika
        when RabbitMQ closes the connection to the publisher unexpectedly.
        """
        logger.debug('Adding connection close callback')
        self._connection.add_on_close_callback(self.on_connection_closed)

    def on_connection_closed(self, connection, reply_code, reply_text):
        """
        This method is invoked by pika when the connection to RabbitMQ is
        closed unexpectedly. Since it is unexpected, we will reconnect to
        RabbitMQ if it disconnects.

        :param pika.connection.Connection connection: The closed connection obj
        :param int reply_code: The server provided reply_code if given
        :param str reply_text: The server provided reply_text if given
        """
        self._channel = None
        if self._closing:
            logger.warning('Closing connection without retry')
            self._connection.ioloop.stop()
        else:
            logger.warning('Connection closed, reopening in 5 seconds: (%s) %s' % (reply_code, reply_text))
            self._connection.add_timeout(5, self.reconnect)

    def reconnect(self):
        """
        Will be invoked by the IOLoop timer if the connection is
        closed. See the on_connection_closed method.
        """
        # This is the old connection IOLoop instance, stop its ioloop
        self._connection.ioloop.stop()

        if not self._closing:

            # Create a new connection
            self._connection = self.connect()

            # There is now a new connection, needs a new ioloop to run
            self._connection.ioloop.start()

    def open_channel(self):
        """
        Open a new channel with RabbitMQ by issuing the Channel.Open RPC
        command. When RabbitMQ responds that the channel is open, the
        on_channel_open callback will be invoked by pika.
        """
        logger.debug('Creating a new channel')
        self._connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel):
        """
        This method is invoked by pika when the channel has been opened.
        The channel object is passed in so we can make use of it.

        Since the channel is now open, we'll declare the exchange to use.

        :param pika.channel.Channel channel: The channel object
        """
        logger.debug('Channel opened')
        self._channel = channel
        self.add_on_channel_close_callback()
        self.setup_exchange(self.EXCHANGE)

    def add_on_channel_close_callback(self):
        """
        This method tells pika to call the on_channel_closed method if
        RabbitMQ unexpectedly closes the channel.
        """
        logger.debug('Adding channel close callback')
        self._channel.add_on_close_callback(self.on_channel_closed)

    def on_channel_closed(self, channel, reply_code, reply_text):
        """
        Invoked by pika when RabbitMQ unexpectedly closes the channel.
        Channels are usually closed if you attempt to do something that
        violates the protocol, such as re-declare an exchange or queue with
        different parameters. In this case, we'll close the connection
        to shutdown the object.

        :param pika.channel.Channel: The closed channel
        :param int reply_code: The numeric reason the channel was closed
        :param str reply_text: The text reason the channel was closed
        """
        logger.debug('Channel %i was closed: (%s) %s' % (channel, reply_code, reply_text))
        self._connection.close()

    def setup_exchange(self, exchange_name):
        """
        Setup the exchange on RabbitMQ by invoking the Exchange.Declare RPC
        command. When it is complete, the on_exchange_declareok method will
        be invoked by pika.

        :param str|unicode exchange_name: The name of the exchange to declare
        """
        logger.debug('Declaring exchange %s' % (exchange_name))
        self._channel.exchange_declare(self.on_exchange_declareok,
                                       exchange_name,
                                       self.EXCHANGE_TYPE)

    def on_exchange_declareok(self, unused_frame):
        """
        Invoked by pika when RabbitMQ has finished the Exchange.Declare RPC
        command.

        :param pika.Frame.Method unused_frame: Exchange.DeclareOk response frame
        """
        logger.debug('Exchange declared')
        self.setup_queue(self._connection_parameters['queue_name'])

    def setup_queue(self, queue_name):
        """
        Setup the queue on RabbitMQ by invoking the Queue.Declare RPC
        command. When it is complete, the on_queue_declareok method will
        be invoked by pika.

        :param str|unicode queue_name: The name of the queue to declare.
        """
        logger.debug('Declaring queue %s' % (queue_name))
        self._channel.queue_declare(self.on_queue_declareok, queue_name)

    def on_queue_declareok(self, method_frame):
        """
        Method invoked by pika when the Queue.Declare RPC call made in
        setup_queue has completed. In this method we will bind the queue
        and exchange together with the routing key by issuing the Queue.Bind
        RPC command. When this command is complete, the on_bindok method will
        be invoked by pika.

        :param pika.frame.Method method_frame: The Queue.DeclareOk frame
        """
        logger.debug('Binding %s to %s with %s' % (self.EXCHANGE, self._connection_parameters['queue_name'], self.ROUTING_KEY))
        self._channel.queue_bind(self.on_bindok, self._connection_parameters['queue_name'],
                                 self.EXCHANGE, self.ROUTING_KEY)

    def on_bindok(self, unused_frame):
        """
        Invoked by pika when the Queue.Bind method has completed. At this
        point we will start consuming messages by calling start_consuming
        which will invoke the needed RPC commands to start the process.

        :param pika.frame.Method unused_frame: The Queue.BindOk response frame
        """
        logger.debug('Queue bound')
        self.start_consuming()

    def start_consuming(self):
        """
        This method sets up the consumer by first calling
        add_on_cancel_callback so that the object is notified if RabbitMQ
        cancels the consumer. It then issues the Basic.Consume RPC command
        which returns the consumer tag that is used to uniquely identify the
        consumer with RabbitMQ. We keep the value to use it when we want to
        cancel consuming. The on_message method is passed in as a callback pika
        will invoke when a message is fully received.
        """
        logger.debug('Issuing consumer related RPC commands')
        self.add_on_cancel_callback()
        self._consumer_tag = self._channel.basic_consume(self.on_message,
                                                         self._connection_parameters['queue_name'])

    def add_on_cancel_callback(self):
        """
        Add a callback that will be invoked if RabbitMQ cancels the consumer
        for some reason. If RabbitMQ does cancel the consumer,
        on_consumer_cancelled will be invoked by pika.
        """
        logger.debug('Adding consumer cancellation callback')
        self._channel.add_on_cancel_callback(self.on_consumer_cancelled)

    def on_consumer_cancelled(self, method_frame):
        """
        Invoked by pika when RabbitMQ sends a Basic.Cancel for a consumer
        receiving messages.

        :param pika.frame.Method method_frame: The Basic.Cancel frame
        """
        logger.debug('Consumer was cancelled remotely, shutting down: %r' % (method_frame))
        if self._channel:
            self._channel.close()

    def on_message(self, unused_channel, basic_deliver, properties, body):
        """Invoked by pika when a message is delivered from RabbitMQ. The
        channel is passed for your convenience. The basic_deliver object that
        is passed in carries the exchange, routing key, delivery tag and
        a redelivered flag for the message. The properties passed in is an
        instance of BasicProperties with the message properties and the body
        is the message that was sent.

        :param pika.channel.Channel unused_channel: The channel object
        :param pika.Spec.Basic.Deliver: basic_deliver method
        :param pika.Spec.BasicProperties: properties
        :param str|unicode body: The message body
        """
        logger.debug(self._connection_parameters['queue_name'] + ' : Received message # %s from %s' % (basic_deliver.delivery_tag, properties.app_id))
        logger.debug('Executing callback function on the received message...')
        self.callback_func(body)
        self.acknowledge_message(basic_deliver.delivery_tag)

    def acknowledge_message(self, delivery_tag):
        """Acknowledge the message delivery from RabbitMQ by sending a
        Basic.Ack RPC method for the delivery tag.

        :param int delivery_tag: The delivery tag from the Basic.Deliver frame
        """
        logger.debug('Acknowledging message %s' % (delivery_tag))
        self._channel.basic_ack(delivery_tag)

    def stop_consuming(self):
        """
        Tell RabbitMQ that you would like to stop consuming by sending the
        Basic.Cancel RPC command.
        """
        if self._channel:
            logger.debug('Sending a Basic.Cancel RPC command to RabbitMQ')
            self._channel.basic_cancel(self.on_cancelok, self._consumer_tag)

    def on_cancelok(self, unused_frame):
        """
        This method is invoked by pika when RabbitMQ acknowledges the
        cancellation of a consumer. At this point we will close the channel.
        This will invoke the on_channel_closed method once the channel has been
        closed, which will in-turn close the connection.

        :param pika.frame.Method unused_frame: The Basic.CancelOk frame
        """
        logger.debug('RabbitMQ acknowledged the cancellation of the consumer')
        self.close_channel()

    def close_channel(self):
        """
        Call to close the channel with RabbitMQ cleanly by issuing the
        Channel.Close RPC command.
        """
        logger.debug('Closing the channel')
        self._channel.close()

    def run(self):
        """
        Run the example consumer by connecting to RabbitMQ and then
        starting the IOLoop to block and allow the SelectConnection to operate.
        """
        self._connection = self.connect()
        self._connection.ioloop.start()

    def stop(self):
        """
        Cleanly shutdown the connection to RabbitMQ by stopping the consumer
        with RabbitMQ. When RabbitMQ confirms the cancellation, on_cancelok
        will be invoked by pika, which will then closing the channel and
        connection. The IOLoop is started again because this method is invoked
        when CTRL-C is pressed raising a KeyboardInterrupt exception. This
        exception stops the IOLoop which needs to be running for pika to
        communicate with RabbitMQ. All of the commands issued prior to starting
        the IOLoop will be buffered but not processed.
        """
        logger.debug('Stopping')
        self._closing = True
        self.stop_consuming()
        self._connection.ioloop.start()
        logger.debug('Stopped')

    def close_connection(self):
        """This method closes the connection to RabbitMQ."""
        logger.debug('Closing connection')
        self._connection.close()
