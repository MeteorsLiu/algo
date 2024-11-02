from time import sleep

import utils
import utils_online


def get_user_nation(username: str, token: str = None):
    """
    获取用户的国家信息。
    Args:
        username: GitHub 用户名。
        token: GitHub API 访问令牌。
    Returns:
        用户的国家信息 {"nation": str, "probability": float}。
    """
    # 尝试从用户自述信息中获取国家信息
    user_info = utils_online.user_info(username)
    if user_info.get('location') is not None:
        location_nation = utils_online.location_nation(user_info.get('location'))
        if location_nation is not None:
            return {'nation': location_nation, "probability": 1}
        else:
            print(f"没有找到“{user_info.get('location')}”对应的国家。")
    else:
        print(f"{username} 没有填写位置信息。")

    # 尝试从用户仓库的 README 语言中推断国家信息（排除英文）
    readme_langs = {}
    entry_count = 0
    for repo in utils_online.user_repos(username):
        readme = utils_online.repo_readme(repo_fullname=repo['full_name'], token=token)
        if readme is None: continue

        lang_distribution = utils.text_lang(readme)
        if lang_distribution is None: continue

        entry_count += 1
        for item in lang_distribution:
            readme_langs[item['lang']] = readme_langs.get(item['lang'], 0) + item['score']

    if entry_count > 0:
        readme_langs.pop('en', None) # 排除英文
        readme_nation_probability = max(readme_langs.values()) / entry_count
        readme_nation_name = utils.language_countries(max(readme_langs, key=readme_langs.get))
        if readme_nation_probability > 0.2 and readme_nation_name is not None:
            return {'nation': readme_nation_name, "probability": readme_nation_probability}
        else:
            print(f"README 置信概率低 {readme_langs}。")

    # 尝试从用户提交记录中推断国家信息
    # TODO: 确定应该返回时区偏移量还是国家列表
    timezones = {}
    for commit in utils_online.user_commits(username, maximum=8):
        timezone = utils_online.commit_timezone(commit['repository']['full_name'], commit['sha'])
        if timezone != -1:
            timezones[timezone] = timezones.get(timezone, 0) + 1
    if not timezones:
        print(f"{username} 没有提交记录。")
        return None
    else:
        most_often_timezone = max(timezones, key=timezones.get)
        most_often_nation = utils.timezone_nation(most_often_timezone)
        most_often_nation_probability = timezones[most_often_timezone] / sum(timezones.values())
        return {'nation': most_often_timezone, "probability": most_often_nation_probability}

print(get_user_nation("TwilightLemon"))
