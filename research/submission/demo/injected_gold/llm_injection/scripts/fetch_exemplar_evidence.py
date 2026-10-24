"""Fetch real before/after evidence for the triaged exemplar bank.

One-time **network** step, run by the harness (never by the injector). For every
human-triaged exemplar it fetches ``<commit_url>.patch``, parses the unified diff
into per-file hunks, matches the files against the alert's ``location``, and
writes an extracted-evidence JSON next to the bank. The bank builder embeds that
evidence so the injector only ever reads local files (``protocol.md`` §4.2: the
injector never sees the tool and, here, never touches the network).

Raw patches are cached under ``exemplars/cache/`` (gitignored); the extracted
evidence under ``exemplars/evidence/`` is committed and is deterministic (no
timestamps).

Run::

    PYTHONPATH=src uv run python .../llm_injection/scripts/fetch_exemplar_evidence.py
    PYTHONPATH=src uv run python .../llm_injection/scripts/fetch_exemplar_evidence.py --offline
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve()
LLM = HERE.parents[1]
EXEMPLARS = LLM / "exemplars"
BANK = EXEMPLARS / "bank.json"
CACHE = EXEMPLARS / "cache" / "patch"
EVIDENCE = EXEMPLARS / "evidence"

MAX_LINES = 60
MAX_FILES_FALLBACK = 5
_DOC_SUFFIXES = (".md", ".rst", ".mdx", ".adoc", ".txt")
_DIFF_FILE_RE = re.compile(r"^diff --git a/(?P<a>\S+) b/(?P<b>\S+)\s*$")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _side(path: str) -> str:
    return "doc" if path.endswith(_DOC_SUFFIXES) else "code"


def _sha_from_url(url: str) -> str | None:
    m = re.search(r"/commit/([0-9a-f]{7,40})/?$", url or "")
    return m.group(1) if m else None


def parse_locations(location) -> list[str]:
    """Document file paths named by a triage ``location`` field."""
    if not location:
        return []
    if isinstance(location, list):
        tokens = []
        for item in location:
            if isinstance(item, str):
                tokens.append(item)
            elif isinstance(item, (list, tuple)) and item:
                tokens.append(str(item[0]))
    else:
        tokens = re.split(r"[;]", str(location))
    out: list[str] = []
    for tok in tokens:
        tok = tok.replace("`", "").strip()
        tok = re.sub(r":[\d,\s-]+$", "", tok).strip()
        tok = re.sub(r"^\./", "", tok)
        if tok:
            out.append(tok)
    return out


def parse_patch(text: str) -> list[dict]:
    """Split a unified diff into per-file blocks with added/removed lines."""
    files: list[dict] = []
    current: dict | None = None
    for line in text.splitlines():
        m = _DIFF_FILE_RE.match(line)
        if m:
            current = {"path": m.group("b"), "removed": [], "added": [], "hunks": 0}
            files.append(current)
            continue
        if current is None:
            continue
        if line.startswith("@@"):
            current["hunks"] += 1
        elif line.startswith("+++") or line.startswith("---"):
            continue
        elif line.startswith("+"):
            current["added"].append(line[1:])
        elif line.startswith("-"):
            current["removed"].append(line[1:])
    for f in files:
        truncated = len(f["removed"]) > MAX_LINES or len(f["added"]) > MAX_LINES
        f["removed"] = f["removed"][:MAX_LINES]
        f["added"] = f["added"][:MAX_LINES]
        f["truncated"] = truncated
    return files


def match_files(files: list[dict], locations: list[str]) -> list[dict]:
    """Keep files matching the alert location; fall back to a capped diffstat."""

    def matches(path: str) -> bool:
        return any(
            path == loc or path.endswith("/" + loc) or loc.endswith("/" + path) for loc in locations
        )

    kept = [f for f in files if matches(f["path"])]
    matched = True
    if not kept:
        kept = files[:MAX_FILES_FALLBACK]
        matched = False
    out = []
    for f in kept:
        out.append(
            {
                "path": f["path"],
                "side": _side(f["path"]),
                "removed": f["removed"],
                "added": f["added"],
                "hunks": f["hunks"],
                "truncated": f["truncated"],
                "matched_location": matched,
            }
        )
    return out


def fetch_patch(url: str, dest: Path, token: str | None, timeout: int = 30) -> tuple[str, str]:
    """Return (status, text). status in {ok, http_404, http_403, error}."""
    headers = {"User-Agent": "docassay-injected-gold/1.0", "Accept": "text/plain"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310
            text = resp.read().decode("utf-8", errors="ignore")
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return "http_404", ""
        if exc.code in (403, 429):
            return "http_403", ""
        return "error", ""
    except (urllib.error.URLError, TimeoutError, OSError):
        return "error", ""
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(text, encoding="utf-8")
    return "ok", text


def _write_evidence(alert_id: str, payload: dict) -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    safe = alert_id.replace(":", "__")
    path = EVIDENCE / f"{safe}.json"
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bank", default=str(BANK))
    ap.add_argument("--pool", default="triaged", choices=("triaged", "raw", "all"))
    ap.add_argument("--sleep", type=float, default=1.0)
    ap.add_argument("--token", default="", help="GitHub token (default: $GITHUB_TOKEN)")
    ap.add_argument("--offline", action="store_true", help="use cache only; no network")
    ap.add_argument("--limit", type=int, default=0, help="max fresh fetches (0 = all)")
    args = ap.parse_args(argv)

    bank = json.loads(_read(Path(args.bank)))
    pool = args.pool
    items: list[dict] = []
    for body in bank["classes"].values():
        for e in body.get("triaged", []):
            if pool in ("triaged", "all"):
                items.append(e)
        for e in body.get("raw", []):
            if pool in ("raw", "all"):
                items.append(e)

    token = args.token or None
    import os

    token = token or os.environ.get("GITHUB_TOKEN") or None

    fetched = 0
    counts: dict[str, int] = {}
    stop = False
    for e in items:
        alert_id = e["id"]
        url = e.get("commit_url")
        sha = _sha_from_url(url)
        if not url or not sha:
            _write_evidence(alert_id, {"alert_id": alert_id, "status": "no_commit_url"})
            counts["no_commit_url"] = counts.get("no_commit_url", 0) + 1
            continue
        cache = CACHE / f"{sha}.patch"
        if cache.is_file():
            status, text = "ok", _read(cache)
        elif args.offline:
            status, text = "offline_missing", ""
        elif stop:
            status, text = "skipped_ratelimit", ""
        elif args.limit and fetched >= args.limit:
            status, text = "skipped_limit", ""
        else:
            status, text = fetch_patch(url.rstrip("/") + ".patch", cache, token)
            fetched += 1
            if status == "ok":
                time.sleep(args.sleep)
            elif status == "http_403":
                stop = True

        counts[status] = counts.get(status, 0) + 1
        locations = parse_locations(e.get("location"))
        if status != "ok":
            _write_evidence(
                alert_id,
                {
                    "alert_id": alert_id,
                    "commit_url": url,
                    "status": status,
                    "locations": locations,
                    "files": [],
                },
            )
            continue
        files = match_files(parse_patch(text), locations)
        _write_evidence(
            alert_id,
            {
                "alert_id": alert_id,
                "commit_url": url,
                "commit_sha": sha,
                "patch_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                "status": "ok",
                "locations": locations,
                "files": files,
            },
        )

    print(f"exemplars={len(items)} fetched={fetched} status={counts}")
    if stop:
        print("  WARNING: rate limit hit; partial result. Re-run to resume from cache.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
