#!/usr/bin/env python3

import pika
import sys
import config

credentials = pika.PlainCredentials(config.rabbitmq.username, config.rabbitmq.password)
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', credentials=credentials))
channel = connection.channel()

channel.queue_declare(queue=config.rabbitmq.queue, durable=True)

message = ' '.join(sys.argv[1:]) or "Hello World!"
channel.basic_publish(exchange='',
                      routing_key=config.rabbitmq.queue,
                      body=message.encode('utf-8'),
                      properties=pika.BasicProperties(
                         delivery_mode = 2, # make message persistent
                      ))
print(" [x] Sent %r" % (message,))
connection.close()
