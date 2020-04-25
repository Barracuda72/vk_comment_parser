#!/usr/bin/env false

from kombu import Connection, Exchange, Producer, Queue
import config

class Populator(object):
    def __init__(self):
        url = "amqp://{}:{}@{}:5672/".format(config.rabbitmq.username, config.rabbitmq.password, config.rabbitmq.host)
        self.connection = Connection(url)
        self.channel = self.connection.channel()

        self.exchange = Exchange("", type="direct", durable=True)

        self.producer = Producer(exchange=self.exchange, channel=self.channel, serializer="pickle")

        self.login_queue = Queue(name=config.rabbitmq.login_queue, exchange=self.exchange, routing_key=config.rabbitmq.login_queue, durable=True)
        self.login_queue.maybe_bind(self.connection)
        self.login_queue.declare()

        self.work_queue = Queue(name=config.rabbitmq.work_queue, exchange=self.exchange, routing_key=config.rabbitmq.work_queue, durable=True)
        self.work_queue.maybe_bind(self.connection)
        self.work_queue.declare()

    def __del__(self):
        self.connection.close()

    def _publish(self, queue_name, data):
        self.producer.publish(data.encode('utf-8'), routing_key=queue_name, retry=True, delivery_mode=2)

    def publish_login(self, credentials):
        self._publish(config.rabbitmq.login_queue, credentials)

    def publish_work(self, work):
        self._publish(config.rabbitmq.work_queue, work)
