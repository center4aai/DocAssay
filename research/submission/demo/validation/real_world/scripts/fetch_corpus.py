"""Fetch (or refresh) the real-world corpus at today's HEAD and pin it.

The corpus is a set of well-known Python projects whose documentation lives in
the repository and describes the repository itself. Every clone keeps full
commit/tree history but filters blobs (``--filter=blob:none``): the staleness
attributor needs history and trees, not old file contents.

Usage::

    PYTHONPATH=src uv run python .../real_world/scripts/fetch_corpus.py
    PYTHONPATH=src uv run python .../real_world/scripts/fetch_corpus.py --only fastapi,flask
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
REAL_WORLD = SCRIPTS.parent
REPO_ROOT = REAL_WORLD.parents[3]  # repository root
REPOS_DIR = REAL_WORLD / "repos"
LOCK = REAL_WORLD / "corpus.lock.json"

# name -> upstream URL. All Python, all with in-repo documentation.
CORPUS: dict[str, str] = {
    "fastapi": "https://github.com/fastapi/fastapi",
    "flask": "https://github.com/pallets/flask",
    "click": "https://github.com/pallets/click",
    "celery": "https://github.com/celery/celery",
    "sqlfluff": "https://github.com/sqlfluff/sqlfluff",
    "dbt-core": "https://github.com/dbt-labs/dbt-core",
    "pydantic": "https://github.com/pydantic/pydantic",
    "httpx": "https://github.com/encode/httpx",
    "aiohttp": "https://github.com/aio-libs/aiohttp",
    "pip": "https://github.com/pypa/pip",
    "black": "https://github.com/psf/black",
    "pytest": "https://github.com/pytest-dev/pytest",
    "mkdocs": "https://github.com/mkdocs/mkdocs",
    "ruff": "https://github.com/astral-sh/ruff",
    "poetry": "https://github.com/python-poetry/poetry",
    "sqlalchemy": "https://github.com/sqlalchemy/sqlalchemy",
}


def git(*args: str, cwd: Path | None = None) -> str:
    proc = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {proc.stderr.strip()}")
    return proc.stdout.strip()


def fetch_one(name: str, url: str, jobs_note: str = "") -> dict:
    dest = REPOS_DIR / name
    if dest.exists():
        git("fetch", "--filter=blob:none", "--prune", "origin", cwd=dest)
        branch = git("rev-parse", "--abbrev-ref", "HEAD", cwd=dest)
        git("reset", "--hard", f"origin/{branch}", cwd=dest)
        action = "fetched"
    else:
        # Single-branch clone with lazy blobs: history + trees are local, file
        # contents are fetched on demand.
        git(
            "clone",
            "--filter=blob:none",
            "--single-branch",
            url,
            str(dest),
            cwd=REPOS_DIR,
        )
        action = "cloned"
    record = {
        "repo": name,
        "url": url,
        "action": action,
        "branch": git("rev-parse", "--abbrev-ref", "HEAD", cwd=dest),
        "sha": git("rev-parse", "HEAD", cwd=dest),
        "commit_date": git("log", "-1", "--date=iso-strict", "--format=%cd", cwd=dest),
        "subject": git("log", "-1", "--format=%s", cwd=dest),
        "nearest_tag": _nearest_tag(dest),
        "tool_commit": tool_commit(),
    }
    return record


def _nearest_tag(dest: Path) -> str | None:
    try:
        return git("describe", "--tags", "--abbrev=0", cwd=dest)
    except RuntimeError:
        return None


def tool_commit() -> str:
    try:
        sha = git("rev-parse", "--short", "HEAD", cwd=REPO_ROOT)
        dirty = git("status", "--porcelain", cwd=REPO_ROOT)
        return sha + ("+dirty" if dirty else "")
    except RuntimeError:
        return "unknown"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", default="", help="comma-separated repo names")
    parser.add_argument("--jobs", type=int, default=4)
    args = parser.parse_args(argv)

    wanted = [n.strip() for n in args.only.split(",") if n.strip()] or list(CORPUS)
    unknown = [n for n in wanted if n not in CORPUS]
    if unknown:
        print(f"unknown repo(s): {', '.join(unknown)}", file=sys.stderr)
        return 2

    REPOS_DIR.mkdir(parents=True, exist_ok=True)

    records: dict[str, dict] = {}
    failures: dict[str, str] = {}
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futures = {pool.submit(fetch_one, n, CORPUS[n]): n for n in wanted}
        for fut in as_completed(futures):
            name = futures[fut]
            try:
                rec = fut.result()
            except Exception as exc:  # noqa: BLE001 - report, do not abort
                failures[name] = str(exc)
                print(f"FAIL {name}: {exc}", file=sys.stderr)
                continue
            records[name] = rec
            print(f"{rec['action']:8s} {name:12s} {rec['sha'][:12]} {rec['commit_date']}")

    lock = {
        "schema": "docassay-real-world-corpus/1",
        "fetched_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "pin": "default-branch HEAD at fetch time (full history, blob-filtered clone)",
        "tool_commit": tool_commit(),
        "repositories": [records[n] for n in CORPUS if n in records],
        "failures": failures,
    }
    LOCK.write_text(json.dumps(lock, indent=2) + "\n", encoding="utf-8")
    print(f"\nwrote {LOCK} ({len(records)} repos, {len(failures)} failures)")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
