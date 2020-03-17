#!/usr/bin/env false

import pika
import config

class Worker(object):
    def __init__(self, collector):
        self.vk_collector = collector
        self.rabbit_connect()

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

    def message_callback(self, channel, method, properties, body):
        # Convert body to UTF-8 string
        body = body.decode('utf-8')

        # Process message
        self.process_message(body)

        # Tell RabbitMQ that we processed message
        channel.basic_ack(delivery_tag = method.delivery_tag)

    def process_message(self, message):
        # Split message into parts
        user, depth = [int(x) for x in message.split()]

        # If current user recursion depth is less than configured, collect user data
        if (config.collector.depth <= int(depth)):
            # Collect user data and retrieve user IDs of users whose data should be collected recursively
            print ("Processing user {}".format(user))
            users = self.vk_collector.collect_user(user)

            # If current recursion depth is less than maximum, then put tasks for recursive processing of returned users
            if (config.collector.depth < depth):
                for user in users:
                    self.produce_message("{} {}".format(user, depth + 1))
        
    def produce_message(self, message):
        # Put message into queue
        self.channel.basic_publish(exchange='',
                      routing_key=config.rabbitmq.queue,
                      body=message.encode('utf-8'),
                      properties=pika.BasicProperties(
                         delivery_mode = 2, # Make message persistent
                      ))
