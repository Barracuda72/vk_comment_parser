#!/usr/bin/env python3

import pika
import time

import config

credentials = pika.PlainCredentials(config.rabbitmq.username, config.rabbitmq.password)
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', credentials=credentials))
channel = connection.channel()

channel.queue_declare(queue=config.rabbitmq.queue, durable=True)
print(' [*] Waiting for messages. To exit press CTRL+C')

def callback(ch, method, properties, body):
    body = body.decode('utf-8')
    print (" [x] Received %r" % (body,))
    time.sleep( body.count('.') )
    print (" [x] Done")
    ch.basic_ack(delivery_tag = method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback,
                      queue=config.rabbitmq.queue)

channel.start_consuming()
