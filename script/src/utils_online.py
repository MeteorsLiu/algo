import base64
import re
from datetime import datetime
from time import sleep

import numpy as np
import requests
from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim
from numpy.distutils.conv_template import header


def commit_timezone(repo_fullname: str, commit_hash: str):
    """
    获取 commit 对应的时区。
    Args:
        repo_fullname: 仓库全名。
        commit_hash: commit 的哈希值。
    Returns:
        时区偏移值，格式为 `+/-HHMM`，若未找到或匹配异常则返回 -1。
    """
    url = f"https://github.com/{repo_fullname}/commit/{commit_hash}.patch"
    response = requests.get(url)

    pattern = r"(Date:\s.*?([+-]\d{4}))"
    matches = [(match.group(), match.start()) for match in re.finditer(pattern, response.text)]

    if len(matches) == 1:  # TODO: 添加匹配位置过滤，避免正文中出现类似格式字符串
        return matches[0][0][-5:]
    else:
        return None


def user_info(username: str, token: str) -> dict:
    """
    获取 GitHub 用户信息。
    Args:
        username: GitHub 用户名。
        token: GitHub API 访问令牌。
    Returns:
        用户信息。
    """
    response = requests.get(url=f"https://api.github.com/users/{username}",
                            headers={"Authorization": f"Bearer {token}"})
    return response.json()


def user_repos(username: str):
    """
    获取用户在 GitHub 上的仓库列表。
    Args:
        username: GitHub 用户名。
    Returns:
        仓库列表，若未找到仓库则返回空列表。
    """
    try:
        url = f"https://api.github.com/users/{username}/repos"

        result = []
        while url:
            response = requests.get(url)
            result.extend([repo['full_name'] for repo in response.json()])
            url = response.links.get('next', {}).get('url')

        return result
    except Exception as e:
        print(f"user_repos error: {e}")
        return None


def repo_readme(repo_fullname: str, token: str = None):
    """
    获取 GitHub 仓库的 README 内容。
    Args:
        repo_fullname: 仓库全名。
        token: GitHub API 访问令牌。
    Returns:
        README 内容。
    """
    response = requests.get(url=f"https://api.github.com/repos/{repo_fullname}/readme",
                            headers={"Authorization": f"Bearer {token}"})
    if response.status_code != 200:
        return None
    readme = response.json().get('content')
    if readme is not None:
        readme = base64.b64decode(readme).decode('utf-8')
    return readme


def user_commits(username: str, token: str, maximum: int = 32):
    """
    获取用户在 GitHub 上的提交记录。
    Args:
        username: GitHub 用户名。
        token: GitHub API 访问令牌。
        maximum: 最大获取提交数。默认为 32。GitHub API 限制为 300。
    Returns:
        提交记录列表，若未找到提交则返回空列表。
    """
    url = f'https://api.github.com/search/commits?q=author:{username}'
    headers = {"Authorization": f"Bearer {token}"}

    commits = []
    while url and len(commits) < maximum:
        response = requests.get(url=url, headers=headers)
        commits.extend(response.json().get('items', []))
        url = response.links.get('next', {}).get('url')
    return commits


def user_mutual_follows(username, token):
    """
    获取用户的双向关注列表。
    Args:
        username: GitHub 用户名。
        token: GitHub API 访问令牌。
    Returns:
        双向关注列表。
    """

    def get_user_list(url):
        user_list = []
        while url:
            response = requests.get(url, headers={"Authorization": f"Bearer {token}"})
            user_list.extend([user['login'] for user in response.json()])
            url = response.links.get('next', {}).get('url')
        return set(user_list)

    following = get_user_list(f"https://api.github.com/users/{username}/following")
    followers = get_user_list(f"https://api.github.com/users/{username}/followers")

    mutual_follows = following.intersection(followers)
    return list(mutual_follows)


def location_nation(location_name: str) -> dict | None:
    """
    根据自然语言提供的位置名称获取可能的国家。
    Args:
        location_name: 位置名称。
    Returns:
        "nation" 键对应国家名称，"display_name" 键对应完整位置名称。返回 None 如果未找到匹配的国家。
    """
    try:
        geolocator = Nominatim(user_agent="algo-demo-geo")
        location = geolocator.geocode(location_name, exactly_one=True)

        if location:
            address_parts = location.raw.get("display_name", "").split(", ")
            country_name = address_parts[-1] if address_parts else None
            return {"nation": country_name, "display_name": location.raw.get("display_name", "")}
        return None
    except Exception as e:
        print(f"API Error: {e}")
        return None


def public_repos(token: str = None, limitation: int = 100, since: int = 3442157):
    """
    获取 GitHub 上的公共仓库列表。
    Args:
        token: GitHub API 访问令牌。
        limitation: 限制返回的仓库数量。默认为 100。
        since: 仓库 ID 的起始值。默认为 3442157。
    Returns:
        仓库列表。
    """
    result = []
    url = f"https://api.github.com/repositories?since={since}"
    while url and limitation > 0:
        response = requests.get(url, headers={"Authorization": f"Bearer {token}"})
        result.extend([repo['full_name'] for repo in response.json()])
        url = response.links.get('next', {}).get('url')
        limitation -= 1


