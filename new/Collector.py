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
    def _get_user_data(self, user_id):
        return self.vk.users.get(user_ids=user_id, name_case="Nom", fields=self.user_fields)[0]

    # Return user posts
    def _get_user_wall_posts(self, user_id):
        return self.tools.get_all('wall.get', config.collector.max_post_count, {'owner_id': user_id})['items']

    # Return comments for post
    def _get_comments_for_post(self, user_id, post_id):
        try:
            return self.tools.get_all('wall.getComments', config.collector.max_comment_count, {'owner_id': user_id, 'post_id': post_id, 'need_likes': True})['items']
        except vk_api.exceptions.VkToolsException as e:
            print ("Exception: {}".format(e))
            return []

    # Return comments for photo
    def _get_comments_for_photo(self, user_id, photo_id):
        try:
            return self.tools.get_all('photos.getComments', config.collector.max_comment_count, {'owner_id': user_id, 'photo_id': photo_id, 'need_likes': True})['items']
        except vk_api.exceptions.VkToolsException as e:
            print ("Exception: {}".format(e))
            return []

    # Create new user or retrieve the existing one
    def _get_user(self, user_id):
        # Search user in the database
        db_user = db.session.query(db.User).get(user_id)
        
        created = False

        if (not db_user):
            # Create new user
            vk_user = self._get_user_data(user_id)
            #print (vk_user)
            db_user = self._create_user(user_id, vk_user)

            created = True

        #print (db_user)

        return (db_user, created)

    # Create new user in the database with all stuff
    def _create_user(self, user_id, vk_user):
        # Check city and add it if neccessary
        vk_city = vk_user.get('city')
        if (vk_city):
            db_city = db.session.query(db.City).get(vk_city['id'])
            if (not db_city):
                db_city = db.City(vk_city['id'], vk_city['title'])
                db.session.add(db_city)

        # Check country and add it if neccessary
        vk_country = vk_user.get('country')
        if (vk_country):
            db_country = db.session.query(db.Country).get(vk_country['id'])
            if (not db_country):
                db_country = db.Country(vk_country['id'], vk_country['title'])
                db.session.add(db_country)

        # Check education and add it if neccessary
        vk_education = vk_user.get('education')
        if (vk_education):
            db_education = db.session.query(db.Education).filter_by(
                        university = vk_education['university'], 
                        faculty = vk_education['faculty'], 
                        graduation = vk_education['graduation']
                    ).first()
            if (not db_education):
                # Check University and Faculty, create them if neccessary
                db_university = db.session.query(db.University).get(vk_educaiton['university'])
                if (not db_university):
                    db_university = db.University(vk_education['university'], vk_education['university_name'])
                    db.session.add(db_university)
                db_faculty = db.session.query(db.Faculty).get(vk_educaiton['faculty'])
                if (not db_faculty):
                    db_faculty = db.University(vk_education['faculty'], vk_education['faculty_name'])
                    db.session.add(db_faculty)

                db_education = db.Education(None, vk_education)
                db.session.add(db_education)

        # TODO: connections, counters!

        db_user = db.User(user_id, vk_user)
        if (vk_education):
            db_user.education_id = db_education.id
        db_user.updated = datetime.utcnow()
        db.session.add(db_user)

        db.session.commit()
        return db_user

    def _get_posts(self, user_id):
        try:
            return self.tools.get_all('wall.get', config.collector.max_post_count, {'owner_id': user_id})['items']
        except vk_api.exceptions.VkToolsException as e:
            print ("Exception: {}".format(e))
            return []

    def _get_photos(self, user_id):
        try:
            return self.tools.get_all('photos.getAll', config.collector.max_photo_count, {'owner_id': user_id})['items']
        except vk_api.exceptions.VkToolsException as e:
            print ("Exception: {}".format(e))
            return []

    # Returns IDs of all users that commented on post
    def collect_comments_for_post_or_photo(self, user_id, post_id=None, photo_id=None):
        if (not post_id and not photo_id) or (post_id and photo_id):
            raise Exception("You should specify one (and only one) of post_id and photo_id!")

        users_replied = []

        if (post_id):
            vk_comments = self._get_comments_for_post(user_id, post_id)
        else:
            vk_comments = self._get_comments_for_photo(user_id, photo_id)

        for vk_comment in vk_comments:
            #print (vk_comment)
            db_comment = db.session.query(db.Comment).get(vk_comment['id'])
            if (not db_comment):
                # Create comment itself
                db_comment = db.Comment(vk_comment['id'], vk_comment)

                # Create record for author if it doesn't exists
                db_user, created = self._get_user(db_comment.from_id, only_create = True)

                db.session.add(db_comment)
                if (created):
                    # HACK: mark this new user as retrieved long ago, so we won't miss him then the time comes
                    db_user.updated = datetime.fromtimestamp(0)
                    db.session.add(db_user)

                # Append author to the list of users commented here
                users_replied.append(db_comment.from_id)

        db.session.commit()

        return users_replied

    # Returns IDs of the users that commented on the posts of current user
    def collect_posts_with_comments(self, user_id):
        users_replied = []

        vk_posts = self._get_posts(user_id)

        for vk_post in vk_posts:
            #print (vk_post)
            #db_post = db.session.query(db.Post).get( (vk_post['id'], vk_post['owner_id']) )
            db_post = db.session.query(db.Post).get( vk_post['id'] )
            if (not db_post):
                # Post doesn't exists, create it
                db_post = db.Post(vk_post['id'], vk_post)
                db.session.add(db_post)

            users_replied.extend(self.collect_comments_for_post_or_photo(user_id, post_id = vk_post['id']))

        db.session.commit()

        return users_replied

    # Returns IDs of the users that commented on the photos of current user
    def collect_photos_with_comments(self, user_id):
        users_replied = []

        vk_photos = self._get_photos(user_id)

        for vk_photo in vk_photos:
            #print (vk_photo)
            #db_photo = db.session.query(db.Photo).get( (vk_photo['id'], vk_photo['owner_id']) )
            db_photo = db.session.query(db.Photo).get( vk_photo['id'] )
            if (not db_photo):
                # Photo doesn't exists, create it
                db_photo = db.Photo(vk_photo['id'], vk_photo)
                db.session.add(db_photo)

            users_replied.extend(self.collect_comments_for_post_or_photo(user_id, photo_id = vk_photo['id']))

        db.session.commit()

        return users_replied

    def collect_user(self, user_id):
        print ("Collecting user {}".format(user_id))

        db_user, created = self._get_user(user_id)

        # Check that user update time was long ago or user was just created
        if (created || (db_user.updated + config.collector.user_time_delta > datetime.utcnow())):
            print ("Skipping user, its data is new")
            return []

        users_from_posts = self.collect_posts_with_comments(user_id)
        users_from_photos = self.collect_photos_with_comments(user_id)

        db_user.updated = datetime.utcnow()
        db.session.add(db_user)
        db.session.commit()

        return users_from_posts + users_from_photos
