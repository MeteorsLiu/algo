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
import os
from dotenv import load_dotenv
import argparse
from pymongo import MongoClient
from tqdm import tqdm
from typing import Literal

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s',
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

def string_to_timestamp(iso_time: str = "2024-04-14T07:20:15Z") -> int:
    # 去掉字符串末尾的 "Z"，并替换 "T" 为空格，使其符合 strptime 的格式
    formatted_time = iso_time.replace("T", " ").replace("Z", "")

    # 解析为 UTC 时间结构
    time_struct = time.strptime(formatted_time, "%Y-%m-%d %H:%M:%S")

    # 转换为本地时间戳
    timestamp = time.mktime(time_struct)

    return timestamp


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
        self.user_issue = self.algodb['user_issue']
        self.user_pr = self.algodb['user_pr']
        self.user_discussion = self.algodb['user_discussion']
        self.repo_info = self.algodb['repo_info']

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
        log.debug(self.rate_limit)
        if self.rate_limit[api_type]['remaining'] == 0:
            # reset: 1730127528
            reset_time = self.rate_limit[api_type]['reset']
            local_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(float(reset_time)))
            wait_time = reset_time - int(time.time()) + 5
            if wait_time > 0:
                log.info(f'api {api_type} reset at {local_time}, wait {wait_time} seconds...')
                time.sleep(wait_time)
            self.get_rate_limit()

    def get_user_follow(self, user: str, follow_type: Literal['followers', 'following'], 
                        per_page: int = 100, page: int = 1) -> list:
        follow_list = []

        try:
            # When the initial core rate limit time is 0, wait for the API rate limit to reset.
            self.api_use('core')

            while True:
                rtn = self.gh_session.get(
                    url=f'https://api.github.com/users/{user}/{follow_type}',
                    params={
                        'per_page': per_page,
                        'page': page
                    }
                )
                self.api_use('core', 1)
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

                log.info(f'page {page} crawled, get next page.')
                page += 1
                

        except KeyboardInterrupt:
            log.info('User Interrupt.')
            return follow_list
        
        except:
            log.error('Unknown error')
            return follow_list
            
        return follow_list

    def save_user_follow(self, user: str, follow_type: Literal['followers', 'following'], 
                        per_page: int = 100, page: int = 1):

        try:
            # When the initial core rate limit time is 0, wait for the API rate limit to reset.
            self.api_use('core')

            while True:
                rtn = self.gh_session.get(
                    url=f'https://api.github.com/users/{user}/{follow_type}',
                    params={
                        'per_page': per_page,
                        'page': page
                    }
                )
                self.api_use('core', 1)
                if rtn.status_code != 200:
                    log.error("Error! Status: " + str(rtn.status_code))
                    log.error(rtn.text)
                    return True
                
                data = rtn.json()
                for i in tqdm(data, desc=f'Updating {user} {follow_type} page {page}'):
                    if i['type'] == "User":
                        self.user_info.update_one(
                            {'_id': i['id']},
                            {"$setOnInsert": {'username': i['login']}},
                            upsert=True
                        )

                if len(data) < per_page:
                    log.info(f'{user} {follow_type} crawling completed.')
                    break

                log.info(f'page {page} crawled, get next page.')
                page += 1
                # time.sleep(0.8)
                
        except KeyboardInterrupt:
            log.info('User Interrupt.')
            return False
        
        except:
            log.error('Unknown error')
            return True
            
        return True
    
    def follow_saved(self, user: str, follow_type: Literal['followers', 'following']):
        follow_meta = self.get_user_follow(user=user, follow_type=follow_type)
        for i in tqdm(follow_meta, desc="Updating User Info"):
            self.user_info.update_one(
                {'_id': i['id']},
                {"$setOnInsert": {'username': i['login'], 'ok': False}},
                upsert=True
            )
        log.info(f'{user} {follow_type} saved.')

    def save_user_issues_or_pullrequest(self, user: str, qualifier: Literal['is:issue', 'is:pull-request'], 
                                         per_page: int = 100, page: int = 1):
        item_list = []
        if qualifier == 'is:issue':
            collection = self.user_issue
        elif qualifier== 'is:pull-request':
            collection = self.user_pr
        else:
            log.error('qualifier can not empty.')
            return item_list
        
        try:
            # When the initial core rate limit time is 0, wait for the API rate limit to reset.
            self.api_use('search')

            while True:
                rtn = self.gh_session.get(url=f'https://api.github.com/search/issues?q=involves:{user}+{qualifier}&per_page={per_page}&page={page}')
                self.api_use('search', 1)
                if rtn.status_code != 200:
                    log.error("Error! Status: " + str(rtn.status_code))
                    log.error(rtn.text)
                    return True
                
                data = rtn.json()
                # log.info(data)
                total_count = data['total_count']
                items = data.get('items', [])
 
                for item in tqdm(items, desc=f"Updating {user} {qualifier}"):
                    reactions = item['reactions']
                    reactions.pop('url')
                    repo_owner, repo_name = item["repository_url"][29:].split('/')

                    collection.update_one(
                        {
                            'issue_id': item['id'], # issue id
                            'user': user
                        }, 
                        {
                            '$set': {
                                'issue_id': item['id'],
                                'user': user,
                                # https://api.github.com/repos/{owner}/{repo_name}
                                "repo_owner": repo_owner,
                                "repo_name": repo_name,
                                'full_name': f'{repo_owner}/{repo_name}',
                                "created_at": string_to_timestamp(item['created_at']) if item['created_at'] else 0,
                                "updated_at": string_to_timestamp(item['updated_at']) if item['updated_at'] else 0,
                                "closed_at": string_to_timestamp(item['closed_at']) if item['closed_at'] else 0,
                                # closed_at = 0 -> state = open
                                "reactions": reactions
                            }
                        }, upsert=True)

                if len(items) < per_page:
                    self.user_info.update_one(
                        {
                            'username': user,
                        },
                        {
                            '$set': {
                                '{}_count'.format('issue' if 'issue' in qualifier else 'pr'): total_count
                            }
                        },
                        upsert=True
                    )
                    log.debug(f'{user} {qualifier} saved.')
                    break

                log.debug(f'{user} {qualifier} page {page} crawled, get next page.')
                page += 1
                

        except KeyboardInterrupt:
            log.info('User Interrupt.')
            return False
        
        except:
            log.exception('Unknown error', stack_info=True)
            return True
            
        return True

    def get_empty_col_user(self, col_name: str, limit: int = 0) -> list:
        data = self.user_info.find({col_name: None}, limit=limit).to_list()
        log.debug(data)
        return data

    def save_repository_info(self, repo_owner: str, repo_name: str, full_name: str):
        try:
            self.api_use('core')

            rtn = self.gh_session.get(url=f'https://api.github.com/repos/{repo_owner}/{repo_name}')
            # must minus 1 after get method.
            self.api_use('core', 1)
            if rtn.status_code != 200:
                log.error("Error! Status: " + str(rtn.status_code))
                log.error(rtn.text)
                return True
            data = rtn.json()
            
            self.repo_info.update_one(
                {'_id': data['id']},
                {
                    '$set': {
                        '_id': data['id'],
                        'repo_owner': repo_owner,
                        'repo_name': repo_name,
                        'full_name': full_name if full_name else f'{repo_owner}/{repo_name}',
                        'language': data['language'],
                        'archived': data['archived'],
                        'forks_count': data['forks_count'],
                        'watchers_count': data['watchers_count'],
                        'stargazers_count': data['stargazers_count'],
                        'open_issues_count': data['open_issues_count'],
                        'subscribers_count': data['subscribers_count'],
                        "created_at": string_to_timestamp(data['created_at']),
                        "updated_at": string_to_timestamp(data['updated_at']),
                        "pushed_at": string_to_timestamp(data['pushed_at'])
                    }
                },
                upsert=True
            )
            log.debug(f'{repo_owner}/{repo_name} is saved')
            # time.sleep(0.8)

        except KeyboardInterrupt:
            log.info('User Interrupt.')
            return False
        except:
            log.exception('Unknown error', stack_info=True)
            return True

        return True

    def save_repository(self, qualifier: Literal['user_issue', 'user_pr']):
        if qualifier == 'user_issue':
            collection = self.user_issue
        elif qualifier == 'user_pr':
            collection = self.user_pr
        else:
            log.error("get_unsaved_repo qualifiter cannot empty")
            return True
        
        distinct_fullnames_cursor = collection.aggregate([
            {
                '$group': {
                    '_id': '$full_name',  # 按 full_name 分组
                    # 'count': { '$sum': 1 }  # 计算每个 full_name 的出现次数
                }
            }
        ])

        # 使用 distinct 方法获取所有不同的 fullname
        distinct_fullnames = collection.distinct('full_name')

        # 计算不同 fullname 的数量
        distinct_count = len(distinct_fullnames)
        log.info(f'distinct_fullnames count {qualifier}: {distinct_count}')

        # 使用for循环逐条处理结果，减少内存占用
        for repo in tqdm(distinct_fullnames_cursor, desc=f'Save {qualifier} Repository', total=distinct_count):
            full_name = repo['_id']

            # 在 repo_info 表中查找是否存在该 repo_owner 和 repo_name 组合
            exists_in_repo_info = self.repo_info.find_one({
                'full_name': full_name,
            }, {'full_name': 1})
            
            repo_owner, repo_name = full_name.split('/')
            # 如果不存在，则打印或记录该组合
            if not exists_in_repo_info:
                log.debug(f"Not in repo_info - Repo Owner: {repo_owner}, Repo Name: {repo_name}")
                self.save_repository_info(
                    repo_owner=repo_owner,
                    repo_name=repo_name,
                    full_name=full_name
                )

    def get_user_list(self, limit=0) -> list:
        data = list(self.user_info.find(
            {},
            ['username']
        ).limit(limit))
        log.debug(data)
        return data
    
