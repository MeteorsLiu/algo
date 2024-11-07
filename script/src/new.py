from os import utime
from random import random
from time import sleep

import pandas as pd
from pymongo import MongoClient
from scipy.signal import ellip
from sklearn.decomposition import PCA
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from random import random
from time import sleep
from tqdm import tqdm
import numpy as np

import geo
from script.src import utils_online

host = "149.56.30.123"
port = 27017
username = "mango"
password = "110b80ed9d60b59a9889b9236ea33b35"

uri = f"mongodb://{username}:{password}@{host}:{port}"

client = MongoClient(uri)

db = client["algodb"]
repo_collection = db["repo_info"]
user_collection = db["user_info"]
issue_collection = db["user_issue"]
pr_collection = db["user_pr"]

# def get_random_user_without_geo(user_collection_func):
#     pipeline = [
#         {"$match": {"geo": {"$exists": False}}},
#         {"$sample": {"size": 1}}
#     ]
#     result = list(user_collection_func.aggregate(pipeline))
#     return result[0] if result else None
#
#
# def process_user_geo(user_collection_def, geo_def):
#     try:
#         user_no_geo = get_random_user_without_geo(user_collection)
#         if not user_no_geo:
#             return
#
#         user_geo = geo_def.get_nation(user_no_geo["username"], "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")
#         user_geo_nation = user_geo["nation"]
#         user_geo_prob = user_geo["probability"]
#
#         user_collection_def.update_one({"username": user_no_geo["username"]}, {
#             "$set": {
#                 "geo": user_geo_nation,
#                 "geo_prob": user_geo_prob
#             }
#         })
#
#         random_sleep_time = 1 + 20 * random()
#         sleep(random_sleep_time)
#
#     except Exception as e:
#         pass#print(e)
#
#
# def main(user_collection_main, geo_main, max_workers=32):
#     with ThreadPoolExecutor(max_workers=max_workers) as executor:
#         futures = [executor.submit(process_user_geo, user_collection_main, geo_main) for _ in range(5163)]
#         for future in tqdm(as_completed(futures), total=5163):
#             pass
#
#
# main(user_collection, geo)

# # get ramdon 10 repos
# repos_learn = list(repo_collection.aggregate([{"$sample": {"size": 10}}]))
# # repos_learn = list(repo_collection.find({}, {
# #     'full_name': 1,
# #     'forks_count': 1,
# #     'stargazers_count': 1,
# #     'subscribers_count': 1,
# #     'watchers_count': 1
# # }).limit(100000))
# repos_to_learn = []
# for repo_learn in repos_learn:
#     try:
#         repo_prs_learn = len(list(pr_collection.find({"full_name": repo_learn["full_name"]})))
#         repo_issues_learn = len(list(issue_collection.find({"full_name": repo_learn["full_name"]})))
#         repos_to_learn.append({
#             "full_name": repo_learn["full_name"],
#             "stars": np.log(repo_learn["stargazers_count"] + 1),
#             "forks": np.log(repo_learn["forks_count"] + 1),
#             "watches": np.log(repo_learn["watchers_count"] + 1),
#             "subscribers": np.log(repo_learn["subscribers_count"] + 1),
#             "issues": np.log(repo_prs_learn + 1),
#             "prs": np.log(repo_issues_learn + 1)
#         })
#     except Exception as e:
#         print(repo_learn, e)
#
# repos_to_learn_df = pd.DataFrame(repos_to_learn).drop(columns=["full_name"])
# pca = PCA(n_components=6)
# principal_components = pca.fit_transform(repos_to_learn_df)
#
# loadings = pca.components_
# loadings_df = pd.DataFrame(loadings, columns=repos_to_learn_df.columns)
# print("Principal Component Loadings:")
# print(loadings_df)
#
# mean = repos_to_learn_df.mean()
# std = repos_to_learn_df.std()
# print("Mean:")
# print(mean)
# print("Standard Deviation:")
# print(std)

mean_final = {
    "stars": 4.160266,
    "forks": 2.989522,
    "watches": 4.160266,
    "subscribers": 2.329286,
    "issues": 0.842846,
    "prs": 0.652200
}

std_final = {
    "stars": 2.752807,
    "forks": 2.206446,
    "watches": 2.752807,
    "subscribers": 1.417005,
    "issues": 0.945928,
    "prs": 0.893581
}

weight_final = {
    "stars": 0.594451,
    "forks": 0.4606115,
    "watches": 0.594451,
    "subscribers": 0.2720080,
    "issues": 0.08193683,
    "prs": 0.01975785
}

# user_query = "deemoe404"

