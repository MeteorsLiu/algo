import argparse
from icehub import Icehub, log
from tqdm import tqdm

def main(user: str = '', limit: int = 1):
    ice = Icehub()
    if user == '':
        # 一个用户足矣, 数据很大你忍一下
        li = ice.get_user_list(limit=limit)
    else:
        # 自选用户
        li = [{'username': i} for i in [user]]
    

    for i in tqdm(li, desc='User extend by fowllowers'):
        rtn = ice.save_user_follow(user=i['username'], follow_type='followers')
        if not rtn:
            break

    for i in tqdm(li, desc='User extend by following'):
        rtn = ice.save_user_follow(user=i['username'], follow_type='following')
        if not rtn:
            break

    li = ice.get_empty_col_user('issue_count')
    _set = {i['username'] for i in li}
    for user in tqdm(_set, 'save_user_issues'):
        ice.save_user_issues_or_pullrequest(user, qualifier='is:issue')

    li = ice.get_empty_col_user('pr_count')
    _set = {i['username'] for i in li}
    for user in tqdm(_set, 'save_user_pull-request'):
        ice.save_user_issues_or_pullrequest(user, qualifier='is:pull-request')

    ice.save_repository('user_issue')
    ice.save_repository('user_pr')

    log.info(ice.get_rate_limit())

if __name__ == '__main__':
    # 创建解析器
    parser = argparse.ArgumentParser(description="ICEHUB")
    
    # 添加参数
    parser.add_argument('--user', type=str, help="entry user", required=False, default='')
    parser.add_argument('--limit', type=int, default=1, help="base user collections entry limit", required=False)
    
    # 解析参数
    args = parser.parse_args()

    main(args.user, args.limit)