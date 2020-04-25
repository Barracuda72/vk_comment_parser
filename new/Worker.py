#!/usr/bin/env false

from threading import Thread
from multiprocessing import Queue
import pika
import config

class Worker(object):
    def __init__(self, queue_name):
        self.queue_name = queue_name
        self.send_queue = Queue()
        self.threads = []
        self.rabbit_connect()

    def rabbit_connect(self):
        # Create plain credentials
        credentials = pika.PlainCredentials(config.rabbitmq.username, config.rabbitmq.password)

        # Establish connection
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=config.rabbitmq.host, credentials=credentials))
        
        # Create communication channel for read
        self.channel_read = self.connection.channel()

        # And a separete one for write
        self.channel_write = self.connection.channel()

        # Declare durable queue (its content will be saved in case of something going wrong, so we won't lose unprocessed messages)
        self.channel_read.queue_declare(queue=self.queue_name, durable=True)

        # Same for writing channel
        self.channel_write.queue_declare(queue=self.queue_name, durable=True)

        # Tell RabbitMQ that we should confirm message processing and will consume only one message at a time
        self.channel_read.basic_qos(prefetch_count=1)

        # Set callback function for our queue
        self.channel_read.basic_consume(on_message_callback=self.message_callback,
                      queue=self.queue_name)

        # Start consuming
        self.channel_read.start_consuming()

    def message_callback(self, channel, method, properties, body):
        # Spawn separate thread to handle all the work, so Pika can properly communicate with RabbitMQ
        # TODO: BEWARE OF RACE CONDITIONS IN CASE YOU INCREASE prefetch_count!
        t = Thread(target=self.decode_message, args=(channel, method, body))
        t.start()
        self.threads.append(t)

    def decode_message(self, channel, method, body):
        # Convert body to UTF-8 string
        body = body.decode('utf-8')

        # Process message
        self.process_message(body)

        # Tell RabbitMQ that we processed the message
        cb = lambda: self.ack_message(channel, method.delivery_tag)
        self.connection.add_callback_threadsafe(cb)

    def ack_message(self, channel, delivery_tag):
        if (channel.is_open):
            channel.basic_ack(delivery_tag = delivery_tag)
        else:
            pass
        
        # Send all messages that were produced
        print ("Send remaining messages")
        while not self.send_queue.empty():
            message = self.send_queue.get()
            print (message)
            self.send_message(message)

    def process_message(self, message):
        # Generic message processing stub
        print ("Message from queue '{}': '{}'".format(self.queue_name, message))
        
    def produce_message(self, message):
        # Put message into queue
        self.send_queue.put(message)

    def send_message(self, message):
        self.channel_write.basic_publish(exchange='',
                      routing_key=self.queue_name,
                      body=message.encode('utf-8'),
                      properties=pika.BasicProperties(
                         delivery_mode = 2, # Make message persistent
                      ))
