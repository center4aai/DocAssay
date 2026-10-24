"""Merge judge-agent verdicts and compare them with the deterministic scorer.

Reads ``<judge_dir>/batch_*.json`` (built by ``judge_batches.py``) and the
verdict files the judge agents wrote (``<judge_dir>/verdicts_*.json``), reports
per-class judge recall and the agreement with the deterministic MPChecker
scorer.

Run::

    PYTHONPATH=src uv run python .../scripts/judge_apply.py \
        --manifest .../runs/<run>/manifest.jsonl --claims .../runs/<run>/claims \
        --judge-dir .../runs/<run>/judge --out .../runs/<run>
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
import score_injections as S  # noqa: E402

DETECTED_REACTIONS = {"refuted"}


def load_verdicts(judge_dir: Path) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for path in sorted(judge_dir.glob("verdicts_*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        for v in data.get("verdicts", []):
            out[v["id"]] = v
    return out


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--claims", required=True)
    ap.add_argument("--judge-dir", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    manifest = [
        json.loads(line)
        for line in Path(args.manifest).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    claims_dir = Path(args.claims)
    repos = sorted({e["repo"] for e in manifest})
    claims_by = {}
    for repo in repos:
        for snap in ("baseline", "injected"):
            claims_by[(repo, snap)] = S.load_claims(claims_dir / f"{repo}__{snap}.jsonl")

    judge_dir = Path(args.judge_dir)
    verdicts = load_verdicts(judge_dir)

    by_class: dict[str, dict] = defaultdict(
        lambda: {"refuted_injected": 0, "refuted_detected": 0, "controls": 0, "controls_clean": 0}
    )
    agree = 0
    total = 0
    missing = 0
    reactions = defaultdict(int)

    # Batch ids are assigned per repo in manifest order (see judge_batches).
    id_to_entry: dict[str, dict] = {}
    for repo in repos:
        entries = [e for e in manifest if e["repo"] == repo]
        for i, e in enumerate(entries):
            id_to_entry[f"{repo}::{i}"] = e

    for item_id, e in id_to_entry.items():
        v = verdicts.get(item_id)
        if v is None:
            missing += 1
            continue
        repo = e["repo"]
        reaction = v.get("reaction", "none")
        reactions[reaction] += 1
        is_control = e.get("control", "none") != "none"
        judge_detected = reaction in DETECTED_REACTIONS
        det = S.classify(
            e,
            claims_by.get((repo, "injected"), []),
            claims_by.get((repo, "baseline"), []),
        )
        total += 1
        agree += int(judge_detected == det["detected"])
        row = by_class[e["canonical_class"]]
        if is_control:
            row["controls"] += 1
            row["controls_clean"] += 0 if judge_detected else 1
        elif e.get("expected_verdict") == "refuted":
            row["refuted_injected"] += 1
            row["refuted_detected"] += int(judge_detected)

    out = {
        "judged": total,
        "missing_verdicts": missing,
        "agreement_with_deterministic": round(agree / total, 3) if total else None,
        "reactions": dict(sorted(reactions.items())),
        "by_class": {
            cls: {
                **row,
                "recall": round(row["refuted_detected"] / row["refuted_injected"], 3)
                if row["refuted_injected"]
                else None,
                "precision": round(row["controls_clean"] / row["controls"], 3)
                if row["controls"]
                else None,
            }
            for cls, row in sorted(by_class.items())
        },
    }
    Path(args.out).joinpath("judge", "summary.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
