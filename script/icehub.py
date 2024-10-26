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

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

log = logger = logging

load_dotenv()

GITHUB_COOKIE = os.environ.get('GITHUB_COOKIE')

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

def task(username: str = 'jellyqwq', output_dir: str = './'):
    s = requests.Session()

    for i in ['issues', 'pullrequests', 'discussions']:
        params = {
            'type': i,
            # 'query': f'involves:{username}',
            'q': f'involves:{username}',
        }
        log.info(f'start involves:{username}+type:{i} query.')

        response = s.get('https://github.com/search', params=params, headers=headers)
        with open(os.path.join(output_dir, f'{username}-{i}.json'), 'w', encoding='UTF-8') as f:
            f.write(json.dumps(
                response.json(),
                ensure_ascii=False,
                indent=4
            ))
        
        log.info(f'{username}-{i}.json saved. waiting 3 seconds.')
        time.sleep(3)
    
    s.close()

if __name__ == '__main__':
    # 创建解析器
    parser = argparse.ArgumentParser(description="ICEHUB")
    
    # 添加参数
    parser.add_argument('--username', type=str, help="输入Github用户名", default='jellyqwq', required=True)
    parser.add_argument('--output_dir', type=str, help="输入输出目录(需要带斜杠/)", default='data', required=False)
    
    # 解析参数
    args = parser.parse_args()

    # 使用参数
    os.makedirs(args.output_dir, exist_ok=True)

    task(username=args.username, output_dir=args.output_dir)