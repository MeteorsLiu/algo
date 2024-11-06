import utils
import utils_online

from concurrent.futures import ThreadPoolExecutor, as_completed

test_mean = {
    "stars": 1.132366,
    "forks": 0.451522,
    "watchers": 1.199872,
    "used_by": 0.101942,
    "contributors": 1.192904,
    "commit_rate": 0.159262,
    "issue_rate": 0.000105
}

test_std = {
    "stars": 0.990616,
    "forks": 0.844213,
    "watchers": 0.571998,
    "used_by": 0.684791,
    "contributors": 1.407939,
    "commit_rate": 0.460403,
    "issue_rate": 0.002566
}

test_weight = {
    "stars": 0.229479,
    "forks": 0.227530,
    "watchers": 0.104085,
    "used_by": 0.102685,
    "contributors": 0.913740,
    "issue_rate": 0.198170,
    "commit_rate": 0.000304
}


def repo_rank(full_name: str, token: str, weight: dict, mean: dict, std: dict):
    repo_stats = utils_online.repo_stats(full_name, token)
    if repo_stats is None:
        return None

    rank = 0
    for key in repo_stats:
        repo_stats[key] = utils.z_score(repo_stats[key], mean[key], std[key])
        rank += repo_stats[key] * weight[key]

    return rank


def user_rank(username: str, token: str, concurrency: int = 32):
    own_repos = utils_online.user_repos(username)
    rank = {}

    def fetch_repo_rank(repo):
        return repo_rank(repo, token, test_weight, test_mean, test_std)

    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = {executor.submit(fetch_repo_rank, own_repo): own_repo for own_repo in own_repos}
        for future in as_completed(futures):
            if future.exception() or future.result() is None:
                continue

            rank[futures[future]] = future.result()

    rank_sum = sum(rank.values())
    rank_avg = rank_sum / len(rank) if rank else 0

    return rank_avg