# users = list(user_collection.find({"rank": {"$exists": False}}))
# i = len(users)
# for user in users:
#     if user:
#         issue_repos = list(
#             issue_collection.find({"user": user["username"]},
#                                   {"repo_name": 1, "repo_owner": 1, "issue_id": 1, "_id": 0}))
#         pr_repos = list(
#             pr_collection.find({"user": user["username"]}, {"repo_name": 1, "repo_owner": 1, "issue_id": 1, "_id": 0}))
#
#         user_repos = {}
#
#         for issue in issue_repos:
#             repo_name = issue["repo_name"]
#             repo_owner = issue["repo_owner"]
#             repo_key = (repo_owner, repo_name)
#
#             if repo_key not in user_repos:
#                 user_repos[repo_key] = {"issues": [], "prs": []}
#
#             user_repos[repo_key]["issues"].append(issue["issue_id"])
#
#         for pr in pr_repos:
#             repo_name = pr["repo_name"]
#             repo_owner = pr["repo_owner"]
#             repo_key = (repo_owner, repo_name)
#
#             if repo_key not in user_repos:
#                 user_repos[repo_key] = {"issues": [], "prs": []}
#
#             user_repos[repo_key]["prs"].append(pr["issue_id"])
#
#         # 得到用户所有参与过的 repo
#         formatted_repos = [
#             {"full_name": f"{owner}/{name}", "issues": data["issues"], "prs": data["prs"]}
#             for (owner, name), data in user_repos.items()
#         ]
#
#         user_languages = {}
#         repos_to_rank = []
#
#         for formatted_repo in formatted_repos:
#             repo_infos = repo_collection.find_one({"full_name": formatted_repo["full_name"]},
#                                                   {
#                                                       "language": 1,
#                                                       "stargazers_count": 1,
#                                                       "forks_count": 1,
#                                                       "watchers_count": 1,
#                                                       "subscribers_count": 1,
#                                                       "pr_count": 1,
#                                                       "issue_count": 1
#                                                   })
#             if repo_infos:
#                 # 得到用户使用过的语言
#                 language = repo_infos["language"]
#                 if language is not None:
#                     if language not in user_languages:
#                         user_languages[language] = 0
#                     user_languages[language] += 1
#
#                 # 获得给仓库打分的数据
#                 repo_prs = repo_infos["pr_count"] if "pr_count" in repo_infos else 0
#                 repo_issues = repo_infos["issue_count"] if "issue_count" in repo_infos else 0
#
#                 # 获取用户与仓库的关系系数
#                 weight_pr = (len(formatted_repo["prs"]) / repo_prs) if repo_prs > 0 else 0
#                 weight_issue = (len(formatted_repo["issues"]) / repo_issues) if repo_issues > 0 else 0
#
#                 repos_to_rank.append({
#                     "full_name": formatted_repo["full_name"],
#                     "stars": np.log(repo_infos["stargazers_count"] + 1),
#                     "forks": np.log(repo_infos["forks_count"] + 1),
#                     "watches": np.log(repo_infos["watchers_count"] + 1),
#                     "subscribers": np.log(repo_infos["subscribers_count"] + 1),
#                     "issues": np.log(repo_issues + 1),
#                     "prs": np.log(repo_prs + 1),
#                     "weight": weight_pr * 0.5 + weight_issue * 0.5
#                 })
#
#         # 进行评分
#         user_ranks = []
#         for repo in repos_to_rank:
#             rank = 0
#             for key in repo:
#                 if key in weight_final:
#                     repo[key] = (repo[key] - mean_final[key]) / std_final[key]
#                     rank += repo[key] * weight_final[key]
#             user_ranks.append(rank * repo["weight"])
#         user_ranks = sum(user_ranks) / len(user_ranks) if user_ranks else 0
#
#         # 把用户分数和语言写进数据库
#         user_collection.update_one({"username": user["username"]}, {
#             "$set": {
#                 "rank": user_ranks,
#                 "lang": user_languages
#             }
#         })
#
#         print(i, user_ranks * 10000)
#         i = i - 1

