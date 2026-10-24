"""Merge subagent triage verdicts with the findings and report precision.

Reads ``triage/inbox/*.jsonl`` (inputs) and ``triage/out/*.jsonl`` (verdicts),
joins on ``uid``, and writes:

    triage/merged.jsonl      finding + verdict, one line per reviewed item
    triage/summary.json      label counts overall / by staleness status / by predicate
    triage/confirmed.md      every REAL_DRIFT record, grouped by repo

Usage::

    PYTHONPATH=src uv run python .../real_world/scripts/merge_triage.py
"""

from __future__ import annotations

import glob
import json
from collections import Counter, defaultdict
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
REAL_WORLD = SCRIPTS.parent
TRIAGE = REAL_WORLD / "triage"
LABELS = [
    "REAL_DRIFT",
    "GENRE_EXAMPLE",
    "GENERATED_ARTIFACT",
    "PREDICATE_FP",
    "HISTORICAL",
    "AMBIGUOUS",
]


def read_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def main() -> int:
    inputs: dict[str, dict] = {}
    for path in sorted(glob.glob(str(TRIAGE / "inbox" / "*.jsonl"))):
        for rec in read_jsonl(Path(path)):
            inputs[rec["uid"]] = rec

    verdicts: dict[str, dict] = {}
    dupes: list[str] = []
    for path in sorted(glob.glob(str(TRIAGE / "out" / "*.jsonl"))):
        for rec in read_jsonl(Path(path)):
            if rec["uid"] in verdicts:
                dupes.append(rec["uid"])
            verdicts[rec["uid"]] = rec

    missing = sorted(set(inputs) - set(verdicts))
    extra = sorted(set(verdicts) - set(inputs))

    merged = []
    for uid in sorted(inputs):
        if uid not in verdicts:
            continue
        merged.append({**inputs[uid], **verdicts[uid]})
    (TRIAGE / "merged.jsonl").write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in merged) + "\n", encoding="utf-8"
    )

    by_label = Counter(r["label"] for r in merged)
    by_status: dict[str, Counter] = defaultdict(Counter)
    by_predicate: dict[str, Counter] = defaultdict(Counter)
    for r in merged:
        by_status[r["staleness"]["status"]][r["label"]] += 1
        by_predicate[r["predicate"]][r["label"]] += 1

    summary = {
        "reviewed": len(merged),
        "labels": dict(by_label),
        "real_drift_share": round(by_label["REAL_DRIFT"] / max(len(merged), 1), 3),
        "by_status": {k: dict(v) for k, v in by_status.items()},
        "by_predicate": {k: dict(v) for k, v in by_predicate.items()},
        "missing": missing,
        "extra": extra,
        "duplicates": sorted(set(dupes)),
    }
    (TRIAGE / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    print(f"reviewed {len(merged)} findings  (missing {len(missing)}, extra {len(extra)})")
    for label in LABELS:
        print(f"  {label:18s} {by_label[label]:4d}")
    print("\nby staleness status:")
    for status in sorted(by_status):
        row = by_status[status]
        print(f"  {status:20s} {dict(sorted(row.items()))}")
    print("\nby predicate:")
    for pred in sorted(by_predicate):
        row = by_predicate[pred]
        print(f"  {pred:14s} {dict(sorted(row.items()))}")

    confirmed = [r for r in merged if r["label"] == "REAL_DRIFT"]
    confirmed.sort(key=lambda r: (-r.get("confidence", 0), r["repo"], r["source"]))
    lines = ["# Confirmed documentation drift (REAL_DRIFT)\n"]
    by_repo: dict[str, list[dict]] = defaultdict(list)
    for r in confirmed:
        by_repo[r["repo"]].append(r)
    for repo in sorted(by_repo):
        lines.append(f"## {repo}\n")
        for r in by_repo[repo]:
            s = r["staleness"]
            lines.append(
                f"- **{r['predicate']}** `{r['object']}` — {r['source']}:{r['line']} "
                f"(conf {r.get('confidence')}, class {r.get('doc_class')})  \n"
                f"  {r.get('reason', '')}  \n"
                f"  evidence: {r.get('evidence', '')}  \n"
                f"  history: {s.get('removed_date', '')[:10]} "
                f"{s.get('removed_subject', '')} {s.get('renamed_to') or ''}"
            )
        lines.append("")
    (TRIAGE / "confirmed.md").write_text("\n".join(lines), encoding="utf-8")

    write_aggregate(merged)
    out = TRIAGE / "merged.jsonl"
    print(f"\nwrote {out}, summary.json, confirmed.md ({len(confirmed)} confirmed)")
    return 0


def write_aggregate(merged: list[dict]) -> None:
    """Per-repo table: corpus size, REFUTED, reviewed, confirmed real."""
    run_dirs = sorted(p for p in (REAL_WORLD / "runs").iterdir() if p.is_dir())
    if not run_dirs:
        return
    run_dir = run_dirs[-1]
    per_repo: dict[str, dict] = {}
    for path in sorted(run_dir.glob("*/summary.json")):
        rec = json.loads(path.read_text(encoding="utf-8"))
        per_repo[rec["repo"]] = {
            "docs": rec["docs"],
            "claims": rec["claims"],
            "refuted": rec["verdicts"].get("REFUTED", 0),
            "seconds": rec["seconds"],
        }
    reviewed = Counter(r["repo"] for r in merged)
    real = Counter(r["repo"] for r in merged if r["label"] == "REAL_DRIFT")
    rows = sorted(per_repo, key=lambda n: (-real[n], -per_repo[n]["refuted"]))
    lines = [
        f"# Corpus aggregate — {run_dir.name}\n",
        "| repo | docs | claims | REFUTED | reviewed | REAL_DRIFT | s |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for name in rows:
        r = per_repo[name]
        lines.append(
            f"| {name} | {r['docs']} | {r['claims']} | {r['refuted']} "
            f"| {reviewed[name]} | {real[name]} | {r['seconds']:.0f} |"
        )
    lines.append(
        f"| **total** | {sum(r['docs'] for r in per_repo.values())} "
        f"| {sum(r['claims'] for r in per_repo.values())} "
        f"| {sum(r['refuted'] for r in per_repo.values())} "
        f"| {sum(reviewed.values())} | {sum(real.values())} | "
        f"{sum(r['seconds'] for r in per_repo.values()):.0f} |"
    )
    (TRIAGE / "aggregate.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nwrote {TRIAGE / 'aggregate.md'}")


if __name__ == "__main__":
    raise SystemExit(main())
