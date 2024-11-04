import re
from datetime import datetime, timedelta

import country_converter as coco
import pycountry
import pytz
import tldextract
from fast_langdetect import detect_multilingual
from pytz import country_timezones

timezone_countries = {}
for country, timezones in country_timezones.items():
    for timezone in timezones:
        timezone_countries.setdefault(timezone, set()).add(country)

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
    依照查找表（LUT）返回语言对应的国家。
    Args:
        lang_code: 语言代码。
    Returns:
        语言对应的国家。若没有找到对应的国家则返回 None。
    """
    return language_countries_LUT.get(lang_code, None)


def text_lang(text: str):
    """
    获取文本的语言分布。
    Args:
        text: 文本内容。
    Returns:
        语言分布列表，若未找到语言则返回空列表。
    """
    if not text:
        return None
    newtext = re.sub(r'\n', ' ', text)
    return detect_multilingual(newtext)


def timezone_nation(timezone_offset: str):
    """
    根据时区偏移值获取可能的国家。
    Args:
        timezone_offset: 时区偏移值，格式为 `+/-HHMM`。
    Returns:
        可能的国家列表。
    """
    hours_offset = int(timezone_offset[:3])
    minutes_offset = int(timezone_offset[0] + timezone_offset[3:])

    utc_offset = timedelta(hours=hours_offset, minutes=minutes_offset)
    now = datetime.now(pytz.utc)

    all_timezones = {tz.zone for tz in map(pytz.timezone, pytz.all_timezones_set) if
                     now.astimezone(tz).utcoffset() == utc_offset}

    countries = []
    for tz in all_timezones:
        country_set = timezone_countries.get(tz, set())
        if country_set:
            countries.extend(country_set)

    cc = coco.CountryConverter()
    return cc.convert(names=list(set(countries)), to='name_short')


def email_nation(email: str):
    """
    根据电子邮件地址获取可能的国家。
    Args:
        email: 电子邮件地址。
    Returns:
        可能的国家名称。
    """
    extracted = tldextract.extract(email)
    tld = extracted.suffix

    result = None
    if len(tld) == 2:
        result = pycountry.countries.get(alpha_2=tld.upper())

    return result.name if result else None


def z_score(data: list[float], mean: float, std: float) -> list[float]:
    """
    计算标准分数。
    Args:
        data: 数据列表。
        mean: 平均值。
        std: 标准差。
    Returns:
        标准分数列表。
    """
    return [(x - mean) / std for x in data]
