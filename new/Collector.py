#!/usr/bin/env false

import vk_api
import time
import hashlib
import config
import database as db
from datetime import datetime

class Collector(object):
    user_fields = """
    photo_id, verified, sex, bdate, city, country, home_town, has_photo, photo_50, photo_100, photo_200_orig, photo_200, photo_400_orig, 
    photo_max, photo_max_orig, online, domain, has_mobile, contacts, site, education, universities, schools, status, last_seen, 
    followers_count, common_count, occupation, nickname, relatives, relation, personal, connections, exports, activities, interests, 
    music, movies, tv, books, games, about, quotes, can_post, can_see_all_posts, can_see_audio, can_write_private_message, 
    can_send_friend_request, is_favorite, is_hidden_from_feed, timezone, screen_name, maiden_name, crop_photo, is_friend, friend_status, 
    career, military, blacklisted, blacklisted_by_me, can_be_invited_group
    """

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
        self.user_fields = self.user_fields.replace(" ", "").replace("\n", "")

    # Return user object
    def _get_user(self, user_id):
        return self.vk.users.get(user_ids=user_id, name_case="Nom", fields=self.user_fields)[0]

    # Return user posts
    def _get_user_wall_posts(self, user_id):
        return self.tools.get_all('wall.get', config.collector.max_post_count, {'owner_id': user_id})['items']

    # Return comments for post
    def _get_comments_for_post(self, user_id, post_id):
        return self.tools.get_all('wall.getComments', config.collector.max_comment_count, {'owner_id': user_id, 'post_id': post_id})['items']

    def collect_user(self, user_id):
        print ("Collecting user {}".format(user_id))
        # Search user in the database
        vk_user = db.session.query(db.User).get(user_id)
        if (not vk_user):
            # Create new user
            user_data = self._get_user(user_id)
            vk_user = db.User(user_id, user_data)
            vk_user.updated = datetime.utcnow()
            db.session.add(vk_user)
            db.session.commit()
        print (vk_user)
        return []
