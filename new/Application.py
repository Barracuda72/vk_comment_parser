#!/usr/bin/env python3

from LoginWorker import LoginWorker

class Application(object):
    def __init__(self):
        self.worker = None 

    def run(self):
        self.worker = LoginWorker()

if (__name__ == '__main__'):
    app = Application()
    app.run()
