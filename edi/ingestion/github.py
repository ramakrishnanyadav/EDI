"""
github.py — GitHub data fetcher.

Fetches Issues, PRs, and Discussions from target repositories.
Respects rate limits. Returns normalized thread dicts ready for extraction.
"""
from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Iterator

from github import Github, GithubException, RateLimitExceededException

logger = logging.getLogger(__name__)

DEFAULT_REPOS = [
    "topoteretes/cognee",
    "langchain-ai/langchain",
    "run-llama/llama_index",
]

@dataclass(frozen=True, slots=True)
class GitHubThread:
    id: str           # unique: "owner/repo#number/type"
    repo: str
    repo_url: str
    number: int
    title: str
    body: str
    url: str
    thread_type: str  # "issue" | "pr" | "discussion"
    created_at: datetime
    labels: list[str]
    comments_text: str
    stars: int
    forks: int
    contributors_count: int

    def full_text(self) -> str:
        parts = [f"Title: {self.title}", f"Body: {self.body or '(empty)'}"]
        if self.comments_text:
            parts.append(f"Discussion:\n{self.comments_text}")
        return "\n\n".join(parts)[:6000]

def _safe_body(text: str | None) -> str:
    return (text or "").strip()[:3000]

def _fetch_comments(item, max_comments: int = 8) -> str:
    try:
        comments = list(item.get_comments())[:max_comments]
        return "\n---\n".join(
            f"@{c.user.login}: {_safe_body(c.body)}"
            for c in comments if c.body
        )
    except GithubException:
        return ""

def _repo_meta(repo) -> dict:
    try:
        contributors = repo.get_contributors()
        count = sum(1 for _ in contributors)
    except GithubException:
        count = 0
    return {
        "stars": repo.stargazers_count,
        "forks": repo.forks_count,
        "contributors_count": min(count, 500),
    }

def fetch_threads(
    repo_names: list[str] | None = None,
    max_per_repo: int = 70,
    token: str | None = None,
) -> list[GitHubThread]:
    token = token or os.getenv("GITHUB_TOKEN")
    if not token or token == "your_github_token":
        raise ValueError(
            "GITHUB_TOKEN not set. Add your token to .env — "
            "get one free at https://github.com/settings/tokens"
        )

    g = Github(token, per_page=100, retry=3)
    repos = repo_names or DEFAULT_REPOS
    threads: list[GitHubThread] = []

    for repo_name in repos:
        logger.info("Fetching from %s ...", repo_name)
        try:
            repo = g.get_repo(repo_name)
            meta = _repo_meta(repo)

            for issue in _paginate(repo.get_issues(state="closed", sort="comments"), max_per_repo // 2):
                if issue.pull_request:
                    continue
                thread = GitHubThread(
                    id=f"{repo_name}#{issue.number}/issue",
                    repo=repo_name,
                    repo_url=f"https://github.com/{repo_name}",
                    number=issue.number,
                    title=issue.title,
                    body=_safe_body(issue.body),
                    url=issue.html_url,
                    thread_type="issue",
                    created_at=issue.created_at,
                    labels=[l.name for l in issue.labels],
                    comments_text=_fetch_comments(issue),
                    **meta,
                )
                threads.append(thread)

            for pr in _paginate(repo.get_pulls(state="closed", sort="updated", direction="desc"), max_per_repo // 2):
                if not pr.merged:
                    continue
                thread = GitHubThread(
                    id=f"{repo_name}#{pr.number}/pr",
                    repo=repo_name,
                    repo_url=f"https://github.com/{repo_name}",
                    number=pr.number,
                    title=pr.title,
                    body=_safe_body(pr.body),
                    url=pr.html_url,
                    thread_type="pr",
                    created_at=pr.created_at,
                    labels=[l.name for l in pr.labels],
                    comments_text=_fetch_comments(pr),
                    **meta,
                )
                threads.append(thread)

            logger.info("  → fetched %d threads from %s", len([t for t in threads if t.repo == repo_name]), repo_name)

        except RateLimitExceededException:
            reset = g.rate_limiting_resettime
            wait = max(0, reset - int(time.time())) + 5
            logger.warning("Rate limit hit. Sleeping %ds ...", wait)
            time.sleep(wait)
        except GithubException as exc:
            logger.error("GitHub error for %s: %s", repo_name, exc)

    logger.info("Total threads fetched: %d", len(threads))
    return threads

def _paginate(query, limit: int) -> Iterator:
    count = 0
    for item in query:
        if count >= limit:
            break
        yield item
        count += 1
