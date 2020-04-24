#!/usr/bin/env false

import config
import Worker

class VkWorker(Worker):
    def __init__(self, collector):
        self.vk_collector = collector
        super().__init__(config.rabbitmq.work_queue)

    def process_message(self, message):
        # Split message into parts
        user, depth = [int(x) for x in message.split()]

        # If current user recursion depth is less than configured, collect user data
        if (depth <= config.collector.depth):
            # Collect user data and retrieve user IDs of users whose data should be collected recursively
            users = self.vk_collector.collect_user(user)

            # If current recursion depth is less than maximum, then put tasks for recursive processing of returned users
            if (depth < config.collector.depth):
                for user in users:
                    self.produce_message("{} {}".format(user, depth + 1))
