"""Fetch raw Markdown from a GitHub repository URL or a local file."""

from __future__ import annotations

import re
from pathlib import Path

import httpx

# Matches:  https://github.com/{owner}/{repo}  (optional /tree/{branch} etc.)
_GITHUB_RE = re.compile(
    r"https?://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+)"
    r"(?:/tree/(?P<branch>[^/]+))?",
    re.IGNORECASE,
)

_RAW_BASE = "https://raw.githubusercontent.com"
_DEFAULT_BRANCHES = ("main", "master", "trunk", "blob/main", "blob/master")
_README_NAMES = ("README.md", "readme.md", "README.MD", "Readme.md")


def _raw_url(owner: str, repo: str, branch: str, filename: str) -> str:
    return f"{_RAW_BASE}/{owner}/{repo}/{branch}/{filename}"


def fetch_markdown(source: str) -> tuple[str, str]:
    """
    Return (markdown_text, display_name).

    *source* can be:
      - a local file path  (e.g. ``README.md``, ``./docs/index.md``)
      - a GitHub repo URL  (e.g. ``https://github.com/user/repo``)
    """
    m = _GITHUB_RE.match(source)
    if m:
        return _fetch_github(m.group("owner"), m.group("repo"), m.group("branch"))

    path = Path(source)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {source}")
    return path.read_text(encoding="utf-8"), path.name


def _fetch_github(owner: str, repo: str, branch: str | None) -> tuple[str, str]:
    """Try known branch names and README filenames until one 200s."""
    branches = [branch] if branch else list(_DEFAULT_BRANCHES)
    tried: list[str] = []

    with httpx.Client(follow_redirects=True, timeout=15) as client:
        for b in branches:
            for name in _README_NAMES:
                url = _raw_url(owner, repo, b, name)
                tried.append(url)
                resp = client.get(url)
                if resp.status_code == 200:
                    return resp.text, f"{owner}/{repo} — {name}"

    raise ValueError(
        f"Could not find a README in {owner}/{repo}.\n"
        f"Tried:\n" + "\n".join(f"  {u}" for u in tried)
    )
