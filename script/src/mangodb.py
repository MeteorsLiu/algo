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

    # 根据用户输入模糊查询用户 
    def user_search(self, user: str, limit: int = 10):
        return self.user_info.find(
            {
                "username": {
                    "$regex": user,
                    "$options": "i"
                }
            }
        ).limit(limit).to_list()
    
    # 根据用户输入精确查询语言
    def language_search(self, language: str, limit: int = 10):
        return (
            self.user_info.find(
                {
                    f"rank_{language}": {"$exists": True}  # 检查 lang 对象中是否包含指定语言
                }
            )
            .sort(f"rank_{language}", 1)  # 按指定语言的熟练度从高到低排序
            .limit(limit)
            .to_list()
        )
    
    def user_rank(self, username: str):
        d = self.user_info.find_one(
            {'username': username},
        )
        lang_rank = {}
        for k in d.get('lang', {}).keys():
            lang_rank[k] = d.get(f'rank_{k}', -1)
        # lang_rank = sorted(lang_rank.items(), key=lambda x: x[1], reverse=True)
        return lang_rank

    def user_nearby(self, language: str, language_index: int = None, limit: int = 10, user: str = None):
        if user:
            user_info = self.user_info.find_one({
                'username': user,
                f"rank_{language}": {"$exists": True}  # 检查 lang 对象中是否包含指定语言
            })
            language_index = user_info.get(f'rank_{language}', None)

        if not language_index:
            return []
        
        # 计算前后索引范围
        before_idx = max(language_index - limit - 1, 0)
        
        after_idx = language_index + limit

        # 使用 $and 方法来构建查询条件
        pipeline = [
            {"$match": {f"rank_{language}": {"$exists": True}}},  # 筛选包含指定语言的记录
            {"$sort": {f"rank_{language}": 1}},  # 按语言熟练度降序排序
            {"$skip": before_idx},  # 跳过前 before_idx 条记录
            {"$limit": after_idx - before_idx},  # 限制返回的记录数量
            {"$project": {"rank_repos": 0}}  # 将 field_to_exclude 替换为要排除的字段
        ]

        result = list(self.user_info.aggregate(pipeline))
        return result

    def user_repo_ranks(self, username: str):
        d = self.user_info.find_one(
            {'username': username},
            {'username':1, 'rank_repos': 1}
        )
        return d


    def count_unique_languages(self):
        pipeline = [
            {"$project": {"langs": {"$objectToArray": "$lang"}}},  # 将 `lang` 对象转换为数组
            {"$unwind": "$langs"},  # 展开数组
            {"$group": {"_id": "$langs.k"}},  # 将语言名称分组
            {"$sort": {"count": 1}}  # 按语言名称排序（可选）
            # {"$count": "unique_languages"}  # 统计唯一语言数
        ]
        
        result = list(self.user_info.aggregate(pipeline))
        # return result[0]["unique_languages"] if result else 0
        return result if result else 0

if __name__ == '__main__':
    mango = Mangodb()
    print(mango.user_nearby(
        language='Rust',
        language_index=1,
    ))