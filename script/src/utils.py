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
