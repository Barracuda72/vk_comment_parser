#!/usr/bin/env false

import vk_api
import time
import hashlib
import config
import database as db
from datetime import datetime
from sqlalchemy.exc import IntegrityError

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

    # Return specific user posts
    def _get_specific_user_wall_posts(self, user_id, posts):
        posts = [str(user_id) + "_" + str(post_id) for post_id in posts]
        posts = ",".join(posts)
        #print ("Requesting posts {}".format(posts))
        ret = self.vk.wall.getById(posts = posts) #['items']
        #import json
        #print ("Got {}".format(json.dumps(ret)))
        return ret

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
        db_user = None
        while not db_user:
            db_user = db.session.query(db.User).get(user_id)
    
            if (not db_user):
                # Create new user
                vk_user = self._get_user_data(user_id)
                with db.session.begin_nested():
                    try:
                        db_user = self._create_user(user_id, vk_user)
                    except IntegrityError as e:
                        print ("Integrity error, probably user already exists: {}".format(e))
                

        #print (db_user)

        return db_user

    def _print_integrity_error(self, db_Class, e):
        print ("Integrity error, probably someone already created this object ({}): {}".format(db_Class.__name__, e))

    # Get or create simple binary relation (city, university, faculty, country, etc)
    def _get_binary_relation(self, db_Class, id, name):
        db_object = None
        while not db_object:
            db_object = db.session.query(db_Class).get(id)
            if (not db_object):
                try:
                    with db.session.begin_nested():
                        db_object = db_Class(id, name)
                        db.session.add(db_object)
                except IntegrityError as e: 
                    self._print_integrity_error(db_Class, e)
        return db_object

    # Create new user in the database with all stuff
    def _create_user(self, user_id, vk_user):
        # Check city and add it if neccessary
        vk_city = vk_user.get('city')
        if (vk_city):
            db_city = self._get_binary_relation(db.City, vk_city['id'], vk_city['title'])

        # Check country and add it if neccessary
        vk_country = vk_user.get('country')
        if (vk_country):
            db_country = self._get_binary_relation(db.Country, vk_country['id'], vk_country['title'])

        # Check education and add it if neccessary
        vk_education = vk_user.get('education')
        if (vk_education):
            db_education = None
            while not db_education:
                db_education = db.session.query(db.Education).filter_by(
                            university = vk_education['university'], 
                            faculty = vk_education['faculty'], 
                            graduation = vk_education['graduation']
                        ).first()
                if (not db_education):
                    # Check University and Faculty, create them if neccessary
                    db_university = self._get_binary_relation(db.University, vk_education['university'], vk_education['university_name'])
                    db_faculty = self._get_binary_relation(db.Faculty, vk_education['faculty'], vk_education['faculty_name'])
                    db_education = db.Education(None, vk_education)
    
                    try:
                        with db.session.begin_nested():
                            db.session.add(db_education)
                    except IntegrityError as e:
                        self._print_integrity_error(db.Education, e)
                        db_education = None

        vk_connections = vk_user.get('connections')
        if (vk_connections):
            db_connections = None
            while not db_connections:
                db_connections = db.session.query(db.Connections).get( user_id )
                if (not db_connections):
                    db_connections = db.Connections( user_id, vk_connections )

                    try:
                        with db.session.begin_nested():
                            db.session.add(db_connections)
                    except IntegrityError as e:
                        self._print_integrity_error(db.Connections, e)
                        db_connections = None

        vk_counters = vk_user.get('counters')
        if (vk_counters):
            db_counters = None
            while not db_counters:
                db_counters = db.session.query(db.Counters).get( user_id )
                if (not db_counters):
                    db_counters = db.Counters( user_id, vk_counters )

                    try:
                        with db.session.begin_nested():
                            db.session.add(db_counters)
                    except IntegrityError as e:
                        self._print_integrity_error(db.Counters, e)
                        db_counters = None

        db_user = None
        try:
            with db.session.begin_nested():
                db_user = db.User(user_id, vk_user)
                if (vk_education):
                    db_user.education_id = db_education.id
            
                # HACK: mark this new user as retrieved long ago, so we won't miss him then the time comes
                db_user.updated = datetime.fromtimestamp(0)
                db.session.add(db_user)
        except IntegrityError as e:
            self._print_integrity_error(db.User, e)

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

    def collect_comments_for_post_or_photo(self, user_id, object_id, real_id, key, getter, db_Class, **kwds):
        # Map for transforming reply_to_comment into real comment IDs
        replies_id_map = {}
        # List of comments that have "reply_to_comment" field
        replies = []
        # List of replied users
        users_replied = []
        # New comments
        new_comments = []

        vk_comments = getter(user_id, object_id)

        for vk_comment in vk_comments:
            kwds['id'] = vk_comment['id']
            db_comment = db.session.query(db_Class).filter_by(**kwds).first()

            if (not db_comment):
                # TODO: HACK
                vk_comment[key] = real_id

                # Create comment
                db_comment = db_Class(vk_comment)

                # Create empty record for author if it doesn't exist
                db_user = self._get_user(db_comment.from_id)

                # Append author to the list of users commented here
                users_replied.append(db_comment.from_id)
                
                if (db_comment.reply_to_comment_id):
                    replies.append(db_comment)
                else:
                    db.session.add(db_comment)
                    db.session.commit()
                    replies_id_map[db_comment.id] = db_comment.unique_id
            else:
                replies_id_map[db_comment.id] = db_comment.unique_id

        # Fix all "reply to" fields
        while len(replies) > 0:
            unprocessed_replies = []
            for db_comment in replies:
                unique_id = replies_id_map.get(db_comment.reply_to_comment_id)
                if (unique_id):
                    db_comment.reply_to_comment_id = unique_id
                    db.session.add(db_comment)
                    db.session.commit()
                    replies_id_map[db_comment.id] = db_comment.unique_id
                else:
                    unprocessed_replies.append(db_comment)

            replies = unprocessed_replies

        db.session.commit()

        return users_replied

    def collect_comments_for_post(self, user_id, post_id, real_id):
        return self.collect_comments_for_post_or_photo(
                user_id, post_id, real_id, 'post_id', 
                self._get_comments_for_post, db.WallComment, 
                post_id = real_id
            )

    def collect_comments_for_photo(self, user_id, photo_id, real_id):
        return self.collect_comments_for_post_or_photo(
                user_id, photo_id, real_id, 'pid', 
                self._get_comments_for_photo, db.PhotoComment, 
                photo_id = real_id
            )

    def get_referenced_post(self, owner_id, post_id):
        db_user = self._get_user(owner_id)

        db_post = None
        while not db_post:
            db_post = db.session.query(db.Post).filter_by(
                id = post_id,
                owner_id = owner_id
            ).first()
    
            if (not db_post):
                post_list = self._get_specific_user_wall_posts(owner_id, [post_id])

                try:
                    vk_post = post_list[0]
                    print ('Successfully retrieved parent post {}_{}'.format(owner_id, post_id))
                except IndexError as e:
                    print ('Failed to retrieve parent post {}_{}'.format(owner_id, post_id))
                    return None

                db_post = db.Post(vk_post)
                db_from = self._get_user(db_post.from_id)
    
                if (vk_post.get('reply_post_id')):
                    parent_post = self.get_referenced_post(vk_post['reply_owner_id'], vk_post['reply_post_id'])

                    if (parent_post):
                        db_post.reply_post_id = parent_post.unique_id
                    else:
                        db_post.reply_post_id = None
                        db_post.reply_owner_id = None
    
                try:
                    with db.session.begin_nested():
                        db.session.add(db_post)
                except IntegrityError as e:
                    self._print_integrity_error(db_Class, e)
                    db_post = None

        return db_post
    
    # Returns IDs of the users that commented on the post or photo of current user
    def collect_records_with_comments(self, user_id, db_Class, getter, comment_collector):
        users_replied = []

        vk_records = getter(user_id)

        for vk_record in vk_records:
            db_record = None
            while not db_record:
                db_record = db.session.query(db_Class).filter_by( 
                    id = vk_record['id'], 
                    owner_id = vk_record['owner_id'] 
                ).first()

                if (not db_record):
                    # Record doesn't exists, create it
                    db_record = db_Class(vk_record)

                    # TODO: HACK: do better!
                    if (db_Class == db.Post):
                        # Photos don't have from_id
                        # Also they don't have recursive dependencies
                        # Create empty record for author if it doesn't exists
                        db_user = self._get_user(db_record.from_id)

                        # Append author to the list of users posted here
                        users_replied.append(db_record.from_id)

                        if (vk_record.get("reply_post_id")):
                            parent_post = self.get_referenced_post(vk_record['reply_owner_id'], vk_record['reply_post_id'])

                            if (parent_post):
                                db_record.reply_post_id = parent_post.unique_id
                                users_replied.append(int(vk_record['reply_owner_id']))
                            else:
                                db_record.reply_post_id = None
                                db_record.reply_owner_id = None

                    try:
                        with db.session.begin_nested():
                            db.session.add(db_record)
                    except IntegrityError as e:
                        self._print_integrity_error(db_Class, e)
                        db_record = None

            users_replied.extend(comment_collector(user_id, vk_record['id'], db_record.unique_id))

        db.session.commit()

        return users_replied

    def collect_user(self, user_id):
        print ("Collecting user {}".format(user_id))

        db_user = self._get_user(user_id)

        # Check that user update time was long ago and user was not just created
        if (db_user.updated + config.collector.user_time_delta > datetime.utcnow()):
            print ("Skipping user, its data is new")
            return []

        users_from_posts = self.collect_records_with_comments(user_id, db.Post, self._get_posts, self.collect_comments_for_post)
        users_from_photos = self.collect_records_with_comments(user_id, db.Photo, self._get_photos, self.collect_comments_for_photo)

        db_user.updated = datetime.utcnow()
        db.session.add(db_user)
        db.session.commit()

        return list(set(users_from_posts + users_from_photos))
