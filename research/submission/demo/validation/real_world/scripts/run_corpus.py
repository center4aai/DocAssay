"""Run the verifier over the real-world corpus and store per-repo artifacts.

One analysis per repository; writes:

    runs/<date>/<repo>/claims.jsonl    every claim with verdict + evidence
    runs/<date>/<repo>/findings.jsonl  triage items (all verdicts, REFUTED ranked)
    runs/<date>/<repo>/report.md       human-readable triage report
    runs/<date>/<repo>/summary.json    counts + timings

Usage::

    PYTHONPATH=src uv run python .../real_world/scripts/run_corpus.py
    PYTHONPATH=src uv run python .../real_world/scripts/run_corpus.py --only celery,pip
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter
from datetime import date
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
REAL_WORLD = SCRIPTS.parent
REPO_ROOT = REAL_WORLD.parents[3]
REPOS_DIR = REAL_WORLD / "repos"
RUNS = REAL_WORLD / "runs"

from docassay.core.dump_claims import _record  # noqa: E402
from docassay.core.pipeline import analyze_repository, exclusion_progress  # noqa: E402
from docassay.triage.findings import collect_findings  # noqa: E402
from docassay.triage.report import render_report, write_findings  # noqa: E402


def _per_predicate_table(items) -> dict[str, dict]:
    """Resolved counts per predicate for the per-repository summary."""
    table: dict[str, dict[str, int]] = {}
    for item in items:
        row = table.setdefault(item.predicate, {"SUPPORTED": 0, "REFUTED": 0, "NEI": 0})
        row[item.verdict or "NEI"] += 1
    return table


def run_one(name: str, run_dir: Path) -> dict:
    repo = REPOS_DIR / name
    out = run_dir / name
    out.mkdir(parents=True, exist_ok=True)

    started = time.monotonic()
    result = analyze_repository(repo, progress=exclusion_progress)
    elapsed = time.monotonic() - started

    evidence_by_id = {e.evidence_id: e for e in result.evidence}
    with (out / "claims.jsonl").open("w", encoding="utf-8", newline="") as fh:
        for referent in result.referents:
            for assertion in referent.assertions:
                for claim in assertion.claims:
                    fh.write(
                        json.dumps(_record(claim, assertion, evidence_by_id), ensure_ascii=False)
                        + "\n"
                    )

    items = collect_findings(result, name)
    write_findings(items, out / "findings.jsonl")
    (out / "report.md").write_text(
        render_report(result, name, top_k=1000, sample_per_stratum=5), encoding="utf-8"
    )

    verdicts = Counter(i.verdict for i in items)
    per_pred = _per_predicate_table(items)
    summary = {
        "repo": name,
        "docs": result.scanned_documents,
        "claims": len(result.claims),
        "referents": len(result.referents),
        "evidence": len(result.evidence),
        "verdicts": dict(verdicts),
        "refuted_by_predicate": {
            p: row["REFUTED"] for p, row in per_pred.items() if row["REFUTED"]
        },
        "seconds": round(elapsed, 1),
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def aggregate_rows(run_dir: Path) -> str:
    rows = []
    for path in sorted(run_dir.glob("*/summary.json")):
        rows.append(json.loads(path.read_text(encoding="utf-8")))
    rows.sort(key=lambda r: -r["verdicts"].get("REFUTED", 0))

    lines = [
        "| repo | docs | claims | resolved | coverage | REFUTED | top predicates | s |",
        "|---|---:|---:|---:|---:|---:|---|---:|",
    ]
    total_refuted = 0
    for r in rows:
        v = r["verdicts"]
        resolved = v.get("SUPPORTED", 0) + v.get("REFUTED", 0)
        coverage = resolved / max(sum(v.values()), 1)
        total_refuted += v.get("REFUTED", 0)
        top = sorted(r["refuted_by_predicate"].items(), key=lambda kv: -kv[1])
        top_s = ", ".join(f"{p} {n}" for p, n in top[:3]) or "—"
        lines.append(
            f"| {r['repo']} | {r['docs']} | {r['claims']} | {resolved} | {coverage:.2f} "
            f"| {v.get('REFUTED', 0)} | {top_s} | {r['seconds']:.0f} |"
        )
    lines.append(
        f"| **total** |  |  |  |  | **{total_refuted}** |  |  |"
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", default="")
    parser.add_argument("--date", default=date.today().isoformat())
    args = parser.parse_args(argv)

    run_dir = RUNS / args.date
    run_dir.mkdir(parents=True, exist_ok=True)
    names = [n.strip() for n in args.only.split(",") if n.strip()]
    if not names:
        names = sorted(p.name for p in REPOS_DIR.iterdir() if p.is_dir())

    for i, name in enumerate(names, 1):
        print(f"[{i}/{len(names)}] {name} ...", flush=True)
        try:
            summary = run_one(name, run_dir)
        except Exception as exc:  # noqa: BLE001 - keep the batch going
            print(f"  FAILED {name}: {exc}", file=sys.stderr)
            continue
        v = summary["verdicts"]
        print(
            f"  docs={summary['docs']} claims={summary['claims']} "
            f"refuted={v.get('REFUTED', 0)} supported={v.get('SUPPORTED', 0)} "
            f"nei={v.get('NEI', 0)} in {summary['seconds']:.0f}s",
            flush=True,
        )

    table = aggregate_rows(run_dir)
    (run_dir / "aggregate.md").write_text(table, encoding="utf-8")
    print("\n" + table)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
