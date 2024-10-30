from datetime import datetime, timedelta
from time import sleep

import requests
import re

def commit_timezone(username: str, repo: str, commit_hash: str):
    """
    Fetches the timezone information from a specific commit on GitHub.

    Args:
        username (str): The GitHub username.
        repo (str): The repository name.
        commit_hash (str): The commit hash.

    Returns:
        str: The timezone offset in the format `+/-HHMM` if exactly one match is found.
        int: -1 if no matches or multiple matches are found.
    """
    url = f"https://github.com/{username}/{repo}/commit/{commit_hash}.patch"
    response = requests.get(url)

    pattern = r"(Date:\s.*?([+-]\d{4}))"
    matches = [(match.group(), match.start()) for match in re.finditer(pattern, response.text)]

    if len(matches) == 1:  # TODO: add position filtering
        return matches[0][0][-5:]
    else:
        return -1


def user_commits(username: str, interval_days: float = 365, sleep_time: float = 0.1):
    """
    Fetches the commits made by a user within a specified interval.

    Args:
        username (str): The GitHub username.
        interval_days (float): The number of days to look back from today. Defaults to 365.
        sleep_time (float): The time to sleep between requests to avoid hitting rate limits. Defaults to 1 second.

    Returns:
        list: A list of commits made by the user within the specified interval.
    """
    url_template = 'https://api.github.com/search/commits?q=author:{author}+committer-date:{start}..{end}'

    end_date = datetime.date(datetime.now())
    start_date = end_date - timedelta(days=interval_days)
    commits = []
    url = url_template.format(author=username, start=start_date, end=end_date)

    while url:
        response = requests.get(url)
        data = response.json()
        commits.extend(data.get('items', []))
        url = response.links.get('next', {}).get('url')
        sleep(sleep_time)
    return commits