# 使用concurrent.futures进行并发执行
# def process_user(user):
#     if not user:
#         return None
#
#     issue_repos = list(
#         issue_collection.find({"user": user["username"]}, {"repo_name": 1, "repo_owner": 1, "issue_id": 1, "_id": 0})
#     )
#     pr_repos = list(
#         pr_collection.find({"user": user["username"]}, {"repo_name": 1, "repo_owner": 1, "issue_id": 1, "_id": 0})
#     )
#
#     user_repos = {}
#     for issue in issue_repos:
#         repo_key = (issue["repo_owner"], issue["repo_name"])
#         if repo_key not in user_repos:
#             user_repos[repo_key] = {"issues": [], "prs": []}
#         user_repos[repo_key]["issues"].append(issue["issue_id"])
#
#     for pr in pr_repos:
#         repo_key = (pr["repo_owner"], pr["repo_name"])
#         if repo_key not in user_repos:
#             user_repos[repo_key] = {"issues": [], "prs": []}
#         user_repos[repo_key]["prs"].append(pr["issue_id"])
#
#     formatted_repos = [
#         {"full_name": f"{owner}/{name}", "issues": data["issues"], "prs": data["prs"]}
#         for (owner, name), data in user_repos.items()
#     ]
#
#     user_languages = {}
#     repos_to_rank = []
#     for formatted_repo in formatted_repos:
#         repo_infos = repo_collection.find_one(
#             {"full_name": formatted_repo["full_name"]},
#             {"language": 1, "stargazers_count": 1, "forks_count": 1, "watchers_count": 1, "subscribers_count": 1, "pr_count": 1, "issue_count": 1}
#         )
#         if repo_infos:
#             language = repo_infos.get("language")
#             if language:
#                 user_languages[language] = user_languages.get(language, 0) + 1
#
#             repo_prs = repo_infos.get("pr_count", 0)
#             repo_issues = repo_infos.get("issue_count", 0)
#             weight_pr = (len(formatted_repo["prs"]) / repo_prs) if repo_prs > 0 else 0
#             weight_issue = (len(formatted_repo["issues"]) / repo_issues) if repo_issues > 0 else 0
#
#             repos_to_rank.append({
#                 "full_name": formatted_repo["full_name"],
#                 "stars": np.log(repo_infos.get("stargazers_count", 0) + 1),
#                 "forks": np.log(repo_infos.get("forks_count", 0) + 1),
#                 "watches": np.log(repo_infos.get("watchers_count", 0) + 1),
#                 "subscribers": np.log(repo_infos.get("subscribers_count", 0) + 1),
#                 "issues": np.log(repo_issues + 1),
#                 "prs": np.log(repo_prs + 1),
#                 "weight": weight_pr * 0.5 + weight_issue * 0.5
#             })
#
#     user_ranks = []
#     for repo in repos_to_rank:
#         rank = sum((repo.get(key, 0) - mean_final[key]) / std_final[key] * weight_final[key]
#                    for key in weight_final if key in repo)
#         user_ranks.append(rank * repo["weight"])
#
#     user_rank_score = sum(user_ranks) / len(user_ranks) if user_ranks else 0
#
#     # 更新用户的分数和语言到数据库
#     user_collection.update_one({"username": user["username"]}, {
#         "$set": {
#             "rank": user_rank_score,
#             "lang": user_languages
#         }
#     })
#
#     return user["username"], user_rank_score
#
# # 获取未打分的用户列表
# users = list(user_collection.find({"rank": {"$exists": False}}))
# total_users = len(users)
#
# # 并发处理每个用户
# with ThreadPoolExecutor(max_workers=64) as executor:
#     futures = {executor.submit(process_user, user): user for user in users}
#
#     for future in as_completed(futures):
#         result = future.result()
#         if result:
#             username, rank_score = result
#             print(f"Updated {username} with rank {rank_score * 10000}")


