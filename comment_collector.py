#!/usr/bin/env false

import vk_api
import time
import hashlib

class CommentCollector:

    def __init__(self, login, password, proxy_dict = None):
        login_hash = hashlib.sha256(login.encode("utf-8")).hexdigest()
        vk_session = vk_api.VkApi(login, password, config_filename = "vk_config." + login_hash + ".json")
        vk_session.http.proxies = proxy_dict

        try:
            vk_session.auth()
            print("auth_success")
        except vk_api.AuthError as error_msg:
            print(error_msg)
            return

        self.tools = vk_api.VkTools(vk_session)
        self.vk = vk_session.get_api()
        self.max_depth = 0

    def get_user(self, id):
        response = self.vk.users.get(user_ids=id, name_case="Nom")
        return response[0]

    @staticmethod
    def _ptime_to_time(ptime):
        return time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(ptime))

    def get_comments_recursive(self, user_id, max_depth):
        self.max_depth = max_depth
        visited_ids = set()
        return self.get_comments(user_id, visited_ids)

    def get_comments(self, user_url_id, visited_ids, depth=0):
        try:
            user_data = self.get_user(user_url_id)
            user_id = user_data['id']
        except vk_api.ApiError as e:
            print(e)
            print('error get user data')
            return {}
        if user_id in visited_ids:
            print('VISITED')
            return {}
        else:
            print(user_data)
            print(depth)
            comments = []
            try:
                comments.extend(self._get_comments_from_photos(user_id, depth))
            except Exception as e:
                print('error get comments from photos')
                print(f'Exception {e}')
            try:
                comments.extend(self._get_comments_from_wall(user_id, depth))
            except Exception as e:
                print('error get comments from wall')
                print(f'Exception {e}')

            collected_data = {'user_id': user_id, 'first_name': user_data['first_name'], 'last_name': user_data['last_name'],
                 'comments': comments}

            visited_ids.add(user_id)

            if depth < self.max_depth:
                collected_data['nested'] = {}
                for comment in comments:
                    collected_data['nested'][comment['author_id']] = self.get_comments(comment['author_id'],
                                                                                       visited_ids,
                                                                                       depth=depth + 1)

            return collected_data

    def _get_comments_from_photos(self, user_id, depth=0):
        print('get_photos')
        processed_comments = []
        for comment in self.vk.photos.getAllComments(owner_id=user_id)['items']:
            processed_comments.append(self._process_comment(comment, depth, photo_id=comment['pid']))

        return processed_comments

    def _get_comments_from_wall(self, user_id, depth=0):
        print('get_wall')
        processed_comments = []
        posts = self.tools.get_all('wall.get', 100, {'owner_id': user_id})
        for item in posts["items"]:
            print('get post')
            for comment in self.tools.get_all('wall.getComments', 100,
                                              {'owner_id': user_id, 'post_id': item['id']})['items']:
                processed_comments.append(self._process_comment(comment, depth, post_id=item['id']))
        return processed_comments

    def _process_comment(self, comment, depth=0, post_id=None, photo_id=None):
        processed_comment = {'id': comment['id'],
                              'text': comment['text'],
                              'date': CommentCollector._ptime_to_time(comment['date']),
                              'author_id': comment['from_id'],
                              'depth': depth,
                              'reply_to_comment': comment.get('reply_to_comment', None)}

        if post_id:
            processed_comment['post_id'] = post_id
        if photo_id:
            processed_comment['photo_id'] = photo_id
        return processed_comment

