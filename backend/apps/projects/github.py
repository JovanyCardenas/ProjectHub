import re
import requests


def parse_github_repo_url(url):
    """
    Converts:
    https://github.com/owner/repo
    https://github.com/owner/repo/
    https://github.com/owner/repo.git

    Into:
    ("owner", "repo")
    """
    if not url:
        return None, None

    pattern = r"github\.com[:/](?P<owner>[^/]+)/(?P<repo>[^/.]+)"
    match = re.search(pattern, url)

    if not match:
        return None, None

    return match.group("owner"), match.group("repo").replace(".git", "")


def fetch_repo_issues(owner, repo, token=None):
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"

    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    if token:
        headers["Authorization"] = f"Bearer {token}"

    response = requests.get(
        url,
        headers=headers,
        params={
            "state": "all",
            "per_page": 100,
        },
        timeout=15,
    )

    response.raise_for_status()

    issues = response.json()

    # GitHub returns PRs in the issues endpoint too, so remove PRs.
    return [issue for issue in issues if "pull_request" not in issue]