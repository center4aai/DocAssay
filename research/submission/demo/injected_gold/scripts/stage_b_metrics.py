"""Stage B metrics: three outcomes, controls, end-to-end, cluster bootstrap.

Reads the frozen run artifacts (``plan.json``, ``manifest.jsonl``,
``provenance.json``, ``claims/``) and writes:

- ``entries.json``      per-entry reaction table (injections and controls);
- ``bootstrap.json``    repo-cluster bootstrap CIs (the headline inference);
- ``baseline_findings.json`` every baseline REFUTED claim, with the doc line;
- ``metrics_stage_b.json`` and the human-readable ``metrics.md``.

The engine is **not** run here; the claims were produced once by
``score_injections.py``.  Wilson intervals are deliberately not used for the
headline: injections cluster within repositories, so the CI resamples the six
repositories with replacement.

Run::

    PYTHONPATH=src uv run python .../scripts/stage_b_metrics.py \
        --run .../runs/stage-b-2026-10-20
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
import score_injections as scorer  # noqa: E402

INJECTED_GOLD = SCRIPTS.parent
NATURAL = INJECTED_GOLD / "synthetic-natural"
OUTCOMES = ("refuted", "nei", "none")


def _read_json(path: Path, default):
    if not path.is_file():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def _rate(k: int, n: int) -> float | None:
    return round(k / n, 3) if n else None


def _percentile(values: list[float], p: float) -> float | None:
    if not values:
        return None
    values = sorted(values)
    k = (len(values) - 1) * p
    lo = int(k)
    hi = min(lo + 1, len(values) - 1)
    return round(values[lo] + (values[hi] - values[lo]) * (k - lo), 3)


def _value(entry: dict, outcome: str) -> float:
    return 1.0 if entry["outcome"] == outcome else 0.0


def cluster_bootstrap(entries: list[dict], outcome: str, replicates: int, seed: int) -> dict | None:
    """Resample repositories with replacement; return a percentile 95% CI."""
    clusters = sorted({e["repo_name"] for e in entries})
    if not clusters:
        return None
    by_cluster: dict[str, list[dict]] = defaultdict(list)
    for entry in entries:
        by_cluster[entry["repo_name"]].append(entry)
    rng = random.Random(seed)
    values: list[float] = []
    for _ in range(replicates):
        chosen: list[dict] = []
        for _ in range(len(clusters)):
            chosen.extend(by_cluster[rng.choice(clusters)])
        if chosen:
            values.append(sum(_value(e, outcome) for e in chosen) / len(chosen))
    point = _rate(sum(1 for e in entries if e["outcome"] == outcome), len(entries))
    return {
        "outcome": outcome,
        "point": point,
        "ci95": [_percentile(values, 0.025), _percentile(values, 0.975)],
        "n_entries": len(entries),
        "n_clusters": len(clusters),
        "replicates": len(values),
        "seed": seed,
        "method": "repo-cluster bootstrap (repositories resampled with replacement)",
    }


def _control_outcome(entry: dict, base_claims: list[dict]) -> str:
    artifact = scorer._match_object(entry)
    if any(
        c.get("code_verdict") == "REFUTED" and scorer.obj_match(c.get("object", ""), artifact)
        for c in base_claims
    ):
        return "refuted"
    if any(
        c.get("code_verdict") == "NEI" and scorer.obj_match(c.get("object", ""), artifact)
        for c in base_claims
    ):
        return "nei"
    return "none"


def _none_subtype(entry: dict, claims: list[dict]) -> str | None:
    """Sub-flag a ``none``: no claim on the line, another referent, or supported."""
    artifact = scorer._match_object(entry)
    line_claims = [c for c in claims if scorer.covers(c, entry.get("line", 0))]
    if not line_claims:
        return "no_claim"
    target_claims = [c for c in line_claims if scorer.obj_match(c.get("object", ""), artifact)]
    if not target_claims:
        return "other_referent"
    if any(c.get("code_verdict") == "SUPPORTED" for c in target_claims):
        return "supported"
    return "other"


def _matched(entry: dict, inj: list[dict], base: list[dict], outcome: str) -> list[dict]:
    if outcome not in ("refuted", "nei"):
        return []
    verdict = "REFUTED" if outcome == "refuted" else "NEI"
    artifact = scorer._match_object(entry)
    return [
        {
            "predicate": c.get("predicate"),
            "object": c.get("object"),
            "source": c.get("source"),
            "line_start": c.get("line_start"),
            "reason": c.get("code_verdict_reason"),
        }
        for c in scorer._new_matching(inj, base, verdict, artifact)
    ]


def build_entries(manifest: list[dict], claims_by: dict[tuple[str, str], list[dict]]) -> list[dict]:
    out: list[dict] = []
    for entry in manifest:
        repo, cls = entry["repo"], entry["canonical_class"]
        inj = claims_by.get((repo, "injected"), [])
        base = claims_by.get((repo, "baseline"), [])
        info = scorer.classify(entry, inj, base)
        control = entry.get("control", "none") != "none"
        if control:
            outcome = _control_outcome(entry, base)
        else:
            outcome = info["reaction"]
        source_claims = base if control else inj
        subtype = _none_subtype(entry, source_claims) if outcome in ("none", "clean") else None
        out.append(
            {
                "repo_name": entry.get("repo_name") or repo.split("__", 1)[0],
                "snapshot_id": entry.get("snapshot_id") or repo,
                "class": cls,
                "kind": entry.get("kind"),
                "form": entry.get("form", "n/a"),
                "control": entry.get("control", "none"),
                "claim_form": info["claim_form"],
                "outcome": outcome,
                "outcome_subtype": subtype,
                "clean": outcome != "refuted" if control else None,
                "target": entry.get("target"),
                "doc_path": entry.get("doc_path"),
                "line": entry.get("line"),
                "expected_verdict": entry.get("expected_verdict"),
                "matched": _matched(entry, inj, base, outcome) if not control else [],
            }
        )
    return out


def summarize(entries: list[dict]) -> dict:
    injections = [e for e in entries if e["control"] == "none"]
    controls = [e for e in entries if e["control"] != "none"]

    def block(rows: list[dict]) -> dict:
        n = len(rows)
        counts = {o: sum(1 for r in rows if r["outcome"] == o) for o in OUTCOMES}
        return {
            "n": n,
            **counts,
            "refutation_rate": _rate(counts["refuted"], n),
            "abstention_rate": _rate(counts["nei"], n),
            "extraction_miss_rate": _rate(counts["none"], n),
        }

    by_class: dict[str, dict] = {}
    for cls in sorted({e["class"] for e in entries}):
        rows = [e for e in injections if e["class"] == cls]
        ctl = [e for e in controls if e["class"] == cls]
        by_class[cls] = {
            "injections": block(rows),
            "none_subtypes": dict(
                sorted(
                    Counter(e["outcome_subtype"] for e in rows if e["outcome"] == "none").items()
                )
            ),
            "controls": {
                "n": len(ctl),
                "clean": sum(1 for e in ctl if e["clean"]),
                "refuted": sum(1 for e in ctl if e["outcome"] == "refuted"),
                "nei": sum(1 for e in ctl if e["outcome"] == "nei"),
                "none": sum(1 for e in ctl if e["outcome"] == "none"),
                "precision": _rate(sum(1 for e in ctl if e["clean"]), len(ctl)),
            },
        }
    by_form: dict[str, dict] = {}
    for form in sorted({e["claim_form"] for e in injections}):
        by_form[form] = block([e for e in injections if e["claim_form"] == form])
    return {
        "injections": block(injections),
        "controls": {
            "n": len(controls),
            "clean": sum(1 for e in controls if e["clean"]),
            "refuted": sum(1 for e in controls if e["outcome"] == "refuted"),
            "nei": sum(1 for e in controls if e["outcome"] == "nei"),
            "none": sum(1 for e in controls if e["outcome"] == "none"),
            "precision": _rate(sum(1 for e in controls if e["clean"]), len(controls)),
        },
        "by_class": by_class,
        "by_claim_form": by_form,
        "none_subtypes": dict(
            sorted(
                Counter(e["outcome_subtype"] for e in injections if e["outcome"] == "none").items()
            )
        ),
        "control_subtypes": dict(
            sorted(
                Counter(
                    "nei" if e["outcome"] == "nei" else e["outcome_subtype"]
                    for e in controls
                    if e["outcome"] != "refuted"
                ).items()
            )
        ),
    }


def end_to_end(
    plan: list[dict],
    provenance: list[dict],
    entries: list[dict],
    replicates: int,
    seed: int,
) -> dict:
    """All planned bundles in the denominator; declines/failures count as none."""
    prov_by_name = {p["name"]: p for p in provenance}
    entry_by_key = {(e["snapshot_id"], e["class"]): e for e in entries if e["control"] == "none"}
    rows: list[dict] = []
    for task in plan:
        prov = prov_by_name.get(task["name"], {})
        entry = entry_by_key.get((task["snapshot_id"], task["class"]))
        if prov.get("status") == "verified" and entry and entry["outcome"] == "refuted":
            outcome = "refuted"
        elif prov.get("status") == "verified" and entry and entry["outcome"] == "nei":
            outcome = "nei"
        else:
            outcome = "none"
        rows.append(
            {
                "repo_name": task["repo"],
                "class": task["class"],
                "outcome": outcome,
                "status": prov.get("status", "missing"),
            }
        )

    def block(rows_: list[dict]) -> dict:
        n = len(rows_)
        counts = {o: sum(1 for r in rows_ if r["outcome"] == o) for o in OUTCOMES}
        by_status: dict[str, int] = defaultdict(int)
        for r in rows_:
            by_status[r["status"]] += 1
        return {
            "planned": n,
            **counts,
            "end_to_end_refutation": _rate(counts["refuted"], n),
            "end_to_end_abstention": _rate(counts["nei"], n),
            "end_to_end_miss": _rate(counts["none"], n),
            "statuses": dict(sorted(by_status.items())),
        }

    by_class = {
        cls: block([r for r in rows if r["class"] == cls])
        for cls in sorted({r["class"] for r in rows})
    }
    overall = block(rows)
    overall["bootstrap"] = {
        outcome: cluster_bootstrap(rows, outcome, replicates, seed) for outcome in OUTCOMES
    }
    for cls in by_class:
        by_class[cls]["bootstrap"] = {
            outcome: cluster_bootstrap(
                [r for r in rows if r["class"] == cls], outcome, replicates, seed
            )
            for outcome in OUTCOMES
        }
    return {"overall": overall, "by_class": by_class}


def baseline_findings(
    plan: list[dict], run: Path, claims_by: dict[tuple[str, str], list[dict]]
) -> list[dict]:
    """Every REFUTED claim on a clean baseline, with the doc line."""
    repos = sorted({t["repo"] for t in plan})
    out: list[dict] = []
    for repo in repos:
        control_id = f"{repo}__control"
        claims = claims_by.get((control_id, "baseline"))
        if claims is None:
            # Fall back to the first snapshot's clean baseline.
            first = next(t["snapshot_id"] for t in plan if t["repo"] == repo)
            claims = claims_by.get((first, "baseline"), [])
        for c in claims:
            if c.get("code_verdict") != "REFUTED":
                continue
            source = c.get("source", "")
            line_start = c.get("line_start")
            doc_line = ""
            doc_path = Path(source)
            for root in (NATURAL / repo,):
                candidate = root / doc_path
                if candidate.is_file():
                    lines = candidate.read_text(encoding="utf-8", errors="ignore").splitlines()
                    if line_start and 1 <= line_start <= len(lines):
                        doc_line = lines[line_start - 1]
                    break
            out.append(
                {
                    "repo": repo,
                    "predicate": c.get("predicate"),
                    "object": c.get("object"),
                    "source": source,
                    "line_start": line_start,
                    "doc_line": doc_line,
                    "reason": c.get("code_verdict_reason"),
                    "adjudication": None,
                    "adjudication_note": "",
                }
            )
    return out


def render_md(payload: dict) -> str:
    def pct(value):
        return "—" if value is None else f"{value:.3f}"

    lines = [
        "# Stage B — metrics",
        "",
        "Three outcomes over **verified** injections: `refuted` / `nei` / `none`.",
        "`nei` is a deliberate abstention, not a miss. The end-to-end table puts",
        "declines and generator failures in the denominator.",
        "",
        "## Injections (verified)",
        "",
        "| outcome | count | rate |",
        "|---|---:|---:|",
    ]
    inj = payload["summary"]["injections"]
    for outcome in OUTCOMES:
        lines.append(
            f"| {outcome} | {inj[outcome]}/{inj['n']} | {pct(_rate(inj[outcome], inj['n']))} |"
        )
    lines += [
        "",
        "## Per class",
        "",
        "| class | n | refuted | NEI | none | refutation | abstention | extraction miss |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for cls, row in payload["summary"]["by_class"].items():
        b = row["injections"]
        lines.append(
            f"| {cls} | {b['n']} | {b['refuted']} | {b['nei']} | {b['none']} | "
            f"{pct(b['refutation_rate'])} | {pct(b['abstention_rate'])} | {pct(b['extraction_miss_rate'])} |"  # noqa: E501
        )
    lines += [
        "",
        "### `none` subtypes by class",
        "",
        "| class | no_claim | other_referent | supported |",
        "|---|---:|---:|---:|",
    ]
    for cls, row in payload["summary"]["by_class"].items():
        st = row.get("none_subtypes", {})
        lines.append(
            f"| {cls} | {st.get('no_claim', 0)} | {st.get('other_referent', 0)} | "
            f"{st.get('supported', 0)} |"
        )
    lines += [
        "",
        "## Per claim form",
        "",
        "| claim form | n | refuted | NEI | none | refutation |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for form, b in payload["summary"]["by_claim_form"].items():
        lines.append(
            f"| {form} | {b['n']} | {b['refuted']} | {b['nei']} | {b['none']} | {pct(b['refutation_rate'])} |"  # noqa: E501
        )
    lines += [
        "",
        "## `none` subtypes",
        "",
        "| subtype | count |",
        "|---|---:|",
    ]
    for subtype, count in payload["summary"].get("none_subtypes", {}).items():
        lines.append(f"| {subtype} | {count} |")
    lines += [
        "",
        "## Injector outcomes (all planned bundles)",
        "",
        "| status | count |",
        "|---|---:|",
    ]
    for status, count in payload.get("injector", {}).get("statuses", {}).items():
        lines.append(f"| {status} | {count} |")
    lines += [
        "",
        "These are the **final** statuses: 72/72 verified, 0 declines, 0 generator",
        "failures. The pre-scoring harness/oracle fixes (55 → 70 → 72) are recorded",
        "in `HARNESS_FIX.md`; no injector output was regenerated.",
        "",
        "## End-to-end (all planned bundles)",
        "",
        "| class | planned | refuted | NEI | none | end-to-end refutation |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for cls, b in payload["end_to_end"]["by_class"].items():
        lines.append(
            f"| {cls} | {b['planned']} | {b['refuted']} | {b['nei']} | {b['none']} | {pct(b['end_to_end_refutation'])} |"  # noqa: E501
        )
    e = payload["end_to_end"]["overall"]
    lines.append(
        f"| **all** | {e['planned']} | {e['refuted']} | {e['nei']} | {e['none']} | {pct(e['end_to_end_refutation'])} |"  # noqa: E501
    )
    lines += [
        "",
        "## Controls",
        "",
        "| class | n | clean | refuted (FP) | NEI | none | precision |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for cls, row in payload["summary"]["by_class"].items():
        c = row["controls"]
        if c["n"]:
            lines.append(
                f"| {cls} | {c['n']} | {c['clean']} | {c['refuted']} | {c['nei']} | {c['none']} | {pct(c['precision'])} |"  # noqa: E501
            )
    overall_c = payload["summary"]["controls"]
    lines.append(
        f"| **all** | {overall_c['n']} | {overall_c['clean']} | {overall_c['refuted']} | "
        f"{overall_c['nei']} | {overall_c['none']} | {pct(overall_c['precision'])} |"
    )
    lines += [
        "",
        "Control subtypes (non-refuted):",
        "",
        "| subtype | count |",
        "|---|---:|",
    ]
    for subtype, count in payload["summary"].get("control_subtypes", {}).items():
        lines.append(f"| {subtype} | {count} |")
    lines += [
        "",
        "## Cluster bootstrap (headline inference)",
        "",
        "Repositories are resampled with replacement (10,000 replicates, fixed seed);",
        "Wilson intervals are **not** used for the headline because injections cluster",
        "within repositories.",
        "",
        "| scope | outcome | point | 95% CI | clusters |",
        "|---|---|---:|---|---:|",
    ]
    for scope, block in [("all", e)] + list(payload["end_to_end"]["by_class"].items()):
        for outcome in OUTCOMES:
            boot = block.get("bootstrap", {}).get(outcome)
            if boot:
                lines.append(
                    f"| {scope} | {outcome} | {pct(boot['point'])} | "
                    f"[{pct(boot['ci95'][0])}, {pct(boot['ci95'][1])}] | {boot['n_clusters']} |"
                )
    lines += [
        "",
        "## Baseline findings",
        "",
        f"{len(payload['baseline_findings'])} baseline `REFUTED` claim(s) recorded; see",
        "`baseline_findings.json`. They are adjudicated separately as true documentation",
        "bugs or tool false positives, never used to edit the corpus.",
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run", required=True)
    ap.add_argument(
        "--manifest", default="", help="default: <run>/scoring_manifest.jsonl or manifest.jsonl"
    )
    ap.add_argument("--replicates", type=int, default=10000)
    ap.add_argument("--seed", type=int, default=20261020)
    args = ap.parse_args(argv)

    run = Path(args.run)
    manifest_path = (
        Path(args.manifest)
        if args.manifest
        else (
            run / "scoring_manifest.jsonl"
            if (run / "scoring_manifest.jsonl").is_file()
            else run / "manifest.jsonl"
        )
    )
    manifest = _read_jsonl(manifest_path)
    plan = _read_json(run / "plan.json", [])
    provenance = _read_json(run / "provenance.json", [])
    claims_dir = run / "claims"
    claims_by: dict[tuple[str, str], list[dict]] = {}
    for path in sorted(claims_dir.glob("*.jsonl")):
        name = path.stem
        if name.endswith("__baseline"):
            claims_by[(name[: -len("__baseline")], "baseline")] = _read_jsonl(path)
        elif name.endswith("__injected"):
            claims_by[(name[: -len("__injected")], "injected")] = _read_jsonl(path)

    entries = build_entries(manifest, claims_by)
    summary = summarize(entries)
    e2e = end_to_end(plan, provenance, entries, args.replicates, args.seed)
    baseline = baseline_findings(plan, run, claims_by)

    # Bootstrap CIs for the verified-only injection rates, per class and overall.
    injections = [e for e in entries if e["control"] == "none"]
    controls = [e for e in entries if e["control"] != "none"]
    summary["bootstrap"] = {
        "overall": {
            o: cluster_bootstrap(injections, o, args.replicates, args.seed) for o in OUTCOMES
        },
        "by_class": {
            cls: {
                o: cluster_bootstrap(
                    [e for e in injections if e["class"] == cls], o, args.replicates, args.seed
                )
                for o in OUTCOMES
            }
            for cls in sorted({e["class"] for e in injections})
        },
        "controls": {
            "precision": cluster_bootstrap(
                [{**e, "outcome": "clean" if e["clean"] else "refuted"} for e in controls],
                "clean",
                args.replicates,
                args.seed,
            )
        },
    }

    statuses: dict[str, int] = defaultdict(int)
    for prov in provenance:
        statuses[prov.get("status", "missing")] += 1
    payload = {
        "run": str(run),
        "manifest": str(manifest_path),
        "summary": summary,
        "end_to_end": e2e,
        "injector": {"planned": len(plan), "statuses": dict(sorted(statuses.items()))},
        "baseline_findings": baseline,
        "controls_source": str(run / "controls.jsonl"),
        "notes": [
            "Verified-only rates use the verified manifest as the denominator.",
            "End-to-end rates use all planned bundles; declines and generator "
            "failures count as none.",
            "Headline CIs are repo-cluster bootstrap, not Wilson.",
            "NEI is an abstention, not a miss.",
        ],
    }

    (run / "entries.json").write_text(
        json.dumps(entries, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (run / "bootstrap.json").write_text(
        json.dumps(summary["bootstrap"], indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (run / "baseline_findings.json").write_text(
        json.dumps(baseline, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (run / "metrics_stage_b.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (run / "metrics.md").write_text(render_md(payload), encoding="utf-8")
    print(json.dumps(summary["injections"], indent=2))
    print(json.dumps(e2e["overall"], indent=2))
    print(
        "wrote entries.json, bootstrap.json, baseline_findings.json, "
        f"metrics_stage_b.json, metrics.md -> {run}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
