from icehub import Icehub, log
from tqdm import tqdm

ice = Icehub()
li = ice.get_user_list(limit=10)
for i in tqdm(li, desc='User extend by fowllowers'):
    ice.save_user_follow(user=i['username'], follow_type='followers')
for i in tqdm(li, desc='User extend by following'):
    ice.save_user_follow(user=i['username'], follow_type='following')

li = ice.get_empty_col_user('issue_count')
_set = {i['username'] for i in li}
for user in tqdm(_set, 'save_user_issues'):
    ice.save_user_issues_or_pullrequest(user, qualifier='is:issue')

li = ice.get_empty_col_user('pr_count')
_set = {i['username'] for i in li}
for user in tqdm(_set, 'save_user_pull-request'):
    ice.save_user_issues_or_pullrequest(user, qualifier='is:pull-request')

ice.get_unsaved_repo('user_issue')
ice.get_unsaved_repo('user_pr')

log.info(ice.get_rate_limit())