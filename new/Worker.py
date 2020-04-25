#!/usr/bin/env false

import socket
from threading import Thread
from kombu import Connection, Exchange, Producer, Queue, Consumer
import config

class Worker(object):
    def __init__(self, queue_name):
        self.queue_name = queue_name
        self.serializer = "pickle"
        self.rabbit_connect()
        self.poll_messages()

    def rabbit_connect(self):
        url = "amqp://{}:{}@{}:5672/".format(config.rabbitmq.username, config.rabbitmq.password, config.rabbitmq.host)
        self.connection = Connection(url)
        self.channel = self.connection.channel()
        self.channel.basic_qos(prefetch_size=0, prefetch_count=1, a_global=False)
        self.exchange = Exchange("", type="direct", durable=True)

        self.queue = Queue(name=self.queue_name, exchange=self.exchange, routing_key=self.queue_name)
        self.queue.maybe_bind(self.connection)
        self.queue.declare()

        self.producer = Producer(exchange=self.exchange, channel=self.channel, serializer=self.serializer)
        self.consumer = Consumer(self.connection, queues=self.queue, callbacks=[self.message_callback], accept=["application/x-python-serialize"])
        #self.consumer.qos(prefetch_count = 1)

    def poll_messages(self):
        while True:
            try:
                self.process_messages()
            except self.connection.connection_errors:
                pass

    def process_messages(self):
        self.connection = self.renew_connection()
        while True:
            try:
                self.connection.drain_events(timeout=5)
            except socket.timeout:
                pass

    def renew_connection(self):
        new_connection = self.connection.clone()
        new_connection.ensure_connection(max_retries=10)
        self.channel = new_connection.channel()
        self.channel.basic_qos(prefetch_size=0, prefetch_count=1, a_global=False)
        self.consumer.revive(self.channel)
        self.producer.revive(self.channel)
        self.consumer.consume()
        return new_connection

    def message_callback(self, body, message):
        # Convert body to UTF-8 string
        body = body.decode('utf-8')

        # Process message
        self.process_message(body)

        # Tell RabbitMQ that we processed the message
        message.ack()

    def process_message(self, message):
        # Generic message processing stub
        print ("Message from queue '{}': '{}'".format(self.queue_name, message))
        
    def produce_message(self, message):
        self.producer.publish(message.encode('utf-8'), routing_key=self.queue_name, retry=True, delivery_mode=2)
