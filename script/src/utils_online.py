import base64
import json
from time import sleep

import requests
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

    if len(matches) == 1:  # TODO: add position filtering
        return matches[0][0][-5:]
    else:
        return -1


def user_info(username: str) -> dict:
    """
    获取 GitHub 用户信息。
    Args:
        username: GitHub 用户名。
    Returns:
        用户信息。
    """
    response = requests.get(f"https://api.github.com/users/{username}")
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


def repo_readme(repo_fullname: str):
    """
    获取 GitHub 仓库的 README 内容。
    Args:
        repo_fullname: 仓库全名。
    Returns:
        README 内容。
    """
    response = requests.get(f"https://api.github.com/repos/{repo_fullname}/readme")
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
