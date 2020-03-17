#!/usr/bin/env false

import pika
import config

class Worker(object):
    demo = True

    def __init__(self, login, password, proxy):
        self.login = login
        self.password = password
        self.proxy = proxy

        if (not self.demo):
            self.vk_connect(login, password, proxy)
            self.rabbit_connect()
        else:
            self.run_demo()

    def rabbit_connect(self):
        # Create plain credentials
        credentials = pika.PlainCredentials(config.rabbitmq.username, config.rabbitmq.password)

        # Establish connection
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=config.rabbitmq.host, credentials=credentials))
        
        # Create communication channel
        self.channel = connection.channel()

        # Declare durable queue (its content will be saved in case of something going wrong, so we won't lose unprocessed messages)
        self.channel.queue_declare(queue=config.rabbitmq.queue, durable=True)

        # Tell RabbitMQ that we should confirm message processing and will consume only one message at a time
        self.channel.basic_qos(prefetch_count=1)

        # Set callback function for our queue
        self.channel.basic_consume(self.message_callback,
                      queue=config.rabbitmq.queue)

        # Start consuming
        self.channel.start_consuming()

    def vk_connect(self, login, password, proxy):
        # TODO
        pass

    def message_callback(self, channel, method, properties, body):
        # Convert body to UTF-8 string
        body = body.decode('utf-8')

        # Process message
        self.process_message(body)

        # Tell RabbitMQ that we processed message
        channel.basic_ack(delivery_tag = method.delivery_tag)

    def process_message(self, message):
        user, depth = message.split()
        # TODO
        #if (config.collector.depth <= int(depth)):
        if (config.user_depth <= int(depth)):
            print ("Processing user {}".format(user))
        
    def run_demo(self):
        import sys
        import random
        
        filename = sys.argv[1]

        user_ids = [x.strip() for x in open(filename, "r").readlines()]

        for user_id in user_ids:
            self.process_message("{} {}".format(str(user_id), random.randint(0, 10)))
