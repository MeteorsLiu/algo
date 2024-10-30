from icehub import Icehub, log
from tqdm import tqdm

ice = Icehub()
# 一个用户足矣, 数据很大你忍一下
li = ice.get_user_list(limit=1)

# 自选用户
li = [{'username': i} for i in ['zixing131']]

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