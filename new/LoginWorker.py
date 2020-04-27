#!/usr/bin/env false

from multiprocessing import Process
import config
from Worker import Worker
from VkWorker import VkWorker
import time

class LoginWorker(Worker):
    def __init__(self):
        self.workers = []
        self.started = False
        super().__init__(config.rabbitmq.login_queue)

    def work(self, login, password, proxy=None, first=False):
        if (not first):
            # If we aren't first, sleep a bit and let the first one create database
            time.sleep(1)
        print ("Spawning thread {}, proxy {}".format(login, proxy))
        # Move here to cope with psycopg restriction on being unable to use same session in different processes
        from Collector import Collector
        collector = Collector(login, password, proxy)
        worker = VkWorker(collector)

    def process_message(self, message):
        # Split message into parts
        login, password = message.split()[:2]
        p = Process(target = self.work, args = (login, password, "socks5://localhost:9050", not self.started,))
        p.start()
        self.workers.append(p)
        self.started = True
