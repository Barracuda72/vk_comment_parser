#!/usr/bin/env python3

import pika
import sys
import config

if (len(sys.argv) < 2):
    print ("Provide file with IDs!")
    sys.exit(1)


filename = sys.argv[1]

user_ids = [x.strip() for x in open(filename, "r").readlines()]

credentials = pika.PlainCredentials(config.rabbitmq.username, config.rabbitmq.password)
connection = pika.BlockingConnection(pika.ConnectionParameters(host=config.rabbitmq.host, credentials=credentials))
channel = connection.channel()

channel.queue_declare(queue=config.rabbitmq.queue, durable=True)

for user_id in user_ids:
    message = "{} {}".format(user_id, 0)
    channel.basic_publish(exchange='',
                      routing_key=config.rabbitmq.queue,
                      body=message.encode('utf-8'),
                      properties=pika.BasicProperties(
                         delivery_mode = 2, # make message persistent
                      ))
connection.close()
