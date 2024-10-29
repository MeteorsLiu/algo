from icehub import Icehub, log
from tqdm import tqdm

ice = Icehub()

li = ice.get_empty_col_user('issue_count')
_set = {i['username'] for i in li}
for user in tqdm(_set, 'save_user_issues'):
    ice.save_user_issues_or_pullrequest(user, qualifier='is:issue')

li = ice.get_empty_col_user('pr_count')
_set = {i['username'] for i in li}
for user in tqdm(_set, 'save_user_pull-request'):
    ice.save_user_issues_or_pullrequest(user, qualifier='is:pull-request')

log.info(ice.get_rate_limit())