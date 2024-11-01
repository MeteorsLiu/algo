from datetime import datetime, timedelta
from time import sleep
from geopy.geocoders import Nominatim
from collections import Counter

import numpy as np
import requests
import re


def commit_timezone(repo_fullname: str, commit_hash: str):
    """
    Fetches the timezone information from a specific commit on GitHub.

    Args:
        repo_fullname (str): The repository full name.
        commit_hash (str): The commit hash.

    Returns:
        str: The timezone offset in the format `+/-HHMM` if exactly one match is found.
        int: -1 if no matches or multiple matches are found.
    """
    url = f"https://github.com/{repo_fullname}/commit/{commit_hash}.patch"
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


def user_location(username: str):
    """
    Fetches the geographical information of a user from GitHub.

    Args:
        username (str): The GitHub username.

    Returns:
        dict: The geographical information state by the user.
    """
    url = f"https://api.github.com/users/{username}"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json().get('location')
    return None


def location_nation(location_name: str, max_results: int = 32):
    """
    Fetches the probable countries for a given location name using geocoding.

    Args:
        location_name (str): The name of the location to geocode.
        max_results (int): The maximum number of results to return. Defaults to 32.

    Returns:
        list: A list of dictionaries containing country names and their probabilities.
    """
    geolocator = Nominatim(user_agent="algo-demo-geo")
    locations = geolocator.geocode(location_name, exactly_one=False, limit=max_results)

    country_counts = Counter()

    if locations:
        for loc in locations:
            address = loc.raw.get("display_name", "")
            address_parts = address.split(", ")
            country = address_parts[-1] if address_parts else "Unknown"
            country_counts[country] += 1

    counts = np.array(list(country_counts.values()), dtype=np.float32)
    softmax_probs = np.exp(counts) / np.sum(np.exp(counts))

    result = [
        {"country": country, "probability": prob}
        for country, prob in zip(country_counts.keys(), softmax_probs)
    ]

    return result
