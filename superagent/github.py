import httpx
from .config import get_settings


class GitHubError(RuntimeError):
    pass


def _headers() -> dict[str, str]:
    settings = get_settings()
    headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    if settings.github_token:
        headers["Authorization"] = f"Bearer {settings.github_token}"
    return headers


async def _get(path: str):
    settings = get_settings()
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(settings.github_api_url.rstrip("/") + path, headers=_headers())
    if response.is_error:
        raise GitHubError(f"GitHub API returned HTTP {response.status_code}: {response.text[:400]}")
    return response.json()


async def audit_repository(full_name: str) -> dict:
    repo = await _get(f"/repos/{full_name}")
    pulls = await _get(f"/repos/{full_name}/pulls?state=open&per_page=100")
    branches = await _get(f"/repos/{full_name}/branches?per_page=100")
    return {
        "repository": full_name,
        "default_branch": repo.get("default_branch"),
        "private": repo.get("private"),
        "archived": repo.get("archived"),
        "open_pull_requests": [
            {"number": p["number"], "title": p["title"], "draft": p.get("draft", False),
             "head": p["head"]["ref"], "base": p["base"]["ref"], "url": p["html_url"]}
            for p in pulls
        ],
        "branches": [b["name"] for b in branches],
        "updated_at": repo.get("updated_at"),
        "html_url": repo.get("html_url"),
    }


def assert_write_allowed(full_name: str) -> None:
    settings = get_settings()
    if not settings.github_write_enabled:
        raise GitHubError("GitHub writes are disabled. Set GITHUB_WRITE_ENABLED=true after reviewing permissions.")
    if full_name.lower() not in settings.allowed_repositories:
        raise GitHubError(f"Repository is not in GITHUB_ALLOWED_REPOS: {full_name}")
    if not settings.github_token:
        raise GitHubError("GITHUB_TOKEN is required for repository writes.")
