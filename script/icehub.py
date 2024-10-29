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
from typing import Literal

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

    def get_rate_limit(self) -> dict:
        """
        core | integration_manifest | search | ...: 
        
        >limit | remaining | reset | used | resource
        """
        rtn = self.gh_session.get(url='https://api.github.com/rate_limit')
        if rtn.status_code != 200:
            log.error("Error! Status: " + str(rtn.status_code))
            return {}
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

    def api_use(self, api_type: Literal['core', 'search', 'graphql', 'integration_manifest', 
                                        'source_import', 'code_scanning_upload', 'actions_runner_registration', 
                                        'scim', 'dependency_snapshots', 'audit_log', 'audit_log_streaming',
                                        'code_search'], times: int = 0):
        self.rate_limit[api_type]['remaining'] -= times
        if self.rate_limit[api_type]['remaining'] == 0:
            # reset: 1730127528
            reset_time = self.rate_limit[api_type]['reset']
            local_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(float(reset_time)))
            wait_time = reset_time - int(time.time()) + 2
            log.info(f'api {api_type} reset at {local_time}, wait {wait_time} seconds...')
            time.sleep(wait_time)
            self.get_rate_limit()

    def get_user_follow(self, user: str, follow_type: Literal['followers', 'following'], per_page: int = 100, page: int = 1) -> list:
        follow_list = []

        try:
            # When the initial core rate limit time is 0, wait for the API rate limit to reset.
            self.api_use('core')

            while True:
                rtn = self.gh_session.get(url=f'https://api.github.com/users/{user}/{follow_type}?per_page={per_page}&page{page}')
                if rtn.status_code != 200:
                    log.error("Error! Status: " + str(rtn.status_code))
                    return follow_list
                
                data = rtn.json()
                for i in data:
                    if i['type'] == "User":
                        follow_list.append(
                            {
                                'id': i['id'],
                                'login': i['login']
                            }
                        )

                if len(data) < per_page:
                    log.info(f'{user} {follow_type} crawling completed.')
                    break

                log.info(f'page {page} crawled, get next page after 5 seconds.')
                time.sleep(5)
                page += 1
                self.api_use('core', 1)

        except KeyboardInterrupt:
            log.info('User Interrupt.')
            return follow_list
        
        except:
            log.error('Unknown error')
            return follow_list
            
        return follow_list

    def follow_saved(self, user: str, follow_type: Literal['followers', 'following']):
        follow_meta = self.get_user_follow(user=user, follow_type=follow_type)
        for i in tqdm(follow_meta, desc="Updating User Info"):
            self.user_info.update_one(
                {'_id': i['id']},
                {"$setOnInsert": {'username': i['login'], 'ok': False}},
                upsert=True
            )
        log.info(f'{user} {follow_type} saved.')

if __name__ == '__main__':
    # 创建解析器
    parser = argparse.ArgumentParser(description="ICEHUB")
    
    # 添加参数
    parser.add_argument('--user', type=str, help="github username", required=True)
    parser.add_argument('--followers', help="get user followers", action='store_true')
    parser.add_argument('--following', help="get user followings", action='store_true')
    
    # 解析参数
    args = parser.parse_args()

    # 使用参数
    ice = Icehub()

    if args.followers:
        ice.follow_saved(user=args.user, follow_type='followers')
    
    if args.following:
        ice.follow_saved(user=args.user, follow_type='following')

    log.info(ice.get_rate_limit())