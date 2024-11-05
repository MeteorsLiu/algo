import base64
import json
import re
from datetime import datetime
from time import sleep

import requests
from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim


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
        return -1


def user_info(username: str, token: str = None) -> dict:
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
    response = requests.get(f"https://api.github.com/users/{username}/repos")
    if response.status_code != 200:
        return []
    return json.loads(response.text)


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


def user_commits(username: str, maximum: int = 32, sleep_time: float = 0.1):
    """
    获取用户在 GitHub 上的提交记录。
    Args:
        username: GitHub 用户名。
        sleep_time: 请求之间的休眠时间，以避免触发速率限制。默认为 0.1 秒。
        maximum: 最大获取提交数。默认为 32。GitHub API 限制为 300。
    Returns:
        提交记录列表，若未找到提交则返回空列表。
    """
    url = f'https://api.github.com/search/commits?q=author:{username}'

    commits = []
    while url and len(commits) < maximum:
        response = requests.get(url)
        commits.extend(response.json().get('items', []))
        url = response.links.get('next', {}).get('url')
        sleep(sleep_time)
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
    geolocator = Nominatim(user_agent="algo-demo-geo")
    location = geolocator.geocode(location_name, exactly_one=True)

    if location:
        address_parts = location.raw.get("display_name", "").split(", ")
        country_name = address_parts[-1] if address_parts else None
        return {"nation": country_name, "display_name": location.raw.get("display_name", "")}
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


def contributors_count(full_name: str):
    url = f"https://github.com/{full_name}/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        contributors_element = soup.find("a", {"class": "Link--inTextBlock Link",
                                               "href": f"/{full_name}/graphs/contributors"})
        if contributors_element:
            contributors_text = contributors_element.get_text(strip=True)
            return int(contributors_text.split()[1].replace(',', ''))
        else:
            print(f"contributors_element not found: {full_name}")
            return 0
    else:
        print(f"contributors response status code: {response.status_code}")
        return None


def issue_count(full_name: str):
    url = f"https://github.com/{full_name}/issues"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        closed_element = soup.find("a", {"href": f"/{full_name}/issues?q=is%3Aissue+is%3Aclosed"})
        open_element = soup.find("a", {"href": f"/{full_name}/issues?q=is%3Aopen+is%3Aissue"})
        if closed_element and open_element:
            closed_text = closed_element.get_text(strip=True)
            open_text = open_element.get_text(strip=True)

            closed_count = int(closed_text.split()[0].replace(',', ''))
            open_count = int(open_text.split()[0].replace(',', ''))

            return {"closed": closed_count, "open": open_count}
        else:
            print(f"issue_element not found: {full_name}")
            return 0
    else:
        print(f"issue response status code: {response.status_code}")
        return None


def repo_stats(repo_fullname: str, token: str = None):
    """
    获取 GitHub 仓库的统计信息。
    Args:
        repo_fullname: 仓库全名。
        token: GitHub API 访问令牌。
    Returns:
        仓库统计信息。包括：

        1. 影响力
            - star 数量
            - fork 数量
            - watch 数量
            - used by 数量
            - contributor 数量
        2. 社区健康度
            - 已解决的 issue 占比
            - issue 的频率（issue 数量比上仓库创建时间）
    """
    response = requests.get(url=f"https://api.github.com/repos/{repo_fullname}",
                            headers={"Authorization": f"Bearer {token}"})

    if response.status_code != 200:
        return None

    repo_info = response.json()
    stars = repo_info.get('stargazers_count')
    forks = repo_info.get('forks_count')
    watchers = repo_info.get('subscribers_count')

    used_by_count = used_by(repo_fullname)
    if used_by_count is None:
        return None

    contributors = contributors_count(repo_fullname)
    if contributors is None:
        return None

    issues = issue_count(repo_fullname)
    if issues is None:
        return None

    if issues['open'] + issues['closed'] > 0:
        closed_proportion = issues['closed'] / (issues['closed'] + issues['open'])
    else:
        closed_proportion = 0

    if repo_info.get('created_at') and repo_info.get('updated_at'):
        created_at = datetime.fromisoformat(repo_info.get('created_at').replace("Z", "+00:00"))
        updated_at = datetime.fromisoformat(repo_info.get('updated_at').replace("Z", "+00:00"))
        created_timespan = (updated_at - created_at).days

        issue_rate = (issues['closed'] + issues['open']) / created_timespan if created_timespan > 0 else 0
    else:
        issue_rate = 0

    return {
        "stars": stars,
        "forks": forks,
        "watchers": watchers,
        "used_by": used_by_count,
        "contributors": contributors,
        "closed_proportion": closed_proportion,
        "issue_rate": issue_rate
    }
