"""Select REFUTED findings for subagent triage and write per-batch inputs.

Selection is prioritized towards findings the git history can explain:

    A. EXISTED_AND_DELETED / EXISTED_AND_RENAMED  (artifact was real, then moved)
    B. MODULE_PRESENT                             (module alive, symbol gone)
    C. PRESENT_NOW                                (predicate/internal mismatch)
    D. NEVER_EXISTED, high-authority docs only    (possible typo/rename)

Each record carries a ``doc_excerpt`` (the claim line with context) so the
reviewer does not have to locate it, plus the repo path and the staleness chain.

Usage::

    PYTHONPATH=src uv run python .../real_world/scripts/build_triage_batches.py
"""

from __future__ import annotations

import argparse
import glob
import json
import sys
from collections import Counter
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
REAL_WORLD = SCRIPTS.parent
REPOS_DIR = REAL_WORLD / "repos"
RUNS = REAL_WORLD / "runs"
INBOX = REAL_WORLD / "triage" / "inbox"

HIGH_AUTHORITY = {"README", "DIRECTIVE", "DOCS"}
EXCERPT_PAD = 6


def load_rows(run_dir: Path) -> list[dict]:
    rows: list[dict] = []
    for path in sorted(glob.glob(str(run_dir / "*" / "staleness.jsonl"))):
        repo = Path(path).parent.name
        for line in Path(path).read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            row["repo"] = row.get("repo") or repo
            row["uid"] = f"{row['repo']}::{row['finding_id']}"
            rows.append(row)
    return rows


def doc_excerpt(repo: str, source: str, line_start: int | None, line_end: int | None) -> str:
    path = REPOS_DIR / repo / source
    if not path.is_file() or not line_start:
        return ""
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    lo = max(0, line_start - 1 - EXCERPT_PAD)
    hi = min(len(lines), (line_end or line_start) + EXCERPT_PAD)
    rendered = []
    for i in range(lo, hi):
        marker = ">>" if (line_start - 1) <= i < (line_end or line_start) else "  "
        rendered.append(f"{marker} {i + 1:5d}| {lines[i]}")
    return "\n".join(rendered)


def slim(row: dict) -> dict:
    return {
        "uid": row["uid"],
        "repo": row["repo"],
        "repo_path": str(REPOS_DIR / row["repo"]),
        "predicate": row["predicate"],
        "object": row["object"],
        "source": row["primary_source"],
        "line": row["primary_line_start"],
        "doc_class": row["signals"].get("doc_class"),
        "raw_context": row["raw_context"],
        "refuting_evidence": row.get("refuting_evidence", []),
        "staleness": row["staleness"],
        "doc_excerpt": doc_excerpt(
            row["repo"], row["primary_source"], row["primary_line_start"], row["primary_line_end"]
        ),
    }


def chunk(items: list[dict], size: int) -> list[list[dict]]:
    return [items[i : i + size] for i in range(0, len(items), size)]


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default="2026-10-21")
    parser.add_argument("--size", type=int, default=24)
    args = parser.parse_args(argv)

    INBOX.mkdir(parents=True, exist_ok=True)
    for old in INBOX.glob("*.jsonl"):
        old.unlink()

    rows = load_rows(RUNS / args.date)
    by_status = Counter(r["staleness"]["status"] for r in rows)

    stale = [
        r
        for r in rows
        if r["staleness"]["status"] in {"EXISTED_AND_DELETED", "EXISTED_AND_RENAMED"}
    ]
    module = [r for r in rows if r["staleness"]["status"] == "MODULE_PRESENT"]
    present = [r for r in rows if r["staleness"]["status"] == "PRESENT_NOW"]
    never = [
        r
        for r in rows
        if r["staleness"]["status"] == "NEVER_EXISTED"
        and r["signals"].get("doc_class") in HIGH_AUTHORITY
        and r["repo"] != "dbt-core"
    ]

    batches: list[tuple[str, list[dict]]] = []

    dbt_stale = [r for r in stale if r["repo"] == "dbt-core"]
    other_stale = [r for r in stale if r["repo"] != "dbt-core"]
    for i, part in enumerate(chunk(sorted(dbt_stale, key=lambda r: r["primary_source"]), 32), 1):
        batches.append((f"dbt-stale-{i}", part))
    batches.append(
        ("stale-other", sorted(other_stale, key=lambda r: (r["repo"], r["primary_source"])))
    )
    batches.append(
        ("module-present", sorted(module, key=lambda r: (r["repo"], r["primary_source"])))
    )
    for i, part in enumerate(
        chunk(sorted(present, key=lambda r: (r["repo"], r["primary_source"])), 20), 1
    ):
        batches.append((f"present-now-{i}", part))
    for i, part in enumerate(
        chunk(sorted(never, key=lambda r: (r["repo"], r["primary_source"])), 40), 1
    ):
        batches.append((f"never-high-authority-{i}", part))

    manifest = []
    for name, items in batches:
        records = [slim(r) for r in items]
        path = INBOX / f"{name}.jsonl"
        with path.open("w", encoding="utf-8") as fh:
            for rec in records:
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        manifest.append({"batch": name, "findings": len(records), "file": str(path)})
        print(f"{name:24s} {len(records):3d} findings  {path.name}")

    (INBOX / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"\nselected {sum(m['findings'] for m in manifest)} of {len(rows)} refuted")
    print("by status:", dict(by_status))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