# def process_user(user):
#     if not user:
#         return None
#
#     issue_repos = list(
#         issue_collection.find({"user": user["username"]}, {"repo_name": 1, "repo_owner": 1, "issue_id": 1, "_id": 0})
#     )
#     pr_repos = list(
#         pr_collection.find({"user": user["username"]}, {"repo_name": 1, "repo_owner": 1, "issue_id": 1, "_id": 0})
#     )
#
#     user_repos = {}
#     for issue in issue_repos:
#         repo_key = (issue["repo_owner"], issue["repo_name"])
#         if repo_key not in user_repos:
#             user_repos[repo_key] = {"issues": [], "prs": []}
#         user_repos[repo_key]["issues"].append(issue["issue_id"])
#
#     for pr in pr_repos:
#         repo_key = (pr["repo_owner"], pr["repo_name"])
#         if repo_key not in user_repos:
#             user_repos[repo_key] = {"issues": [], "prs": []}
#         user_repos[repo_key]["prs"].append(pr["issue_id"])
#
#     formatted_repos = [
#         {"full_name": f"{owner}/{name}", "issues": data["issues"], "prs": data["prs"]}
#         for (owner, name), data in user_repos.items()
#     ]
#
#     repos_to_rank = []
#     for formatted_repo in formatted_repos:
#         repo_infos = repo_collection.find_one(
#             {"full_name": formatted_repo["full_name"]},
#             {"language": 1, "stargazers_count": 1, "forks_count": 1, "watchers_count": 1, "subscribers_count": 1,
#              "pr_count": 1, "issue_count": 1}
#         )
#         if repo_infos:
#             repo_prs = repo_infos.get("pr_count", 0)
#             repo_issues = repo_infos.get("issue_count", 0)
#             weight_pr = (len(formatted_repo["prs"]) / repo_prs) if repo_prs > 0 else 0
#             weight_issue = (len(formatted_repo["issues"]) / repo_issues) if repo_issues > 0 else 0
#
#             repos_to_rank.append({
#                 "full_name": formatted_repo["full_name"],
#                 "stars": np.log(repo_infos.get("stargazers_count", 0) + 1),
#                 "forks": np.log(repo_infos.get("forks_count", 0) + 1),
#                 "watches": np.log(repo_infos.get("watchers_count", 0) + 1),
#                 "subscribers": np.log(repo_infos.get("subscribers_count", 0) + 1),
#                 "issues": np.log(repo_issues + 1),
#                 "prs": np.log(repo_prs + 1),
#                 "weight": weight_pr * 0.5 + weight_issue * 0.5
#             })
#
#     user_ranks = []
#     ranked_repos = []
#     for repo in repos_to_rank:
#         rank = sum((repo.get(key, 0) - mean_final[key]) / std_final[key] * weight_final[key]
#                    for key in weight_final if key in repo)
#         user_ranks.append(rank * repo["weight"])
#         ranked_repos.append({"full_name": repo["full_name"],
#                              "repo_rank": rank,
#                              "user_prop": repo["weight"]})
#
#     user_rank_score = sum(user_ranks) / len(user_ranks) if user_ranks else 0
#
#     # 更新用户的分数和语言到数据库
#     user_collection.update_one({"username": user["username"]}, {
#         "$set": {
#             "rank_repos": ranked_repos
#         }
#     })
#
#     return user["username"], user_rank_score
#
#
# # 获取未打分的用户列表
# users = list(user_collection.find({"rank_repos": {"$exists": False}}))
# total_users = len(users)
#
# # 并发处理每个用户
# with ThreadPoolExecutor(max_workers=64) as executor:
#     futures = {executor.submit(process_user, user): user for user in users}
#
#     for future in as_completed(futures):
#         result = future.result()
#         if result:
#             username, rank_score = result
#             print(f"Updated {username} with rank {rank_score * 10000}")


# users = list(user_collection.find({"geo": {"$exists": False}}))
# for user in users:
#     github_profile_data = utils_online.user_info(user["username"], "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")
#     github_profile_data = github_profile_data.get('location')
#     if github_profile_data:
#         user_collection.update_one({"username": user["username"]}, {
#             "$set": {
#                 "location": github_profile_data
#             }
#         })
#         print(f"Updated {user['username']} with location {github_profile_data}")
#     else:
#         user_collection.update_one({"username": user["username"]}, {
#             "$set": {
#                 "location": "Not specified"
#             }
#         })
#         print(f"Updated {user['username']} with location Not specified")


# def update_user_location(user):
#     github_profile_data = utils_online.user_info(user["username"], "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")
#     location = github_profile_data.get('location') if github_profile_data.get('location') else 0
#
#     user_collection.update_one({"username": user["username"]}, {"$set": {"location": location}})
#     print(f"Updated {user['username']} with location {location}")
#
#
# # 查找没有 geo 信息的用户
# users = list(user_collection.find({"location": {"$exists": False}}))
#
# # 使用 ThreadPoolExecutor 进行并行处理
# with ThreadPoolExecutor(max_workers=32) as executor:
#     executor.map(update_user_location, users)

import pymongo

users = list(user_collection.find({"lang": {"$exists": True}}, {"lang": 1, "rank": 1, "username": 1}))
langs = {}

for user in users:
    for lang in user["lang"]:
        langs.setdefault(lang, []).append(user)

# sort by rank
for lang in langs:
    langs[lang].sort(key=lambda x: x["rank"], reverse=True)

# write user rank by language to user
updates = []
for lang in langs:
    for i, user in enumerate(langs[lang]):
        updates.append(pymongo.UpdateOne(
            {"username": user["username"]},
            {"$set": {f"rank_{lang}": i + 1}}
        ))

# Execute bulk update
if updates:
    user_collection.bulk_write(updates)

print("Rank updates completed.")
