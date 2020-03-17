#!/usr/bin/env false

import vk_api
import time
import hashlib
import config

class Collector(object):
    def __init__(self, login, password, proxy = None):
        proxy_dict = {
            'http' : proxy,
            'https' : proxy,
        }

        login_hash = hashlib.sha256(login.encode("utf-8")).hexdigest()
        vk_session = vk_api.VkApi(login, password, config_filename = "vk_config." + login_hash + ".json")
        vk_session.http.proxies = proxy_dict

        try:
            vk_session.auth()
            print("auth_success")
        except vk_api.AuthError as error:
            print(error)
            raise error

        self.tools = vk_api.VkTools(vk_session)
        self.vk = vk_session.get_api()

    # Return user object
    def _get_user(self, user_id):
        return self.vk.users.get(user_ids=user_id, name_case="Nom")[0]

    # Return user posts
    def _get_user_wall_posts(self, user_id):
        return self.tools.get_all('wall.get', config.collector.max_post_count, {'owner_id': user_id})['items']

    # Return comments for post
    def _get_comments_for_post(self, user_id, post_id):
        return self.tools.get_all('wall.getComments', config.collector.max_comment_count, {'owner_id': user_id, 'post_id': post_id})['items']

    def collect_user(self, user):
        print ("Collecting user {}".format(user))
        vk_user = self._get_user(user)
        print (vk_user)
        return []
