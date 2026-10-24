"""Run the engine on the snapshots and score the injected defects.

Stage 4 of the injected-gold protocol (README §7). The engine (SUT) is invoked
here and **only** here: it never influences class or target selection.

For each ``manifest.jsonl`` entry we look up the claims the engine produced on
the relevant snapshot (injected for injections, baseline for controls) and
record a three-way reaction to the injected artifact:

- ``refuted`` — the engine refuted a claim about the artifact;
- ``nei`` — the engine noticed the artifact but abstained (deliberate NEI);
- ``none`` — no claim about the artifact was produced (extraction miss).

``refuted`` is the detection outcome, ``nei`` is an abstention (not a miss), and
``none`` is an extraction miss. Metrics therefore report a refutation rate, an
abstention rate and an extraction-miss rate, plus a breakdown by claim form.

``precision`` on controls: a control is clean unless the engine refuted it.
``completeness_gap`` is reported separately from the ``refuted`` bucket.
Out-of-scope classes stay on the boundary.

Run::

    PYTHONPATH=src uv run python .../scripts/score_injections.py \
        --manifest .../runs/<date>/manifest.jsonl \
        --snapshots .../snapshots --out .../runs/<date>
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
ARTIFACT = SCRIPTS.parents[1]
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(ARTIFACT / "scripts"))
from _paths import REPO_ROOT  # noqa: E402

INJECTED_GOLD = SCRIPTS.parent
BOUNDARY = INJECTED_GOLD / "boundary.json"

OUTCOMES = ("refuted", "nei", "none")


def _rate(k: int, n: int) -> float | None:
    return round(k / n, 3) if n else None


def claim_form(entry: dict) -> str:
    """Surface form of the documented claim the injection targets.

    ``path`` / ``dependency`` come from the artifact class. Otherwise the target
    spelling decides: a call (``name()``), a dotted qualification, or a bare
    name.
    """
    target = str(entry.get("target") or "").strip().strip("`").strip()
    artifact_class = entry.get("artifact_class")
    if artifact_class == "path":
        return "path"
    if artifact_class == "dependency":
        return "dependency"
    if target.endswith("()"):
        return "bare_call"
    if "." in target:
        return "qualified"
    return "bare"


def wilson(k: int, n: int) -> list[float] | None:
    """Wilson 95% confidence interval for a proportion."""
    if n == 0:
        return None
    z = 1.959963984540054
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / denom
    return [round(max(0.0, centre - half), 3), round(min(1.0, centre + half), 3)]


def run_engine(root: Path, out: Path, engine: list[str]) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    env["PYTHONPATH"] = str(REPO_ROOT / "src") + os.pathsep + env.get("PYTHONPATH", "")
    result = subprocess.run(
        [*engine, str(root), str(out)],
        cwd=str(REPO_ROOT),
        env=env,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        sys.stderr.write(result.stderr[-2000:])
        raise SystemExit(f"engine failed on {root} (exit {result.returncode})")


def load_claims(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def covers(claim: dict, line: int) -> bool:
    start = claim.get("line_start")
    end = claim.get("line_end") or start
    if start is None:
        return False
    return start <= line <= end


def obj_match(obj: str, target: str) -> bool:
    o = (obj or "").strip().strip("`").rstrip("/.").lower()
    t = (target or "").strip().strip("`").rstrip("/.").lower()
    if not o or not t:
        return False
    if o == t or o.endswith("/" + t) or t.endswith("/" + o):
        return True
    if o.endswith("." + t) or t.endswith("." + o):
        return True
    if o.rsplit("/", 1)[-1] == t.rsplit("/", 1)[-1]:
        return True
    # Last dot-segment only for dotted symbols, never for path extensions.
    if "/" not in o and "/" not in t:
        return o.rsplit(".", 1)[-1] == t.rsplit(".", 1)[-1]
    return False


def _claim_key(claim: dict) -> tuple[str, str]:
    return (str(claim.get("source", "")).lower(), str(claim.get("object", "")).lower())


def _keys(claims: list[dict], verdict: str) -> set[tuple[str, str]]:
    return {_claim_key(c) for c in claims if c.get("code_verdict") == verdict}


def _match_object(entry: dict) -> str:
    """The claim ``object`` the injected defect should surface as.

    ``obj_match`` compares the engine's predicate ``object`` (the referent: a
    path, a dotted symbol, or a dependency name), not the *value* that changed
    (``old``). They differ for a dependency constraint break: ``old`` is a
    constraint string (``>=6.0``) but the object is the dependency name.

    Matching on ``old`` there misses genuine refutations, so map each artifact
    class to the referent it produces.
    """
    artifact_class = entry.get("artifact_class")
    if artifact_class == "dependency":
        return entry.get("symbol") or entry.get("target") or ""
    return entry.get("old") or entry.get("target") or ""


def _new_matching(
    inj_claims: list[dict], base_claims: list[dict], verdict: str, artifact: str
) -> list[dict]:
    """Claims with ``verdict`` in the injected tree that are new vs baseline."""
    base_keys = _keys(base_claims, verdict)
    return [
        c
        for c in inj_claims
        if c.get("code_verdict") == verdict
        and _claim_key(c) not in base_keys
        and obj_match(c.get("object", ""), artifact)
    ]


def reaction(entry: dict, inj_claims: list[dict], base_claims: list[dict]) -> str:
    """MPChecker-style reaction of the tool to the injected artifact.

    Detection is **not** bound to the recorded doc line: it scans the whole
    baseline->injected claim diff for a *new* claim whose object matches the
    injected artifact (old symbol/path/dependency/target). ``refuted`` is a
    finding; ``nei`` is a reaction that abstained; ``none`` is no reaction.
    """
    artifact = _match_object(entry)
    if _new_matching(inj_claims, base_claims, "REFUTED", artifact):
        return "refuted"
    if _new_matching(inj_claims, base_claims, "NEI", artifact):
        return "nei"
    return "none"


def classify(entry: dict, inj_claims: list[dict], base_claims: list[dict]) -> dict:
    """Three-outcome reaction for one manifest entry (MPChecker scheme).

    ``reaction`` is one of ``refuted`` / ``nei`` / ``none`` for injections
    (``clean`` / ``refuted`` for controls). ``detected`` is kept for backward
    compatibility and means ``reaction == "refuted"``; ``abstained`` and
    ``extraction_miss`` expose the other two outcomes separately.
    """
    form = claim_form(entry)
    if entry.get("control", "none") != "none":
        artifact = _match_object(entry)
        refuted = any(
            c.get("code_verdict") == "REFUTED" and obj_match(c.get("object", ""), artifact)
            for c in base_claims
        )
        return {
            "reaction": "refuted" if refuted else "clean",
            "detected": refuted,
            "abstained": False,
            "extraction_miss": False,
            "claim_form": form,
        }

    if entry.get("expected_verdict") == "completeness_gap":
        found = _new_matching(
            inj_claims, base_claims, "REFUTED", entry.get("target", "")
        )
        r = "refuted" if found else "none"
        return {
            "reaction": r,
            "detected": bool(found),
            "abstained": False,
            "extraction_miss": r == "none",
            "claim_form": form,
        }

    r = reaction(entry, inj_claims, base_claims)
    return {
        "reaction": r,
        "detected": r == "refuted",
        "abstained": r == "nei",
        "extraction_miss": r == "none",
        "claim_form": form,
    }


def score(manifest: list[dict], claims_by: dict[tuple[str, str], list[dict]]) -> dict:
    def blank() -> dict:
        return {
            "refuted": {
                "injected": 0,
                "verified": 0,
                "refuted": 0,
                "nei": 0,
                "none": 0,
                "reactions": defaultdict(int),
            },
            "completeness_gap": {
                "injected": 0,
                "verified": 0,
                "refuted": 0,
                "nei": 0,
                "none": 0,
                "reactions": defaultdict(int),
            },
            "controls": {"n": 0, "clean": 0},
        }

    by_class: dict[str, dict] = defaultdict(blank)
    for e in manifest:
        is_control = e.get("control", "none") != "none"
        inj_claims = claims_by.get((e["repo"], "injected"), [])
        base_claims = claims_by.get((e["repo"], "baseline"), [])
        info = classify(e, inj_claims, base_claims)
        row = by_class[e["canonical_class"]]
        if is_control:
            row["controls"]["n"] += 1
            row["controls"]["clean"] += 0 if info["detected"] else 1
            continue
        outcome = e.get("expected_verdict") or "refuted"
        bucket = row[outcome]
        bucket["injected"] += 1
        bucket["verified"] += 1 if e.get("verifier") == "ok" else 0
        bucket["reactions"][info["reaction"]] += 1
        if info["reaction"] in OUTCOMES:
            bucket[info["reaction"]] += 1

    def block(raw: dict) -> dict:
        n = raw["injected"]
        return {
            "injected": n,
            "verified": raw["verified"],
            "refuted": raw["refuted"],
            "nei": raw["nei"],
            "none": raw["none"],
            # Backward-compatible detection view: refuted only.
            "detected": raw["refuted"],
            "recall": _rate(raw["refuted"], n),
            "recall_ci95": wilson(raw["refuted"], n),
            "refutation_rate": _rate(raw["refuted"], n),
            "refutation_ci95": wilson(raw["refuted"], n),
            "abstention_rate": _rate(raw["nei"], n),
            "extraction_miss_rate": _rate(raw["none"], n),
            "reactions": dict(sorted(raw["reactions"].items())),
        }

    results: dict[str, dict] = {}
    for cls, row in sorted(by_class.items()):
        ctl = row["controls"]
        results[cls] = {
            "refuted": block(row["refuted"]),
            "completeness_gap": block(row["completeness_gap"]),
            "controls": {
                "n": ctl["n"],
                "clean": ctl["clean"],
                "precision": _rate(ctl["clean"], ctl["n"]),
                "precision_ci95": wilson(ctl["clean"], ctl["n"]),
            },
        }
    return results


def by_claim_form(
    manifest: list[dict], claims_by: dict[tuple[str, str], list[dict]]
) -> dict[str, dict]:
    """Three-outcome breakdown of the ``refuted`` bucket by claim form."""
    forms: dict[str, dict] = defaultdict(
        lambda: {
            "injected": 0,
            "verified": 0,
            "refuted": 0,
            "nei": 0,
            "none": 0,
            "controls": 0,
            "controls_clean": 0,
        }
    )
    for e in manifest:
        info = classify(
            e,
            claims_by.get((e["repo"], "injected"), []),
            claims_by.get((e["repo"], "baseline"), []),
        )
        row = forms[info["claim_form"]]
        if e.get("control", "none") != "none":
            row["controls"] += 1
            row["controls_clean"] += 0 if info["detected"] else 1
            continue
        if (e.get("expected_verdict") or "refuted") != "refuted":
            continue
        row["injected"] += 1
        row["verified"] += 1 if e.get("verifier") == "ok" else 0
        if info["reaction"] in OUTCOMES:
            row[info["reaction"]] += 1

    out: dict[str, dict] = {}
    for form, row in sorted(forms.items()):
        n = row["injected"]
        out[form] = {
            "injected": n,
            "verified": row["verified"],
            "refuted": row["refuted"],
            "nei": row["nei"],
            "none": row["none"],
            "refutation_rate": _rate(row["refuted"], n),
            "abstention_rate": _rate(row["nei"], n),
            "extraction_miss_rate": _rate(row["none"], n),
            "controls": row["controls"],
            "controls_clean": row["controls_clean"],
            "precision": _rate(row["controls_clean"], row["controls"]),
        }
    return out


def overall(results: dict[str, dict]) -> dict:
    inj = sum(r["refuted"]["injected"] for r in results.values())
    verified = sum(r["refuted"]["verified"] for r in results.values())
    ref = sum(r["refuted"]["refuted"] for r in results.values())
    nei = sum(r["refuted"]["nei"] for r in results.values())
    none = sum(r["refuted"]["none"] for r in results.values())
    gap_inj = sum(r["completeness_gap"]["injected"] for r in results.values())
    gap_ref = sum(r["completeness_gap"]["refuted"] for r in results.values())
    ctl = sum(r["controls"]["n"] for r in results.values())
    clean = sum(r["controls"]["clean"] for r in results.values())
    return {
        "refuted_injected": inj,
        "refuted_verified": verified,
        "refuted": ref,
        "nei": nei,
        "none": none,
        # Backward-compatible detection view: refuted only.
        "refuted_detected": ref,
        "recall_refuted": _rate(ref, inj),
        "recall_ci95": wilson(ref, inj),
        "refutation_rate": _rate(ref, inj),
        "refutation_ci95": wilson(ref, inj),
        "abstention_rate": _rate(nei, inj),
        "extraction_miss_rate": _rate(none, inj),
        "completeness_gap_injected": gap_inj,
        "completeness_gap_detected": gap_ref,
        "completeness_gap_refuted": gap_ref,
        "controls": ctl,
        "controls_clean": clean,
        "precision": _rate(clean, ctl),
        "precision_ci95": wilson(clean, ctl),
    }


def seed_stats(manifest: list[dict], claims_by: dict[tuple[str, str], list[dict]]) -> dict:
    by_op: dict[str, dict] = {}
    per_seed: dict[int, dict] = {}
    for e in manifest:
        # Controls are not operator injections and do not carry ``op_id``;
        # control precision is reported by ``score``/``control_misses``.
        if e.get("control", "none") != "none":
            continue
        key = f"{e['repo']}::{e['op_id']}"
        row = by_op.setdefault(
            key,
            {"pool_size": e.get("pool_size"), "seeds": set(), "targets": set(), "n": 0},
        )
        row["seeds"].add(e["seed"])
        row["targets"].add((e.get("doc_path", ""), e.get("line", 0), str(e.get("target", ""))))
        row["n"] += 1

        is_control = e.get("control", "none") != "none"
        info = classify(
            e,
            claims_by.get((e["repo"], "injected"), []),
            claims_by.get((e["repo"], "baseline"), []),
        )
        ps = per_seed.setdefault(
            e["seed"],
            {
                "refuted_injected": 0,
                "refuted_verified": 0,
                "refuted": 0,
                "nei": 0,
                "none": 0,
                "refuted_detected": 0,
                "controls": 0,
                "controls_clean": 0,
            },
        )
        if is_control:
            ps["controls"] += 1
            ps["controls_clean"] += 0 if info["detected"] else 1
            continue
        outcome = e.get("expected_verdict") or "refuted"
        if outcome == "refuted":
            ps["refuted_injected"] += 1
            ps["refuted_verified"] += 1 if e.get("verifier") == "ok" else 0
            if info["reaction"] in OUTCOMES:
                ps[info["reaction"]] += 1
            ps["refuted_detected"] += 1 if info["detected"] else 0

    by_op_out = {
        k: {
            "pool_size": v["pool_size"],
            "seeds": sorted(v["seeds"]),
            "n_entries": v["n"],
            "distinct_targets": len(v["targets"]),
            "coverage": round(len(v["targets"]) / v["pool_size"], 3)
            if v["pool_size"]
            else None,
        }
        for k, v in sorted(by_op.items())
    }
    return {"by_operator": by_op_out, "per_seed": {str(k): v for k, v in sorted(per_seed.items())}}


def control_misses(
    manifest: list[dict], claims_by: dict[tuple[str, str], list[dict]]
) -> list[dict]:
    """Controls the engine refuted on the baseline (false findings)."""
    out: list[dict] = []
    for e in manifest:
        if e.get("control", "none") == "none":
            continue
        claims = claims_by.get((e["repo"], "baseline"), [])
        bad = [
            c
            for c in claims
            if c.get("code_verdict") == "REFUTED"
            and obj_match(c.get("object", ""), e.get("target", ""))
        ]
        if bad:
            out.append(
                {
                    "repo": e["repo"],
                    "op_id": e.get("op_id", e.get("control", "")),
                    "doc_path": e.get("doc_path"),
                    "line": e.get("line"),
                    "target": e.get("target"),
                    "verdicts": [
                        {
                            "predicate": c.get("predicate"),
                            "object": c.get("object"),
                            "reason": c.get("code_verdict_reason"),
                        }
                        for c in bad
                    ],
                }
            )
    return out


def unattributed_findings(
    manifest: list[dict], claims_by: dict[tuple[str, str], list[dict]]
) -> dict:
    """Findings on the injected tree not attributable to any injected artifact.

    These are pre-existing refutations (genuine old doc bugs or false positives)
    that survive injection; a precision-proxy companion to the controls.
    """
    arts_by_repo: dict[str, list[str]] = defaultdict(list)
    for e in manifest:
        if e.get("control", "none") != "none":
            continue
        arts_by_repo[e["repo"]].append(_match_object(e))
    out: dict[str, dict] = {}
    for repo in sorted({e["repo"] for e in manifest}):
        arts = arts_by_repo.get(repo, [])
        base = claims_by.get((repo, "baseline"), [])
        inj = claims_by.get((repo, "injected"), [])
        base_refuted = {_claim_key(c) for c in base if c.get("code_verdict") == "REFUTED"}
        new_refuted = [
            c
            for c in inj
            if c.get("code_verdict") == "REFUTED" and _claim_key(c) not in base_refuted
        ]
        unattributed = [
            c
            for c in new_refuted
            if not any(obj_match(c.get("object", ""), a) for a in arts)
        ]
        out[repo] = {
            "baseline_refuted": len(base_refuted),
            "new_refuted": len(new_refuted),
            "unattributed": len(unattributed),
            "examples": [
                {
                    "source": c.get("source"),
                    "line": c.get("line_start"),
                    "predicate": c.get("predicate"),
                    "object": c.get("object"),
                }
                for c in unattributed[:10]
            ],
        }
    return out


def render_seed_md(seed: dict) -> str:
    lines = [
        "# Seed diversity and per-seed detection",
        "",
        "`coverage` = distinct injected targets / candidate-pool size. A pool of 1",
        "is seed-invariant by construction (e.g. a single resolvable path).",
        "",
        "## Per operator × repo",
        "",
        "| repo::operator | pool | entries | distinct targets | coverage | seeds |",
        "|---|---|---|---|---|---|",
    ]
    for key, r in seed["by_operator"].items():
        lines.append(
            f"| {key} | {r['pool_size']} | {r['n_entries']} | {r['distinct_targets']} | "
            f"{r['coverage']} | {len(r['seeds'])} |"
        )
    lines += [
        "",
        "## Per seed",
        "",
        "NEI is a deliberate abstention, not a miss; `none` is an extraction miss.",
        "",
        "| seed | refuted inj | refuted | NEI | none | controls | clean |",
        "|---|---|---|---|---|---|---|",
    ]
    for s, r in seed["per_seed"].items():
        lines.append(
            f"| {s} | {r['refuted_injected']} | {r['refuted']} | {r['nei']} | "
            f"{r['none']} | {r['controls']} | {r['controls_clean']} |"
        )
    lines.append("")
    return "\n".join(lines)


def render_md(payload: dict) -> str:
    def fmt(x) -> str:
        return "-" if x is None else str(x)

    o = payload["overall"]
    lines = [
        "# Injected-gold metrics",
        "",
        f"- date: {payload['date']}",
        f"- seed: {payload['seed']}",
        f"- repos: {', '.join(payload['repos'])}",
        f"- engine: `{' '.join(payload['engine'])}`",
        f"- smoke/contamination: {payload['contamination']}",
        "",
        "## Overall",
        "",
        "NEI is a deliberate abstention, not a failure; only `none` is an",
        "extraction miss. `refutation + abstention + extraction miss = 1`.",
        "",
        "| verified/injected | refuted | NEI | none | refutation [ci95] | "
        "abstention | extraction miss | gap inj/refuted | controls | clean | "
        "precision [ci95] |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
        f"| {o['refuted_verified']}/{o['refuted_injected']} | {o['refuted']} | "
        f"{o['nei']} | {o['none']} | {o['refutation_rate']} {o['refutation_ci95']} | "
        f"{o['abstention_rate']} | {o['extraction_miss_rate']} | "
        f"{o['completeness_gap_injected']}/{o['completeness_gap_refuted']} | "
        f"{o['controls']} | {o['controls_clean']} | "
        f"{o['precision']} {o['precision_ci95']} |",
        "",
        "## Per canonical class",
        "",
        "| canonical_class | verified/injected | refuted | NEI | none | refutation | "
        "abstention | extraction miss | gap inj/refuted | controls | precision |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for cls, r in payload["by_class"].items():
        b = r["refuted"]
        lines.append(
            f"| {cls} | {b['verified']}/{b['injected']} | {b['refuted']} | "
            f"{b['nei']} | {b['none']} | {fmt(b['refutation_rate'])} | "
            f"{fmt(b['abstention_rate'])} | {fmt(b['extraction_miss_rate'])} | "
            f"{r['completeness_gap']['injected']}/{r['completeness_gap']['refuted']} | "
            f"{r['controls']['n']} | {fmt(r['controls']['precision'])} |"
        )
    lines += [
        "",
        "## Outcome by claim form",
        "",
        "Aggregated over the `refuted` bucket (controls shown separately).",
        "",
        "| claim form | verified/injected | refuted | NEI | none | refutation | "
        "abstention | extraction miss | controls | precision |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for form, r in payload.get("by_claim_form", {}).items():
        lines.append(
            f"| {form} | {r['verified']}/{r['injected']} | {r['refuted']} | "
            f"{r['nei']} | {r['none']} | {fmt(r['refutation_rate'])} | "
            f"{fmt(r['abstention_rate'])} | {fmt(r['extraction_miss_rate'])} | "
            f"{r['controls']} | {fmt(r['precision'])} |"
        )
    lines += [
        "",
        "## Reaction distribution (MPChecker: how the tool reacted)",
        "",
        "| canonical_class | bucket | refuted | nei | none |",
        "|---|---|---|---|---|",
    ]
    for cls, r in payload["by_class"].items():
        for bucket in ("refuted", "completeness_gap"):
            b = r[bucket]
            if not b["injected"]:
                continue
            rx = b["reactions"]
            lines.append(
                f"| {cls} | {bucket} | {rx.get('refuted', 0)} | {rx.get('nei', 0)} | "
                f"{rx.get('none', 0)} |"
            )
    lines += [
        "",
        "## Unattributed findings (injected tree, precision proxy)",
        "",
        "New refutations on the injected tree not matching any injected artifact —",
        "pre-existing findings (genuine or false) that survive injection.",
        "",
        "| repo | baseline refuted | new refuted | unattributed |",
        "|---|---|---|---|",
    ]
    for repo, r in payload.get("unattributed_findings", {}).items():
        lines.append(
            f"| {repo} | {r['baseline_refuted']} | {r['new_refuted']} | {r['unattributed']} |"
        )
    lines += [
        "",
        "## Control false refutes (baseline)",
        "",
    ]
    fr = payload.get("control_false_refutes", [])
    if not fr:
        lines.append("None.")
    else:
        for item in fr:
            lines.append(
                f"- `{item['repo']}` {item['op_id']} `{item['target']}` "
                f"@ {item['doc_path']}:{item['line']}"
            )
            for v in item["verdicts"]:
                lines.append(f"  - {v['predicate']} {v['object']!r} — {v['reason']}")
    lines += [
        "",
        "## Boundary (out-of-scope classes, not operators)",
        "",
        "```",
        json.dumps(payload["boundary"], indent=2, ensure_ascii=False),
        "```",
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--snapshots", required=True)
    ap.add_argument("--out", required=True, help="run dir for metrics.{md,json}")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument(
        "--engine",
        default="",
        help="engine command prefix (default: <python> -m docassay.core.dump_claims)",
    )
    ap.add_argument("--force", action="store_true", help="re-run the engine even if claims exist")
    args = ap.parse_args(argv)

    engine = args.engine.split() if args.engine else [
        sys.executable,
        "-m",
        "docassay.core.dump_claims",
    ]
    manifest_path = Path(args.manifest)
    snapshots = Path(args.snapshots)
    out = Path(args.out)
    claims_dir = out / "claims"
    claims_dir.mkdir(parents=True, exist_ok=True)

    manifest = [
        json.loads(line)
        for line in manifest_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    repos = sorted({e["repo"] for e in manifest})

    claims_by: dict[tuple[str, str], list[dict]] = {}
    for repo in repos:
        for snap in ("baseline", "injected"):
            cache = claims_dir / f"{repo}__{snap}.jsonl"
            if args.force or not cache.is_file():
                print(f"running engine: {repo} ({snap})")
                run_engine(snapshots / f"{repo}__{snap}", cache, engine)
            claims_by[(repo, snap)] = load_claims(cache)

    results = score(manifest, claims_by)
    boundary = json.loads(BOUNDARY.read_text(encoding="utf-8"))
    synth_dirs = (INJECTED_GOLD / "synthetic", INJECTED_GOLD / "synthetic-natural")

    def _corpus_name(repo_id: str) -> str:
        # Snapshot ids are ``<repo>__<class>__s<seed>_<sample>`` or
        # ``<repo>__control``; the corpus directory is the first segment.
        return repo_id.split("__", 1)[0]

    is_synthetic = bool(repos) and all(
        any((d / _corpus_name(r)).is_dir() for d in synth_dirs) for r in repos
    )
    is_conformance = bool(manifest) and all(
        e.get("repo_class") == "conformance" for e in manifest
    )

    if is_conformance:
        contamination = (
            "conformance: constructed cases on a clean synthetic base "
            "(predicate-defined artifact classes; separate provenance arm)"
        )
    elif is_synthetic:
        contamination = (
            "synthetic: generated repos, docs and code consistent by construction "
            "(uncontaminated evaluation corpus)"
        )
    else:
        contamination = (
            "smoke: repos are from test_repos/validation_repos (held-out); "
            "not an evaluation corpus"
        )

    payload = {
        "date": date.today().isoformat(),
        "seed": args.seed,
        "repos": repos,
        "engine": engine,
        "contamination": contamination,
        "overall": overall(results),
        "by_class": results,
        "by_claim_form": by_claim_form(manifest, claims_by),
        "control_false_refutes": control_misses(manifest, claims_by),
        "unattributed_findings": unattributed_findings(manifest, claims_by),
        "boundary": {
            k: boundary[k]
            for k in (
                "out_of_scope_repo_expr",
                "out_of_scope_doc_process_data",
                "candidate_unconfirmed",
            )
        },
    }
    seed = seed_stats(manifest, claims_by)
    out.mkdir(parents=True, exist_ok=True)
    (out / "metrics.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (out / "metrics.md").write_text(render_md(payload), encoding="utf-8")
    (out / "seed_diversity.json").write_text(
        json.dumps(seed, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (out / "seed_diversity.md").write_text(render_seed_md(seed), encoding="utf-8")

    print(json.dumps(payload["overall"], indent=2))
    print(f"wrote {out / 'metrics.md'}, metrics.json, seed_diversity.{{md,json}}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
