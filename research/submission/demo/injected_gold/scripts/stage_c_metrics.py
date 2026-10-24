"""Stage C metrics: credited vs target-line, attribution, controls, T1–T15.

Reads the frozen Stage C run artifacts (``plan.json``, ``manifest.jsonl``,
``provenance.json``, ``claims/``, ``controls.jsonl``) and writes:

- ``entries.json`` — per-entry artifact outcome, target-line status, attribution,
  ``none`` sub-flags, and the engine-free claim-form/context label;
- ``bootstrap.json`` — repository-cluster percentile CIs for ``R_credit`` and
  ``R_target`` (10,000 replicates, fixed seed; no Wilson);
- ``baseline_findings.json`` — every baseline ``REFUTED`` claim;
- ``metrics_stage_c.json`` and ``metrics.md`` — tables T1–T15.

The engine is not run here. Wilson intervals are not computed anywhere.

Run::

    PYTHONPATH=src uv run python .../scripts/stage_c_metrics.py \
        --run .../runs/stage-c-2026-10-20 --snapshots .../runs/stage-c-2026-10-20/snapshots
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
import bootstrap_repo_cluster as boot  # noqa: E402
import classify_claim_context as clf  # noqa: E402
import score_injections as scorer  # noqa: E402

INJECTED_GOLD = SCRIPTS.parent
REPO_ROOT = INJECTED_GOLD.parents[3]
OUTCOMES = ("refuted", "nei", "none")
PLANNED = 72


def _read_json(path: Path, default):
    if not path.is_file():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _rate(k: int, n: int) -> float | None:
    return round(k / n, 3) if n else None


def _repo_inputs(
    corpus_dir: Path, repo: str
) -> tuple[frozenset[str], frozenset[str], frozenset[str]]:
    """Engine-free inventory: modules, dependencies, tracked paths."""
    root = corpus_dir / repo
    spec = _read_json(root / "spec.json", {})
    modules: set[str] = set()
    for module in spec.get("modules", []):
        path = str(module.get("path", ""))
        if path.endswith(".py"):
            modules.add(path[:-3].replace("/", "."))
    for init in root.rglob("__init__.py"):
        rel = init.relative_to(root).as_posix()
        modules.add(rel[: -len("/__init__.py")].replace("/", "."))
    dependencies = frozenset(
        str(d.get("name", "")).lower() for d in spec.get("dependencies", []) if d.get("name")
    )
    paths = frozenset(
        p.relative_to(root).as_posix()
        for p in root.rglob("*")
        if p.is_file() and "__pycache__" not in p.parts and not p.name.endswith(".pyc")
    )
    return frozenset(modules), dependencies, paths


def _line_label(
    corpus_dir: Path,
    repo: str,
    doc_path: str,
    line: int | None,
    cache: dict,
) -> tuple[str, str]:
    """Engine-free (claim_form, context_source) for the recorded line."""
    key = (repo, doc_path)
    if key not in cache:
        root = corpus_dir / repo
        modules, deps, paths = _repo_inputs(corpus_dir, repo)
        text_path = root / doc_path
        text = text_path.read_text(encoding="utf-8", errors="ignore") if text_path.is_file() else ""
        cache[key] = clf.classify_document(text, modules=modules, dependencies=deps, paths=paths)
    rows = cache[key]
    if line and 1 <= line <= len(rows):
        row = rows[line - 1]
        return row["claim_form"], row["context_source"]
    return "not_a_claim", "none"


def _artifact_outcome(entry: dict, inj: list[dict], base: list[dict]) -> dict:
    artifact = scorer._match_object(entry)
    new_ref = scorer._new_matching(inj, base, "REFUTED", artifact)
    new_nei = scorer._new_matching(inj, base, "NEI", artifact)
    same = [c for c in inj if scorer.obj_match(c.get("object", ""), artifact)]
    if new_ref:
        outcome = "refuted"
    elif new_nei:
        outcome = "nei"
    else:
        outcome = "none"

    doc_path, line = entry.get("doc_path"), entry.get("line") or 0
    on_line_ref = [c for c in new_ref if c.get("source") == doc_path and scorer.covers(c, line)]
    off_line_ref = [c for c in new_ref if c not in on_line_ref]
    on_line_same = [c for c in same if c.get("source") == doc_path and scorer.covers(c, line)]
    if on_line_ref:
        target_status = "refuted"
    elif any(c.get("code_verdict") == "NEI" for c in on_line_same):
        target_status = "nei"
    else:
        target_status = "none"

    if on_line_ref and off_line_ref:
        attribution = "both"
    elif on_line_ref:
        attribution = "target_line"
    elif off_line_ref:
        attribution = "other_mention"
    else:
        attribution = "target_line"

    def sub(claims: list[dict], line_claims: list[dict]) -> str:
        if any(c.get("code_verdict") == "SUPPORTED" for c in claims):
            return "supported"
        if not claims and line_claims:
            return "other_referent"
        if line_claims and not any(scorer.obj_match(c.get("object", ""), artifact)
                                  for c in line_claims):
            return "other_referent"
        return "no_claim"

    line_claims = [c for c in inj if c.get("source") == doc_path and scorer.covers(c, line)]
    none_sub = sub(same, line_claims) if outcome == "none" else None
    target_sub = (
        sub(
            [c for c in same if c.get("source") == doc_path and scorer.covers(c, line)],
            line_claims,
        )
        if target_status == "none"
        else None
    )
    return {
        "outcome": outcome,
        "target_line_status": target_status,
        "attribution": attribution,
        "outcome_subtype": none_sub,
        "target_line_subtype": target_sub,
    }


def _control_outcome(entry: dict, base: list[dict]) -> str:
    artifact = scorer._match_object(entry)
    doc, line = entry.get("doc_path"), entry.get("line") or 0
    on_line = [
        c for c in base
        if c.get("source") == doc and scorer.covers(c, line)
    ]
    if any(
        c.get("code_verdict") == "REFUTED" and scorer.obj_match(c.get("object", ""), artifact)
        for c in on_line
    ):
        return "refuted"
    if any(
        c.get("code_verdict") == "NEI" and scorer.obj_match(c.get("object", ""), artifact)
        for c in on_line
    ):
        return "nei"
    return "none"


def _control_extracted(entry: dict, base: list[dict]) -> bool:
    line, doc = entry.get("line") or 0, entry.get("doc_path")
    target = str(entry.get("target") or entry.get("symbol") or "").strip().strip("`")
    for claim in base:
        if claim.get("source") != doc or not scorer.covers(claim, line):
            continue
        raw = str(claim.get("raw_context") or "")
        if target and (target.lower() in raw.lower()
                       or scorer.obj_match(claim.get("object", ""), target)):
            return True
    return False


def build_entries(
    manifest: list[dict], claims_by: dict, corpus_dir: Path
) -> list[dict]:
    labels: dict = {}
    out: list[dict] = []
    for entry in manifest:
        repo = entry["repo"]
        cluster = entry.get("repo_name") or repo.split("__", 1)[0]
        inj = claims_by.get((repo, "injected"), [])
        base = claims_by.get((repo, "baseline"), [])
        control = entry.get("control", "none") != "none"
        info = scorer.classify(entry, inj, base)
        form, context = _line_label(corpus_dir, cluster, entry.get("doc_path", ""),
                                    entry.get("line"), labels)
        if control:
            outcome = _control_outcome(entry, base)
            status, attribution, subtype, tsub = outcome, "n/a", None, None
            extracted = _control_extracted(entry, base)
        else:
            result = _artifact_outcome(entry, inj, base)
            outcome = result["outcome"]
            status = result["target_line_status"]
            attribution = result["attribution"]
            subtype = result["outcome_subtype"]
            tsub = result["target_line_subtype"]
            extracted = None
        status_value = entry.get("bundle_status")
        if not status_value:
            status_value = (
                "verified" if (control or entry.get("verifier") == "ok")
                else "verify_failed"
            )
        out.append({
            "repo": cluster,
            "snapshot_id": entry.get("snapshot_id") or repo,
            "class": entry.get("canonical_class"),
            "control": entry.get("control", "none"),
            "control_family": entry.get("control", "none") if control else None,
            "bundle_status": status_value,
            "claim_form": form if form != "not_a_claim" else info.get("claim_form", "bare"),
            "context_source": context,
            "genre": entry.get("genre", "n/a"),
            "target_document": entry.get("target_document", "n/a"),
            "dependency_phrasing": entry.get("dependency_phrasing", "n/a"),
            "dependency_form": entry.get("dependency_form", "n/a"),
            "outcome": outcome,
            "detected": (outcome in ("refuted", "nei")) if not control else None,
            "target_line_status": status,
            "attribution": attribution,
            "outcome_subtype": subtype,
            "target_line_subtype": tsub,
            "extracted": extracted,
            "clean": (outcome != "refuted") if control else None,
            "target": entry.get("target"),
            "doc_path": entry.get("doc_path"),
            "line": entry.get("line"),
            "expected_verdict": entry.get("expected_verdict"),
            "matched": [] if control else [
                {"predicate": c.get("predicate"), "object": c.get("object"),
                 "source": c.get("source"), "line_start": c.get("line_start"),
                 "reason": c.get("code_verdict_reason")}
                for c in scorer._new_matching(inj, base, "REFUTED",
                                              scorer._match_object(entry))
            ],
        })
    return out


def _block(rows: list[dict]) -> dict:
    n = len(rows)
    counts = {o: sum(1 for r in rows if r["outcome"] == o) for o in OUTCOMES}
    target = {o: sum(1 for r in rows if r["target_line_status"] == o) for o in OUTCOMES}
    return {
        "n": n,
        **counts,
        "target_line": target,
        "r_credit": _rate(counts["refuted"], n),
        "r_detect": _rate(sum(1 for r in rows if r.get("detected")), n),
        "r_target": _rate(target["refuted"], n),
        "abstention_rate": _rate(counts["nei"], n),
        "extraction_miss_rate": _rate(counts["none"], n),
        "cross_mention": sum(
            1 for r in rows if r["outcome"] == "refuted" and r["attribution"] == "other_mention"
        ),
        "both": sum(
            1 for r in rows if r["outcome"] == "refuted" and r["attribution"] == "both"
        ),
    }


def summarize(entries: list[dict], design: dict, stats: dict | None = None) -> dict:
    inj = [e for e in entries if e["control"] == "none"]
    ctl = [e for e in entries if e["control"] != "none"]
    overall = _block(inj)
    overall["r_end"] = _rate(sum(1 for e in inj if e["outcome"] == "refuted"), PLANNED)
    overall["bootstrap"] = {
        "r_credit": boot.bootstrap_rate(inj, "outcome", "refuted",
                                        seed=design["seed"]),
        "r_detect": boot.bootstrap_rate(inj, "detected", True,
                                        seed=design["seed"]),
        "r_target": boot.bootstrap_rate(inj, "target_line_status", "refuted",
                                        seed=design["seed"]),
    }

    def breakdown(field: str) -> dict:
        out = {}
        for value in sorted({str(e.get(field, "n/a")) for e in inj}):
            rows = [e for e in inj if str(e.get(field, "n/a")) == value]
            block = _block(rows)
            out[value] = block
        return out

    by_class = breakdown("class")
    for cls, block in by_class.items():
        # Operator KPI (2026-10-21): a refutation found anywhere in the
        # baseline->injected diff is a detection. Target-line status is an
        # attribution diagnostic, not a pass/fail criterion.
        block["primary"] = "R_credit"
        block["both"] = sum(
            1 for e in inj if e["class"] == cls and e["attribution"] == "both"
        )
    controls = {}
    for family in sorted({e["control_family"] for e in ctl}):
        rows = [e for e in ctl if e["control_family"] == family]
        evaluated = [e for e in rows if e["bundle_status"] == "verified"]
        extracted = [e for e in evaluated if e["extracted"]]
        refuted = [e for e in evaluated if e["outcome"] == "refuted"]
        controls[family] = {
            "required": _control_config(design).get("families", {})
            .get(family, {}).get("required"),
            "evaluated": len(evaluated),
            "dropped": len(rows) - len(evaluated),
            "extracted": len(extracted),
            "refuted": len(refuted),
            "specificity": _rate(len(evaluated) - len(refuted), len(evaluated)),
            "precision_extracted": _rate(len(extracted) - len(
                [e for e in extracted if e["outcome"] == "refuted"]
            ), len(extracted)),
            "extraction_rate": _rate(len(extracted), len(evaluated)),
            "false_positives": [
                {"repo": e["repo"], "doc_path": e["doc_path"], "line": e["line"],
                 "target": e["target"], "claim_form": e["claim_form"],
                 "context_source": e["context_source"]}
                for e in refuted
            ],
            "shortfall": max(
                0,
                (_control_config(design).get("families", {})
                 .get(family, {}).get("required") or 0) - len(evaluated),
            ),
        }
    for family in _control_config(design).get("families", {}):
        if family in controls:
            continue
        required = _control_config(design)["families"][family].get("required")
        controls[family] = {
            "required": required,
            "evaluated": 0,
            "dropped": 0,
            "extracted": 0,
            "refuted": 0,
            "specificity": None,
            "precision_extracted": None,
            "extraction_rate": None,
            "false_positives": [],
            "shortfall": required or 0,
            "not_applicable": family == "C",
        }
    statuses = Counter(e["bundle_status"] for e in entries if e["control"] == "none")
    distinct = defaultdict(set)
    for e in inj:
        distinct[e["class"]].add((e["repo"], str(e.get("target") or "")))
    seed_collapse = defaultdict(int)
    for e in inj:
        seed_collapse[e["class"]] += 1
    groups: dict[str, dict[tuple[str, str], int]] = defaultdict(dict)
    for e in inj:
        key = (e["repo"], str(e.get("target") or ""))
        groups[e["class"]][key] = groups[e["class"]].get(key, 0) + 1
    ess = {
        cls: {
            "entries": seed_collapse[cls],
            "distinct_repo_artifact": len(distinct[cls]),
            "collapsed_targets": sum(1 for n in groups[cls].values() if n > 1),
            "collapsed_entries": sum(n for n in groups[cls].values() if n > 1),
        }
        for cls in sorted(seed_collapse)
    }
    return {
        "kpi": {
            "definition": (
                "detection = a same-artifact REFUTED finding anywhere in the "
                "baseline->injected diff, OR a same-artifact NEI. NEI is an "
                "explicit abstention with a mention, not silence, and counts as "
                "caught. none (no claim / wrong SUPPORTED / other referent) is a "
                "miss; R_credit counts REFUTED only."
            ),
            "primary": "R_detect",
            "secondary": "R_credit",
            "diagnostic": "R_target",
            "decided": "2026-10-21, operator decision after scoring; see deviations.md",
        },
        "injections": overall,
        "controls": controls,        "control_overall": {
            "evaluated": sum(c["evaluated"] for c in controls.values()),
            "refuted": sum(c["refuted"] for c in controls.values()),
            "specificity": _rate(
                sum(c["evaluated"] for c in controls.values())
                - sum(c["refuted"] for c in controls.values()),
                sum(c["evaluated"] for c in controls.values()),
            ),
        },
        "by_class": by_class,
        "by_claim_form": breakdown("claim_form"),
        "by_context_source": breakdown("context_source"),
        "by_genre": breakdown("genre"),
        "by_target_document": breakdown("target_document"),
        "by_dependency_phrasing": breakdown("dependency_phrasing"),
        "by_dependency_form": breakdown("dependency_form"),
        "by_repo": breakdown("repo"),
        "none_subtypes": dict(sorted(Counter(
            e["outcome_subtype"] for e in inj if e["outcome"] == "none"
        ).items())),
        "target_line_none_subtypes": dict(sorted(Counter(
            e["target_line_subtype"] for e in inj if e["target_line_status"] == "none"
        ).items())),
        "attribution": dict(sorted(Counter(
            e["attribution"] for e in inj if e["outcome"] == "refuted"
        ).items())),
        "end_to_end": {
            "planned": (stats or {}).get("planned", PLANNED),
            "verified": (stats or {}).get("overall", {}).get(
                "verified", sum(1 for e in inj if e["bundle_status"] == "verified")
            ),
            **{status: (stats or {}).get("overall", {}).get(status, statuses.get(status, 0))
               for status in (
                   "declined", "invalid", "verify_failed", "apply_failed", "timeout",
                   "no_output", "unresolved", "conflict",
               )},
            "refuted": overall["refuted"],
        },
        "effective_sample_size": ess,
        "annotation": {"status": "pending", "n": 0},
        "deviations": ["see deviations.md"],
    }


def _control_config(design: dict) -> dict:
    run = Path(design["_run"])
    return _read_json(run / "control_config.json", {})


def baseline_findings(claims_by: dict, corpus_dir: Path) -> list[dict]:
    out: list[dict] = []
    for (repo, kind), claims in sorted(claims_by.items()):
        if kind != "baseline" or repo.endswith("__control"):
            continue
        repo_name = repo.split("__", 1)[0]
        for claim in claims:
            if claim.get("code_verdict") != "REFUTED":
                continue
            out.append({
                "repo": repo_name,
                "predicate": claim.get("predicate"),
                "object": claim.get("object"),
                "doc_path": claim.get("source"),
                "line": claim.get("line_start"),
                "reason": claim.get("code_verdict_reason"),
                "adjudication": "undetermined",
            })
    return out


def _fmt(value) -> str:
    return "n/a" if value is None else str(value)


def render_md(payload: dict) -> str:
    lines = [
        "# Stage C metrics",
        "",
        "**KPI: `R_detect` — REFUTED or NEI on the same artifact counts as "
        "caught.** NEI is an explicit abstention with a mention, not silence; "
        "`none` (no claim / wrong SUPPORTED / other referent) is a miss. "
        "`R_credit` is REFUTED only; `R_target` is an attribution diagnostic. "
        "No Wilson interval is used.",
        "",
        "## T2 — overall",
        "",
        "| verified | detected (REFUTED+NEI) | R_detect (KPI) [CI] | REFUTED "
        "(R_credit) | NEI | none | R_target (attribution) [CI] |",
        "|---|---|---|---|---|---|---|",
    ]
    i = payload["injections"]
    bd = i["bootstrap"].get("r_detect") or {}
    bt = i["bootstrap"]["r_target"]
    lines.append(
        f"| {i['n']} | {i['refuted'] + i['nei']} | "
        f"{_fmt(i['r_detect'])} {bd.get('ci95', '')} | {i['refuted']} "
        f"({_fmt(i['r_credit'])}) | {i['nei']} | {i['none']} | "
        f"{_fmt(i['r_target'])} {bt['ci95'] if bt else ''} |"
    )
    for title, key in (
        ("T3 — class", "by_class"),
        ("T4 — claim form", "by_claim_form"),
        ("T5 — context source", "by_context_source"),
        ("T6 — genre", "by_genre"),
        ("T7 — target document", "by_target_document"),
        ("T8 — dependency phrasing", "by_dependency_phrasing"),
        ("T8 — dependency form", "by_dependency_form"),
        ("T7 — repo", "by_repo"),
    ):
        lines += ["", f"## {title}", "",
                  "| value | n | detected | R_detect (KPI) | refuted | NEI | none | "
                  "R_credit | R_target | cross-mention |",
                  "|---|---|---|---|---|---|---|---|---|---|"]
        for value, block in payload[key].items():
            lines.append(
                f"| {value} | {block['n']} | {block['refuted'] + block['nei']} | "
                f"{_fmt(block['r_detect'])} | {block['refuted']} | {block['nei']} | "
                f"{block['none']} | {_fmt(block['r_credit'])} | {_fmt(block['r_target'])} | "
                f"{block.get('cross_mention', 0)} |"
            )
        if key == "by_class":
            lines += [
                "",
                "Every class is scored on `R_detect` (KPI: REFUTED + NEI). NEI is "
                "an explicit abstention with a mention and counts as caught; "
                "`none` (no claim / wrong SUPPORTED / other referent) is a miss. "
                "`R_target` is attribution only.",
            ]
    lines += ["", "## T9 — end-to-end statuses", "",
              "| planned | verified | declined | invalid | verify_failed | apply_failed | "
              "timeout | no_output | unresolved | conflict | refuted |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
    e = payload["end_to_end"]
    lines.append("| " + " | ".join(str(e[k]) for k in (
        "planned", "verified", "declined", "invalid", "verify_failed", "apply_failed",
        "timeout", "no_output", "unresolved", "conflict", "refuted")) + " |")
    lines += ["", "## T10 — credited detection × target-line attribution", "",
              "| class | credited refuted (KPI) | target-line refuted (attribution) | "
              "other-mention-only | both |",
              "|---|---|---|---|---|"]
    for cls, block in payload["by_class"].items():
        other = block["cross_mention"]
        both = block.get("both", 0)
        lines.append(f"| {cls} | {block['refuted']} | {block['target_line']['refuted']} | "
                     f"{other} | {both} |")
    lines += ["", "## T11 — controls", "",
              "| family | required | evaluated | dropped | shortfall | extracted | refuted | "
              "specificity | precision (extracted) | extraction |",
              "|---|---|---|---|---|---|---|---|---|---|"]
    for family, c in payload["controls"].items():
        lines.append(
            f"| {family} | {_fmt(c['required'])} | {c['evaluated']} | {c['dropped']} | "
            f"{_fmt(c.get('shortfall'))} | {c['extracted']} | {c['refuted']} | "
            f"{_fmt(c['specificity'])} | {_fmt(c['precision_extracted'])} | "
            f"{_fmt(c['extraction_rate'])} |"
        )
    lines += ["", "## T13 — effective sample size", "",
              "| class | entries | distinct (repo, artifact) | collapsed targets | "
              "collapsed entries |",
              "|---|---|---|---|---|"]
    for cls, row in payload["effective_sample_size"].items():
        lines.append(f"| {cls} | {row['entries']} | {row['distinct_repo_artifact']} | "
                     f"{row['collapsed_targets']} | {row['collapsed_entries']} |")
    lines += [
        "", "## T12 — baseline findings", "",
        f"{len(payload['baseline_findings'])} baseline `REFUTED` claim(s); "
        "adjudication pending (see baseline_findings.json).",
        "", "## T14 — annotation", "",
        "Pending: no non-author annotator at sign-off (OPEN-C9). Engine-only provisional.",
        "", "## T15 — deviations", "",
    ]
    lines += [f"- {d}" for d in payload["deviations"]] or ["None recorded."]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run", required=True)
    ap.add_argument("--design", default="")
    ap.add_argument("--corpus-dir", default="")
    ap.add_argument("--replicates", type=int, default=10000)
    args = ap.parse_args(argv)
    run = Path(args.run).resolve()
    design = _read_json(Path(args.design) if args.design else run / "corpus_design.json", {})
    design["_run"] = str(run)
    corpus = Path(args.corpus_dir) if args.corpus_dir else Path(design["corpus_dir"])
    if not corpus.is_absolute():
        corpus = REPO_ROOT / corpus
    manifest_path = run / "scoring_manifest.jsonl"
    if not manifest_path.is_file():
        manifest_path = run / "manifest.jsonl"
    manifest = _read_jsonl(manifest_path)
    stats = _read_json(run / "stats.json", {})
    claims_dir = run / "claims"
    claims_by: dict[tuple[str, str], list[dict]] = {}
    if claims_dir.is_dir():
        for path in sorted(claims_dir.glob("*.jsonl")):
            kind = "injected" if path.stem.endswith("__injected") else "baseline"
            suffix = "__injected" if kind == "injected" else "__baseline"
            snapshot = path.stem[: -len(suffix)]
            claims_by[(snapshot, kind)] = _read_jsonl(path)
    entries = build_entries(manifest, claims_by, corpus)
    payload = summarize(entries, design, stats)
    payload["baseline_findings"] = baseline_findings(claims_by, corpus)
    (run / "entries.json").write_text(json.dumps(entries, indent=2) + "\n", encoding="utf-8")
    (run / "bootstrap.json").write_text(
        json.dumps(payload["injections"]["bootstrap"], indent=2) + "\n", encoding="utf-8"
    )
    (run / "baseline_findings.json").write_text(
        json.dumps(payload["baseline_findings"], indent=2) + "\n", encoding="utf-8"
    )
    (run / "metrics_stage_c.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )
    (run / "metrics.md").write_text(render_md(payload), encoding="utf-8")
    print(f"wrote entries.json, bootstrap.json, baseline_findings.json, metrics_stage_c.json, "
          f"metrics.md ({len(entries)} entries)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
