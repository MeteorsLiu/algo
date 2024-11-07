import utils
import utils_online

from concurrent.futures import ThreadPoolExecutor, as_completed


def from_profile(username: str, token: str):
    user_info = utils_online.user_info(username, token)
    if user_info.get('location') is not None:
        location_nation = utils_online.location_nation(user_info.get('location'))
        if location_nation is not None:
            return {'nation': location_nation, "probability": 1}
        else:
            print(f"没有找到“{user_info.get('location')}”对应的国家。")
            return None
    else:
        print(f"{username} 没有填写位置信息。")
        return None


def from_readme(username: str, token: str, concurrency: int = 10):
    repos = utils_online.user_repos(username)
    if not repos or len(repos) == 0:
        print(f"{username} 没有仓库。")
        return None

    def fetch_readme_lang_distribution(repo):
        readme = utils_online.repo_readme(repo_fullname=repo, token=token)
        if readme is not None:
            return utils.text_lang(readme)
        return None

    readme_langs = {}
    entry_count = 0
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = {executor.submit(fetch_readme_lang_distribution, repo): repo for repo in repos}
        for future in as_completed(futures):
            lang_distribution = future.result()
            if lang_distribution is None:
                continue

            entry_count += 1
            for item in lang_distribution:
                readme_langs[item['lang']] = readme_langs.get(item['lang'], 0) + item['score']

    if entry_count > 0:
        readme_langs.pop('en', None)
        if readme_langs:
            readme_nation_probability = max(readme_langs.values()) / entry_count
            readme_nation_name = utils.language_countries(max(readme_langs, key=readme_langs.get))
            if readme_nation_name is not None:
                return {'nation': readme_nation_name, "probability": readme_nation_probability}
            else:
                print("语言未知")
                return None
    else:
        print(f"{username} 的仓库没有可用的 README 信息。")
        return None


def from_relationship(username: str, token: str, concurrency: int = 10):
    mutual_followings = utils_online.user_mutual_follows(username, token)
    if not mutual_followings:
        print(f"{username} 没有共同关注的 GitHub 用户。")
        return None

    def fetch_user_nation(user):
        _profile = from_profile(user, token)
        if _profile is not None:
            return _profile
        else:
            return from_readme(user, token)

    nations = {}
    valid_data = 0
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = {executor.submit(fetch_user_nation, user): user for user in mutual_followings}
        for future in as_completed(futures):
            nation = future.result()
            if nation is not None and nation.get('nation') is not None:
                try:
                    nations[nation['nation']] = nations.get(nation['nation'], 0) + nation['probability']
                    valid_data += 1
                except Exception as e:
                    print(f"Error: {e}")

    if nations:
        most_likely_nation = max(nations, key=nations.get)
        most_likely_nation_probability = nations[most_likely_nation] / valid_data
        return {'nation': most_likely_nation, "probability": most_likely_nation_probability}
    else:
        print(f"没有找到共同关注列表中 GitHub 用户的国家信息。")
        return None


def from_commits(username: str, token: str, concurrency: int = 10):
    commits = utils_online.user_commits(username, token, 8)
    if not commits or len(commits) == 0:
        print(f"{username} 没有提交记录。")
        return None

    def fetch_commit_timezone(commit):
        return utils_online.commit_timezone(commit['repository']['full_name'], commit['sha'])

    timezones = {}
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = {executor.submit(fetch_commit_timezone, commit): commit for commit in commits}
        for future in as_completed(futures):
            timezone = future.result()
            if timezone is not None:
                timezones[timezone] = timezones.get(timezone, 0) + 1

    if not timezones:
        print(f"{username} 的提交记录没有有效的时区信息。")
        return None
    else:
        # TODO: 确定应该返回时区偏移量还是国家列表
        most_often_timezone = max(timezones, key=timezones.get)
        most_often_nation = utils.timezone_nation(most_often_timezone)
        most_often_nation_probability = timezones[most_often_timezone] / sum(timezones.values())
        return {'nation': most_often_timezone, "probability": most_often_nation_probability}


def get_nation(username: str, token: str, concurrency: int = 32):
    profile = from_profile(username, token)
    if profile is not None:
        return profile

    readme = from_readme(username, token, concurrency)
    if readme is not None:
        return readme

    relationship = from_relationship(username, token, concurrency)
    if relationship is not None:
        return relationship

    commits = from_commits(username, token, concurrency)
    if commits is not None:
        return commits

    print(f"无法确定 {username} 的国家信息。")
    return None


print(get_nation("deemoe404", "xxxxxxx"))
