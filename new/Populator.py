#!/usr/bin/env false

import pika
import config

class Populator(object):
    def __init__(self):
        credentials = pika.PlainCredentials(config.rabbitmq.username, config.rabbitmq.password)
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=config.rabbitmq.host, credentials=credentials))
        self.channel = self.connection.channel()

        self.channel.queue_declare(queue=config.rabbitmq.login_queue, durable=True)
        self.channel.queue_declare(queue=config.rabbitmq.work_queue, durable=True)

    def __del__(self):
        self.connection.close()

    def _publish(self, queue_name, data):
        self.channel.basic_publish(exchange='',
                      queue_name,
                      body=data.encode('utf-8'),
                      properties=pika.BasicProperties(
                         delivery_mode = 2, # make message persistent
                      ))

    def publish_login(self, credentials):
        self._publish(config.rabbitmq.login_queue, credentials)

    def publish_work(self, work):
        self._publish(config.rabbitmq.work_queue, work)