def used_by(full_name: str):
    """
    获取仓库的使用者数量。
    Args:
        full_name: 仓库全名。
    Returns:
        使用者数量。
    """
    url = f"https://github.com/{full_name}/network/dependents"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        used_by_element = soup.find("a", {"href": f"/{full_name}/network/dependents?dependent_type=REPOSITORY"})
        if used_by_element:
            used_by_result = used_by_element.get_text(strip=True).split()[0]
            return int(used_by_result.replace(',', ''))
        else:
            print(f"used_by_element not found: {full_name}")
            return 0
    else:
        print(f"used_by response status code: {response.status_code}")
        return None


def page_count(url: str, headers: dict):
    response = requests.get(url=url, headers=headers)
    last_url = response.links.get('last', {}).get('url', None)

    if last_url is None:
        return 0
    page_num = int(response.links.get('last', {}).get('url', "").split("=")[-1])

    return page_num


def contributors_count(full_name: str, token: str):
    url = f"https://api.github.com/repos/{full_name}/contributors?per_page=1&anon=true"
    headers = {"Authorization": f"Bearer {token}"}

    try:
        return page_count(url, headers)
    except Exception as e:
        print(f"contributors_count error: {e}")
        return None


def commit_count(full_name: str, token: str):
    url = f"https://api.github.com/repos/{full_name}/commits?per_page=1&page=1"
    headers = {"Authorization": f"Bearer {token}"}

    try:
        return page_count(url, headers)
    except Exception as e:
        print(f"commit_count error: {e}")
        return None


def issue_count(full_name: str, token: str):
    closed_url = f"https://api.github.com/search/issues?q=repo:{full_name}+type:issue+state:closed&page=0&per_page=1"
    open_url = f"https://api.github.com/search/issues?q=repo:{full_name}+type:issue+state:open&page=0&per_page=1"
    headers = {"Authorization": f"Bearer {token}"}

    try:
        closed_response = requests.get(closed_url, headers=headers)
        open_response = requests.get(open_url, headers=headers)

        closed_count = closed_response.json().get('total_count', 0)
        open_count = open_response.json().get('total_count', 0)

        return {"closed": closed_count, "open": open_count}
    except Exception as e:
        print(f"issue_count error: {e}")
        return None


def repo_stats(repo_fullname: str, token: str = None):
    """
    获取 GitHub 仓库的统计信息。
    Args:
        repo_fullname: 仓库全名。
        token: GitHub API 访问令牌。
    Returns:
        自然对数仓库统计信息（频率定义为数量比上仓库创建到最后一次更新的间隔，单位为天）。包括：

        1. 影响力
            - star 数量
            - fork 数量
            - watch 数量
            - used by 数量
            - contributor 数量
        2. 社区健康度
            - commit 频率
            - 已解决的 issue 占比 * issue 的频率
    """
    result = {}

    commits = commit_count(repo_fullname, token)
    if commits is None or commits == 0:
        return None

    try:
        response = requests.get(url=f"https://api.github.com/repos/{repo_fullname}",
                                headers={"Authorization": f"Bearer {token}"})
        repo_info = response.json()

        created_at = datetime.fromisoformat(repo_info.get('created_at').replace("Z", "+00:00"))
        updated_at = datetime.fromisoformat(repo_info.get('updated_at').replace("Z", "+00:00"))
        created_timespan = (updated_at - created_at).days + 1
        if repo_info.get('fork') == True and created_timespan < 1:
            return None

        result["stars"] = np.log(repo_info.get('stargazers_count') + 1)
        result["forks"] = np.log(repo_info.get('forks_count') + 1)
        result["watchers"] = np.log(repo_info.get('subscribers_count') + 1)
    except Exception as e:
        print(f"repo_info error: {e}")
        return None

    used_by_count = used_by(repo_fullname)
    if used_by_count is None:
        return None
    result["used_by"] = np.log(used_by_count + 1)

    contributors = contributors_count(repo_fullname, token)
    if contributors is None:
        return None
    result["contributors"] = np.log(contributors + 1)

    issues = issue_count(repo_fullname, token)
    if issues is None:
        return None

    if issues['open'] + issues['closed'] > 0:
        closed_proportion = issues['closed'] / (issues['closed'] + issues['open'])
    else:
        closed_proportion = 0

    issue_rate = (issues['closed'] + issues['open']) / created_timespan if created_timespan > 0 else 0
    result["issue_rate"] = np.log(closed_proportion * issue_rate + 1)
    result["commit_rate"] = np.log(commits / created_timespan + 1)

    return result
