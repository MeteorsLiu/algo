from icehub import Icehub, log
from tqdm import tqdm

ice = Icehub()

li = ice.get_user_info_empty('issue_count')
_set = {i['username'] for i in li}
for user in tqdm(_set, 'save_user_issues'):
    ice.save_user_issues_or_pullrequest(user, qualifier='is:issue')

li = ice.get_user_info_empty('pr_count')
_set = {i['username'] for i in li}
for user in tqdm(_set, 'save_user_pull-request'):
    ice.save_user_issues_or_pullrequest(user, qualifier='is:pull-request')

