# input
# username

# output
# {
#     issues: [{repository: str, is_involves: bool, msg_count: int, opened_time: str, index: int}, ...],
#     pullrequest: [{repository: str, is_involves: bool, msg_count: int, opened_time: str, index: int}, ...],
#     discussion: [{repository: str, is_involves: bool, msg_count: int, opened_time: str, index: int}, ...],
# }

import requests
import time
import logging
import json
import os
from dotenv import load_dotenv
import argparse
from pymongo import MongoClient
from tqdm import tqdm

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

log = logger = logging

load_dotenv()

GITHUB_USERNAME = os.environ.get('GITHUB_USERNAME')
GITHUB_COOKIE = os.environ.get('GITHUB_COOKIE')
GITHUB_ACCESS_TOKEN = os.environ.get('GITHUB_ACCESS_TOKEN')
MONGODB_IP = os.environ.get('MONGODB_IP')
MONGODB_PORT = os.environ.get('MONGODB_PORT')
MONGODB_USENAME = os.environ.get('MONGODB_USENAME')
MONGODB_PASSWORD = os.environ.get('MONGODB_PASSWORD')

class Icehub():
    url_followers = 'https://api.github.com/users/{}/followers?per_page={}&page{}'
    url_following = 'https://api.github.com/users/{}/following'
    url_id = 'https://api.github.com/users/{}'
    

    headers = {
            # github 遵守 accept 返回类型
            'accept': 'application/json',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'no-cache',
            'cookie': GITHUB_COOKIE,
            'pragma': 'no-cache',
            'priority': 'u=0, i',
            'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
        }

    def __init__(self) -> None:
        # database init
        self.client = MongoClient(f"mongodb://{MONGODB_USENAME}:{MONGODB_PASSWORD}@{MONGODB_IP}:{MONGODB_PORT}/")
        log.info(self.client)
        self.algodb = self.client['algodb']
        # user_info collection structure
        # username update_time issues pullrequests discussions
        self.user_info = self.algodb["user_info"]

        self.gh_session = requests.Session()
        self.gh_session.auth = (GITHUB_USERNAME, GITHUB_ACCESS_TOKEN)

        self.get_rate_limit()

    def get_rate_limit(self):
        """
        core | integration_manifest | search: 
        
        >limit | remaining | reset | used | resource
        """
        rtn = self.gh_session.get(url='https://api.github.com/rate_limit')
        if rtn.status_code != 200:
            log.error("Error! Status: " + str(rtn.status_code))
            return
        data = rtn.json()
        self.rate_limit = data['resources']
        return self.rate_limit
    
    @DeprecationWarning    
    def contribution_saved(self, username: str = 'jellyqwq', output_dir: str = './'):
        s = requests.Session()

        for i in ['issues', 'pullrequests', 'discussions']:
            params = {
                'type': i,
                # 'query': f'involves:{username}',
                'q': f'involves:{username}',
            }
            log.info(f'start involves:{username}+type:{i} query.')

            response = s.get('https://github.com/search', params=params, headers=self.headers)
            
            # with open(os.path.join(output_dir, f'{username}-{i}.json'), 'w', encoding='UTF-8') as f:
            #     f.write(json.dumps(
            #         response.json(),
            #         ensure_ascii=False,
            #         indent=4
            #     ))
            
            log.info(f'{username}-{i}.json saved. waiting 3 seconds.')
            time.sleep(3)
        
        s.close()

    def api_use(self, api_type: str, times: int = 0):
        """
        api_type: core | integration_manifest | search
        """
        self.rate_limit[api_type]['remaining'] -= times
        if self.rate_limit[api_type]['remaining'] == 0:
            # reset: 1730127528
            reset_time = self.rate_limit[api_type]['reset']
            local_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(float(reset_time)))
            wait_time = reset_time - int(time.time()) + 2
            log.info(f'api {api_type} reset at {local_time}, wait {wait_time} seconds...')
            time.sleep(wait_time)
            self.get_rate_limit()

    def get_user_followers(self, user: str, per_page: int = 100, page: int = 1) -> list:
        follower_list = []

        try:
            # When the initial core rate limit time is 0, wait for the API rate limit to reset.
            self.api_use('core')

            while True:
                rtn = self.gh_session.get(url=f'https://api.github.com/users/{user}/followers?per_page={per_page}&page{page}')
                if rtn.status_code != 200:
                    log.error("Error! Status: " + str(rtn.status_code))
                    return follower_list
                data = rtn.json()
                for i in data:
                    if i['type'] == "User":
                        follower_list.append(
                            {
                                'id': i['id'],
                                'login': i['login']
                            }
                        )
                if len(data) < per_page:
                    log.info(f'{user} followers crawling completed.')
                    break
                log.info(f'page {page} crawled, get next page after 5 seconds.')
                time.sleep(5)
                page += 1
                self.api_use('core', 1)

        except KeyboardInterrupt:
            log.info('User Interrupt.')
            return follower_list
            
        return follower_list

    def get_user_following(self, user: str, per_page: int = 100, page: int = 1) -> list:
        self.get_rate_limit()
        if self.rate_limit['core']['remaining'] == 0:
            # reset: 1730127528
            reset_time = self.rate_limit['core']['reset']
            local_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(float(reset_time)))
            wait_time = reset_time - int(time.time()) + 2
            log.info(f'api reset at {local_time}, wait {wait_time} seconds...')
            time.sleep(wait_time)

        following_list = []
        while True and self.rate_limit['core']['remaining']:
            rtn = self.gh_session.get(url=f'https://api.github.com/users/{user}/following?per_page={per_page}&page{page}')
            if rtn.status_code != 200:
                log.error("Error! Status: " + str(rtn.status_code))
                return []
            data = rtn.json()
            for i in data:
                if i['type'] == "User":
                    following_list.append(
                        {
                            'id': i['id'],
                            'login': i['login']
                        }
                    )
            if len(data) < per_page:
                break
            page += 1
        return following_list

    def followers_saved(self, user: str):
        followers = self.get_user_followers(user)
        for i in tqdm(followers, desc="Updating User Info"):
            self.user_info.update_one(
                {'_id': i['id']},
                {"$setOnInsert": {'username': i['login'], 'ok': False}},
                upsert=True
            )
        log.info(f'{user} followers saved.')

    @DeprecationWarning
    def followings_saved(self, user: str):
        followings = self.get_user_followings(user)
        result = self.user_info.insert_many(
            [{'_id': i['id'], 'username': i['login']} for i in followings]
        )
        log.info(f'{user} following saved')
        log.info(result)

if __name__ == '__main__':
    # # 创建解析器
    # parser = argparse.ArgumentParser(description="ICEHUB")
    
    # # 添加参数
    # parser.add_argument('--username', type=str, help="输入Github用户名", default='jellyqwq', required=True)
    # parser.add_argument('--output_dir', type=str, help="输入输出目录(需要带斜杠/)", default='data', required=False)
    
    # # 解析参数
    # args = parser.parse_args()

    # # 使用参数
    # os.makedirs(args.output_dir, exist_ok=True)

    # task(username=args.username, output_dir=args.output_dir)
    ice = Icehub()
    # log.info(ice.get_user_followers('MeteorsLiu'))
    ice.followers_saved('MeteorsLiu')
    log.info(ice.get_rate_limit()['core'])