#!/usr/bin/env python3

from multiprocessing import Pool
from Worker import Worker
from Collector import Collector
import config
import credentials

class Application(object):
    def __init__(self):
        self.creds = credentials.login_list
        self.pool_size = len(self.creds)

    def work(self, login, password, proxy=None):
        print ("Spawning thread {}, proxy {}".format(login, proxy))
        collector = Collector(login, password, proxy)
        worker = Worker(collector)

    def run(self):
        with Pool(self.pool_size) as p:
            p.starmap(self.work, self.creds)

if (__name__ == '__main__'):
    app = Application()
    app.run()