if __name__ == '__main__':
    # 创建解析器
    parser = argparse.ArgumentParser(description="ICEHUB")
    
    # 添加参数
    parser.add_argument('--user', type=str, help="github username", required=False)
    parser.add_argument('--followers', help="get user followers", action='store_true')
    parser.add_argument('--following', help="get user followings", action='store_true')
    parser.add_argument('--user_issue', help="get user issue", action='store_true')
    parser.add_argument('--user_pr', help="get user pull request", action='store_true')
    parser.add_argument('--user_null', type=str, help="get user null column", required=False)
    parser.add_argument('--username_list', help="get username_list", action='store_true')
    parser.add_argument('--repo_owner', type=str, help="get repository owner", required=False)
    parser.add_argument('--repo_name', type=str, help="get repository name", required=False)
    parser.add_argument('--repo_unsaved', help="get unsaved repository", action='store_true')
    
    # 解析参数
    args = parser.parse_args()

    # 使用参数
    ice = Icehub()

    if args.followers:
        ice.follow_saved(user=args.user, follow_type='followers')
    
    if args.following:
        ice.follow_saved(user=args.user, follow_type='following')

    if args.user_issue:
        ice.save_user_issues_or_pullrequest(args.user, 'is:issue')

    if args.user_pr:
        ice.save_user_issues_or_pullrequest(args.user, 'is:pull-request')

    if args.user_null:
        ice.get_user_info_empty(args.user_null)

    if args.repo_owner and args.repo_name:
        ice.save_repository_info(args.repo_owner, args.repo_name)

    if args.repo_unsaved:
        ice.save_repository('user_issue')
        ice.save_repository('user_pr')
    
    if args.username_list:
        log.info(ice.get_user_list(limit=10))

    # log.info(ice.get_rate_limit())