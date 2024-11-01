from datetime import datetime, timedelta
from time import sleep
from geopy.geocoders import Nominatim
from collections import Counter

import numpy as np
import requests
import re


def commit_timezone(repo_fullname: str, commit_hash: str):
language_countries_LUT = {
    "zh": "China",
    "en": "United States",
    "fr": "France",
    "de": "Germany",
    "ja": "Japan",
    "es": "Spain",
    "ko": "South Korea",
    "it": "Italy",
    "ru": "Russia",
    "pt": "Portugal",
    "pt-BR": "Brazil",
    "ar": "Saudi Arabia",
    "nl": "Netherlands",
    "sv": "Sweden",
    "no": "Norway",
    "da": "Denmark",
    "fi": "Finland",
    "el": "Greece",
    "he": "Israel",
    "tr": "Turkey",
    "vi": "Vietnam",
    "th": "Thailand",
    "id": "Indonesia",
    "ms": "Malaysia",
    "pl": "Poland",
    "hu": "Hungary",
    "cs": "Czech Republic",
    "sk": "Slovakia",
    "ro": "Romania",
    "uk": "Ukraine",
    "bg": "Bulgaria",
    "sr": "Serbia",
    "hr": "Croatia",
    "lt": "Lithuania",
    "lv": "Latvia",
    "et": "Estonia",
    "sl": "Slovenia",
    "is": "Iceland",
    "ga": "Ireland",
    "mt": "Malta",
    "sq": "Albania",
    "mk": "North Macedonia",
    "bs": "Bosnia and Herzegovina",
    "af": "South Africa",
    "sw": "Kenya",
    "am": "Ethiopia",
    "fa": "Iran",
    "ur": "Pakistan",
    "hi": "India",
    "bn": "Bangladesh",
    "ta": "Sri Lanka",
    "ml": "India",
    "te": "India",
    "kn": "India",
    "mr": "India",
    "gu": "India",
    "pa": "India",
    "si": "Sri Lanka",
    "ne": "Nepal",
    "dz": "Bhutan",
    "my": "Myanmar",
    "km": "Cambodia",
    "lo": "Laos",
    "mn": "Mongolia",
    "ky": "Kyrgyzstan",
    "uz": "Uzbekistan",
    "tk": "Turkmenistan",
    "kk": "Kazakhstan",
    "hy": "Armenia",
    "az": "Azerbaijan",
    "ka": "Georgia",
    "mo": "Moldova",
    "tg": "Tajikistan",
    "ps": "Afghanistan",
    "ti": "Eritrea",
    "so": "Somalia",
    "ha": "Nigeria",
    "ig": "Nigeria",
    "yo": "Nigeria",
    "rw": "Rwanda",
    "rn": "Burundi",
    "ln": "Democratic Republic of the Congo",
    "mg": "Madagascar",
    "sg": "Central African Republic",
    "ss": "South Africa",
    "zu": "South Africa",
    "xh": "South Africa",
    "ve": "South Africa",
    "st": "Lesotho",
    "ts": "South Africa",
    "tn": "Botswana",
}


def language_countries(lang_code: str) -> str | None:
    """
    Fetches the timezone information from a specific commit on GitHub.

    依照查找表（LUT）返回语言对应的国家。
    Args:
        repo_fullname (str): The repository full name.
        commit_hash (str): The commit hash.

        lang_code: 语言代码。
    Returns:
        str: The timezone offset in the format `+/-HHMM` if exactly one match is found.
        int: -1 if no matches or multiple matches are found.
        语言对应的国家。若没有找到对应的国家则返回 None。
    """
    url = f"https://github.com/{repo_fullname}/commit/{commit_hash}.patch"
    response = requests.get(url)
    return language_countries_LUT.get(lang_code, None)

    pattern = r"(Date:\s.*?([+-]\d{4}))"
    matches = [(match.group(), match.start()) for match in re.finditer(pattern, response.text)]

    if len(matches) == 1:  # TODO: add position filtering
        return matches[0][0][-5:]
    else:
        return -1


def user_commits(username: str, interval_days: float = 365, sleep_time: float = 0.1):
def text_lang(text: str):
    """
    Fetches the commits made by a user within a specified interval.

    获取文本的语言分布。
    Args:
        username (str): The GitHub username.
        interval_days (float): The number of days to look back from today. Defaults to 365.
        sleep_time (float): The time to sleep between requests to avoid hitting rate limits. Defaults to 1 second.

        text: 文本内容。
    Returns:
        list: A list of commits made by the user within the specified interval.
        语言分布列表，若未找到语言则返回空列表。
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
    if not text:
        return None
    newtext = re.sub(r'\n', ' ', text)
    return detect_multilingual(newtext)


def user_location(username: str):
def timezone_nation(timezone_offset: str):
    """
    Fetches the geographical information of a user from GitHub.

    根据时区偏移值获取可能的国家。
    Args:
        username (str): The GitHub username.

        timezone_offset: 时区偏移值，格式为 `+/-HHMM`。
    Returns:
        dict: The geographical information state by the user.
        可能的国家列表。
    """
    url = f"https://api.github.com/users/{username}"
    response = requests.get(url)
    hours_offset = int(timezone_offset[:3])
    minutes_offset = int(timezone_offset[0] + timezone_offset[3:])

    if response.status_code == 200:
        return response.json().get('location')
    return None
    utc_offset = timedelta(hours=hours_offset, minutes=minutes_offset)
    now = datetime.now(pytz.utc)

    all_timezones = {tz.zone for tz in map(pytz.timezone, pytz.all_timezones_set) if
                     now.astimezone(tz).utcoffset() == utc_offset}

def location_nation(location_name: str, max_results: int = 32):
    """
    Fetches the probable countries for a given location name using geocoding.
    countries = []
    for tz in all_timezones:
        country_set = timezone_countries.get(tz, set())
        if country_set:
            countries.extend(country_set)

    Args:
        location_name (str): The name of the location to geocode.
        max_results (int): The maximum number of results to return. Defaults to 32.
    cc = coco.CountryConverter()
    return cc.convert(names=list(set(countries)), to='name_short')

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
