from time import sleep

import utils
import utils_online


def get_user_nation(username: str):
    user_info = utils_online.user_info(username)
    if user_info.get('location') is not None:
        location_nation = utils_online.location_nation(user_info.get('location'))
        if location_nation is not None:
            return location_nation

    sleep(1)

    readme_langs = {}
    entry_count = 0
    for repo in utils_online.user_repos(username):
        readme = utils_online.repo_readme(repo['full_name'])
        if readme is None: continue

        lang_distribution = utils.text_lang(readme)
        if lang_distribution is None: continue

        entry_count += 1
        for item in lang_distribution:
            readme_langs[item['lang']] = readme_langs.get(item['lang'], 0) + item['score']

    if entry_count > 0:
        readme_langs.pop('en', None)
        readme_nation_probability = max(readme_langs.values()) / entry_count
        readme_nation_name = utils.language_countries(max(readme_langs, key=readme_langs.get))
        if max(readme_langs.values()) / entry_count > 0.2 and readme_nation_name is not None:
            return {'nation': readme_nation_name, "probability": readme_nation_probability}

    timezones = {}
    for commit in utils_online.user_commits(username):
        timezone = utils_online.commit_timezone(commit['repository']['full_name'], commit['sha'])
        if timezone != -1:
            timezones[timezone] = timezones.get(timezone, 0) + 1
    user_nations_commit = utils.timezone_nation(max(timezones, key=timezones.get))
    print(f"{username} commits from {user_nations_commit}.")
    print(max(timezones.values()) / sum(timezones.values()))


print(get_user_nation("TwilightLemon"))
