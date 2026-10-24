"""Deterministic diff-based judge: did the tool react to the injection, and how?

This is our own adjudicator — no LLM. It looks only at the tool's
baseline->injected finding diff (never at the injection's line) and decides, per
injected artifact, how the tool reacted:

- ``refuted``      — a *new* finding whose object names the injected artifact;
- ``nei``          — a *new* finding about the artifact that abstained;
- ``none``         — no new finding concerns the artifact.

Matching is symbol/path-aware and considers both the stale artifact (``old``)
and the mutated value (``new``), so ``doc_side`` mutations are judged too. The
whole-repo diff is computed once, then each injection is matched against the
small set of new findings.

Writes ``<judge_dir>/deterministic_verdicts.json`` in the same shape as the LLM
judge's verdicts and, when those exist, the head-to-head agreement.

Run::

    PYTHONPATH=src uv run python .../scripts/judge_diff.py \
        --manifest .../runs/<run>/manifest.jsonl --claims .../runs/<run>/claims \
        --judge-dir .../runs/<run>/judge
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


def _artifacts(entry: dict) -> list[str]:
    out = []
    for key in ("old", "new", "target", "symbol"):
        value = entry.get(key)
        if value:
            out.append(str(value))
    return out


def _match(candidate: dict, artifacts: list[str]) -> tuple[str | None, bool]:
    """Whether a finding object names any artifact; return (artifact, strong)."""
    obj = candidate.get("object", "")
    last = obj.lower().rsplit("/", 1)[-1]
    for art in artifacts:
        if S.obj_match(obj, art):
            strong = last == art.lower().rsplit("/", 1)[-1]
            return art, strong
    return None, False


def _repo_diff(claims_by: dict, repo: str) -> dict:
    """Precompute the new findings of one repo (injected vs baseline)."""
    base = claims_by.get((repo, "baseline"), [])
    inj = claims_by.get((repo, "injected"), [])

    def new_of(verdict: str) -> list[dict]:
        keys = S._keys(base, verdict)
        return [c for c in inj if c.get("code_verdict") == verdict and S._claim_key(c) not in keys]

    return {
        "new_refuted": new_of("REFUTED"),
        "new_nei": new_of("NEI"),
        "base_refuted": [c for c in base if c.get("code_verdict") == "REFUTED"],
    }


def judge(entry: dict, diff: dict) -> dict:
    """Deterministic reaction for one entry, from the precomputed diff."""
    artifacts = _artifacts(entry)
    if entry.get("control", "none") != "none":
        bad = [
            c
            for c in diff["base_refuted"]
            if any(S.obj_match(c.get("object", ""), a) for a in artifacts)
        ]
        return {
            "reaction": "refuted" if bad else "clean",
            "matched": [f"{c.get('source')}:{c.get('line_start')} {c.get('object')}" for c in bad],
            "rule": "control",
        }

    for key, reaction in (("new_refuted", "refuted"), ("new_nei", "nei")):
        for c in diff[key]:
            art, strong = _match(c, artifacts)
            if art is not None:
                where = f"{c.get('source')}:{c.get('line_start')}"
                return {
                    "reaction": reaction,
                    "matched": [f"{where} {c.get('predicate')} {c.get('object')}"],
                    "rule": f"new_{reaction}{'_strong' if strong else ''}",
                }
    return {"reaction": "none", "matched": [], "rule": "no_new_finding"}


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--claims", required=True)
    ap.add_argument("--judge-dir", required=True)
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
    diffs = {repo: _repo_diff(claims_by, repo) for repo in repos}

    verdicts = []
    by_class: dict[str, dict] = defaultdict(
        lambda: {"refuted_injected": 0, "refuted_detected": 0, "controls": 0, "controls_clean": 0}
    )
    reactions: dict[str, int] = defaultdict(int)
    idx_by_repo: dict[str, int] = defaultdict(int)
    entry_by_id: dict[str, dict] = {}
    for e in manifest:
        repo = e["repo"]
        v = judge(e, diffs[repo])
        item_id = f"{repo}::{idx_by_repo[repo]}"
        idx_by_repo[repo] += 1
        entry_by_id[item_id] = e
        verdicts.append(
            {"id": item_id, "reaction": v["reaction"], "matched": v["matched"], "rule": v["rule"]}
        )
        reactions[v["reaction"]] += 1
        row = by_class[e["canonical_class"]]
        is_control = e.get("control", "none") != "none"
        detected = v["reaction"] == "refuted"
        if is_control:
            row["controls"] += 1
            row["controls_clean"] += 0 if detected else 1
        elif e.get("expected_verdict") == "refuted":
            row["refuted_injected"] += 1
            row["refuted_detected"] += int(detected)

    judge_dir = Path(args.judge_dir)
    judge_dir.mkdir(parents=True, exist_ok=True)
    (judge_dir / "deterministic_verdicts.json").write_text(
        json.dumps({"verdicts": verdicts}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    llm: dict[str, str] = {}
    for path in sorted(judge_dir.glob("verdicts_*.json")):
        for v in json.loads(path.read_text(encoding="utf-8")).get("verdicts", []):
            llm[v["id"]] = v.get("reaction", "none")

    def _detected(reaction: str) -> bool:
        return reaction == "refuted"

    agreement_detected = None
    agreement_label = None
    disagreements: list[dict] = []
    if llm:
        n = len(verdicts)
        agree_det = 0
        agree_lbl = 0
        for v in verdicts:
            e = entry_by_id[v["id"]]
            is_control = e.get("control", "none") != "none"
            llm_r = llm[v["id"]]
            # controls: `clean` (ours) and `none`/`clean` (LLM) mean the same
            norm_det = "none" if (is_control and v["reaction"] == "clean") else v["reaction"]
            norm_llm = "none" if (is_control and llm_r == "clean") else llm_r
            agree_det += int(_detected(norm_det) == _detected(norm_llm))
            agree_lbl += int(norm_det == norm_llm)
            if _detected(norm_det) != _detected(norm_llm):
                disagreements.append(
                    {
                        "id": v["id"],
                        "deterministic": v["reaction"],
                        "llm": llm_r,
                        "rule": v["rule"],
                        "matched": v["matched"],
                        "artifact": (
                            e.get("old") or e.get("target") or e.get("new")
                        ),
                    }
                )
        agreement_detected = round(agree_det / n, 3)
        agreement_label = round(agree_lbl / n, 3)

    summary = {
        "judged": len(verdicts),
        "reactions": dict(sorted(reactions.items())),
        "agreement_with_llm_detected": agreement_detected,
        "agreement_with_llm_label": agreement_label,
        "disagreements": disagreements,
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
    (judge_dir / "deterministic_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                k: summary[k]
                for k in (
                    "judged",
                    "reactions",
                    "agreement_with_llm_detected",
                    "agreement_with_llm_label",
                )
            },
            indent=2,
        )
    )
    for d in disagreements:
        print(
            f"  detected-disagree {d['id']} det={d['deterministic']} llm={d['llm']} "
            f"rule={d['rule']} artifact={d['artifact']!r}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
