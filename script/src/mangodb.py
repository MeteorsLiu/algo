import logging
import os
from dotenv import load_dotenv
from pymongo import MongoClient

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

log = logger = logging

load_dotenv()

GITHUB_ACCESS_TOKEN = os.environ.get('GITHUB_ACCESS_TOKEN')
MONGODB_IP = os.environ.get('MONGODB_IP')
MONGODB_PORT = os.environ.get('MONGODB_PORT')
MONGODB_USENAME = os.environ.get('MONGODB_USENAME')
MONGODB_PASSWORD = os.environ.get('MONGODB_PASSWORD')


class Mangodb():
    def __init__(self, timeout: int = 40000) -> None:
        self.client = MongoClient(f"mongodb://{MONGODB_USENAME}:{MONGODB_PASSWORD}@{MONGODB_IP}:{MONGODB_PORT}/")
        log.info(self.client)
        self.algodb = self.client['algodb']
        # user_info collection structure
        # username update_time issues pullrequests discussions
        self.user_info = self.algodb["user_info"]
        self.user_issue = self.algodb['user_issue']
        self.user_pr = self.algodb['user_pr']
        self.user_discussion = self.algodb['user_discussion']
        self.repo_info = self.algodb['repo_info']

        self.user_cache = self.algodb['user_cache']

    def get_user_repos(this, user, token):
        import requests
        url = f'https://api.github.com/users/{user}/repos'
        repos = []
        page = 1

        headers = {
            'Authorization': f'token {token}'
        }

        while True:
            response = requests.get(url, params={'page': page, 'per_page': 100}, headers=headers)
            if response.status_code != 200:
                print(f"Failed to fetch data: {response.status_code}")
                break

            data = response.json()
            if not data:
                break

            repos.extend(data)
            page += 1

        return repos

    def get_languages(self, user, token):
        repos = self.get_user_repos(user, token)
        print(repos)
        languages = set()

        for repo in repos:
            language = repo.get('language')
            if language:
                languages.add(language)

        return languages

    # 写缓存
    def write_user_cache(self, username: str, lang: set, geo: str, geo_prob: float, rank: float):
        self.user_cache.insert_one({'username': username,
                                    'lang': lang,
                                    'geo': geo,
                                    'geo_prob': geo_prob,
                                    'rank': rank})

    # 读缓存（用户信息）
    def get_user_cache(self, username: str, token: str):
        import geo
        import rank

        tmp = self.user_cache.find_one({'username': username})
        if tmp is None:
            try:
                tmp_user_rank = rank.user_rank(username, token)
                tmp_user_geo = geo.get_nation(username, token)
                tmp_user_lang = self.get_languages(username, token)

                self.write_user_cache(username,
                                      tmp_user_lang,
                                      tmp_user_geo['nation'],
                                      tmp_user_geo['probability'],
                                      tmp_user_rank)
                return self.user_cache.find_one({'username': username})
            except Exception as e:
                log.error(e)
                return None
        else:
            return tmp

    def user_search(self, query: str):
        return self.user_info.find(
            {
                "username": {
                    "$regex": query,
                    "$options": "i"
                }
            }
        ).to_list()