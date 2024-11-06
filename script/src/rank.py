import utils
import utils_online

from concurrent.futures import ThreadPoolExecutor, as_completed

test_mean = {
    "stars": 0.004543,
    "forks": 0.001678,
    "watchers": 0.002349,
    "used_by": 0.093500,
    "contributors": 1.159181,
    "commit_rate": 0.140307,
    "issue_rate": 0.000549
}

test_std = {
    "stars": 0.037582,
    "forks": 0.017535,
    "watchers": 0.004528,
    "used_by": 0.670376,
    "contributors": 1.322982,
    "commit_rate": 0.441339,
    "issue_rate": 0.004910
}

test_weight = {
    "stars": 0.45767391,
    "forks": 0.36005329,
    "watchers": 0.08024534,
    "used_by": 0.04689893,
    "contributors": 0.03328084,
    "commit_rate": 0.02184671,
    "issue_rate": 0.00000097
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
