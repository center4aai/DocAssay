"""Agreement for the Stage C LLM annotation arm (supplementary).

Reads the blind sheet, the three annotator output directories, and the frozen
entries/key. Reports, per field: Fleiss' kappa (3 raters, nominal), percent
agreement, pairwise Cohen's kappa, majority-label counts, and the KPI-relevant
checks (are the injected defects real, are the controls true, is the NEI
abstention legitimate, are the `none` rows genuine misses).

This is an **LLM** arm: supplementary confirmation; no IAA is claimed. It is reported as
supplementary, never as external validation.

Run::

    PYTHONPATH=src uv run python .../scripts/annotation_agreement.py \
        --run .../runs/stage-c-2026-10-20
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

FIELDS = (
    "claim_type",
    "claim_form",
    "context_source",
    "defect_is_real",
    "nei_reason_applies",
    "none_claim_not_extracted",
    "control_false_positive",
    "same_artifact",
)
ALLOWED = {
    "claim_type": {"current_claim", "historical", "illustrative", "conditional", "not_a_claim"},
    "claim_form": {"path", "dependency", "qualified", "section_qualified", "bare_call",
                   "bare", "not_a_claim"},
    "context_source": {"heading", "table", "prose", "list", "path_prose", "none"},
    "defect_is_real": {"yes", "no", "n/a"},
    "nei_reason_applies": {"yes", "no", "n/a"},
    "none_claim_not_extracted": {"yes", "no", "n/a"},
    "control_false_positive": {"yes", "no", "n/a"},
    "same_artifact": {"yes", "no", "unsure", "n/a"},
}


def _read_jsonl(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()]


def _norm(value) -> str:
    text = str(value or "").strip().lower()
    if text in {"na", "n.a.", "none", ""}:
        return "n/a" if text != "none" else "none"
    return text


def _fleiss(items: list[list[str]], categories: list[str]) -> float | None:
    n_items = len(items)
    if not n_items:
        return None
    n_raters = len(items[0])
    if n_raters < 2:
        return None
    p_i = []
    for ratings in items:
        counts = Counter(ratings)
        total = sum(counts[c] ** 2 for c in categories)
        p_i.append((total - n_raters) / (n_raters * (n_raters - 1)))
    p_bar = sum(p_i) / n_items
    p_e = 0.0
    for category in categories:
        share = sum(Counter(ratings)[category] for ratings in items) / (n_items * n_raters)
        p_e += share ** 2
    if p_e == 1:
        return None
    return round((p_bar - p_e) / (1 - p_e), 4)


def _cohen(a: list[str], b: list[str]) -> float | None:
    n = len(a)
    if not n:
        return None
    po = sum(1 for x, y in zip(a, b, strict=True) if x == y) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum((ca[k] / n) * (cb[k] / n) for k in set(ca) | set(cb))
    if pe == 1:
        return None
    return round((po - pe) / (1 - pe), 4)


def _majority(ratings: list[str]) -> str:
    counts = Counter(ratings)
    top = counts.most_common()
    if len(top) > 1 and top[0][1] == top[1][1]:
        return "tie"
    return top[0][0]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run", required=True)
    args = ap.parse_args(argv)
    run = Path(args.run).resolve()

    sheet = _read_jsonl(run / "annotation_sheet.jsonl")
    key = {r["mention_id"]: r for r in _read_jsonl(run / "annotation_sheet_key.jsonl")}
    model_dirs = sorted(p for p in (run / "annotations").iterdir() if p.is_dir())
    if len(model_dirs) < 2:
        print("need at least two annotator directories", file=sys.stderr)
        return 2
    models = [p.name for p in model_dirs]
    by_model: dict[str, dict[str, dict]] = {}
    coverage = {}
    for directory in model_dirs:
        rows = {}
        for path in sorted(directory.glob("*.jsonl")):
            for row in _read_jsonl(path):
                rows[row["mention_id"]] = row
        by_model[directory.name] = rows
        coverage[directory.name] = len(rows)

    missing = {m: len(set(r["mention_id"] for r in sheet) - set(by_model[m])) for m in models}
    invalid: list[str] = []
    for model in models:
        for mid, row in by_model[model].items():
            for field in FIELDS:
                value = _norm(row.get(field))
                if field == "same_artifact" and value == "none":
                    continue
                if value not in ALLOWED[field]:
                    invalid.append(f"{model}/{mid}/{field}={value!r}")

    agreement: dict[str, dict] = {}
    majority: dict[str, dict] = {}
    for field in FIELDS:
        items = []
        per_model = {m: [] for m in models}
        for row in sheet:
            mid = row["mention_id"]
            ratings = [_norm(by_model[m].get(mid, {}).get(field)) for m in models]
            items.append(ratings)
            for m, value in zip(models, ratings, strict=True):
                per_model[m].append(value)
        categories = sorted({v for ratings in items for v in ratings})
        pairwise = {}
        for i, m1 in enumerate(models):
            for m2 in models[i + 1:]:
                pairwise[f"{m1} vs {m2}"] = _cohen(per_model[m1], per_model[m2])
        all_agree = sum(1 for ratings in items if len(set(ratings)) == 1)
        agreement[field] = {
            "fleiss_kappa": _fleiss(items, categories),
            "percent_agreement": round(all_agree / len(items), 4) if items else None,
            "pairwise_cohen": pairwise,
            "category_counts": dict(sorted(Counter(
                _majority(r) for r in items
            ).items())),
            "invalid_values": [v for v in invalid if f"/{field}=" in v],
        }
        majority[field] = dict(sorted(Counter(_majority(r) for r in items).items()))

    entries = {e["snapshot_id"]: e for e in
               (json.loads((run / "entries.json").read_text(encoding="utf-8"))
                if (run / "entries.json").is_file() else [])}
    checks = {
        "injection_defect_real_yes": 0,
        "injection_defect_real_no": 0,
        "injection_defect_real_na": 0,
        "control_true_yes": 0,
        "control_false_positive_no": 0,
        "nei_legitimate_yes": 0,
        "nei_legitimate_no": 0,
        "none_is_miss_no": 0,
        "none_is_miss_yes": 0,
    }
    for row in sheet:
        mid = row["mention_id"]
        verdicts = {m: _norm(by_model[m].get(mid, {}).get("defect_is_real")) for m in models}
        votes = Counter(verdicts.values())
        majority_defect = votes.most_common(1)[0][0] if votes else "n/a"
        if row.get("is_control"):
            cfp = Counter(_norm(by_model[m].get(mid, {}).get("control_false_positive"))
                          for m in models)
            if cfp and cfp.most_common(1)[0][0] == "yes":
                checks["control_true_yes"] += 1
            elif cfp and cfp.most_common(1)[0][0] == "no":
                checks["control_false_positive_no"] += 1
            continue
        if majority_defect == "yes":
            checks["injection_defect_real_yes"] += 1
        elif majority_defect == "no":
            checks["injection_defect_real_no"] += 1
        else:
            checks["injection_defect_real_na"] += 1

        info = key.get(mid, {})
        entry = entries.get(info.get("snapshot_id")) if info.get("snapshot_id") else None
        if entry and entry.get("control") != "none":
            entry = None
        if entry and entry.get("outcome") == "nei":
            votes = Counter(_norm(by_model[m].get(mid, {}).get("nei_reason_applies"))
                            for m in models)
            if votes and votes.most_common(1)[0][0] == "yes":
                checks["nei_legitimate_yes"] += 1
            elif votes and votes.most_common(1)[0][0] == "no":
                checks["nei_legitimate_no"] += 1
        if entry and entry.get("outcome") == "none":
            votes = Counter(_norm(by_model[m].get(mid, {}).get("none_claim_not_extracted"))
                            for m in models)
            if votes and votes.most_common(1)[0][0] == "no":
                checks["none_is_miss_no"] += 1
            elif votes and votes.most_common(1)[0][0] == "yes":
                checks["none_is_miss_yes"] += 1

    refuted = sum(1 for e in entries.values()
                  if e.get("control") == "none" and e.get("outcome") == "refuted")
    verified = sum(1 for e in entries.values() if e.get("control") == "none")
    adjusted = refuted + checks["nei_legitimate_yes"]
    payload = {
        "arm": "LLM annotation (supplementary confirmation)",
        "annotators": models,
        "rows": len(sheet),
        "coverage": coverage,
        "missing": missing,
        "invalid_values": invalid[:50],
        "agreement": agreement,
        "majority": majority,
        "kpi_checks": checks,
        "sensitivity": {
            "operator_kpi": "REFUTED + every NEI",
            "operator_detect": refuted + sum(
                1 for e in entries.values()
                if e.get("control") == "none" and e.get("outcome") == "nei"
            ),
            "llm_validated_nei_only": adjusted,
            "refuted": refuted,
            "nei_legitimate_yes": checks["nei_legitimate_yes"],
            "nei_legitimate_no": checks["nei_legitimate_no"],
            "verified": verified,
            "llm_adjusted_r_detect": round(adjusted / verified, 4) if verified else None,
        },
    }
    (run / "annotation_agreement.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )
    _render_md(run / "annotation_agreement.md", payload)
    print(f"wrote annotation_agreement.json/.md ({len(models)} annotators, {len(sheet)} rows)")
    return 0


def _render_md(path: Path, payload: dict) -> None:
    lines = [
        "# Stage C — LLM annotation arm (supplementary)",
        "",
        "**LLM annotation (supplementary confirmation).** Three LLM annotators label the blind",
        "sheet; the report is provisional.",
        "",
        f"- annotators: {', '.join(payload['annotators'])}",
        f"- rows: {payload['rows']}",
        f"- coverage: {payload['coverage']}",
        "",
        "| field | Fleiss κ | % agreement | pairwise Cohen | majority |",
        "|---|---:|---:|---|---|",
    ]
    for field, row in payload["agreement"].items():
        pairwise = "; ".join(f"{k}: {v}" for k, v in row["pairwise_cohen"].items())
        lines.append(
            f"| {field} | {row['fleiss_kappa']} | {row['percent_agreement']} | "
            f"{pairwise} | {row['category_counts']} |"
        )
    lines += [
        "",
        "## KPI checks (majority label)",
        "",
        "| check | count |",
        "|---|---:|",
    ]
    for key, value in payload["kpi_checks"].items():
        lines.append(f"| {key} | {value} |")
    lines += [
        "",
        "## Sensitivity: NEI legitimacy",
        "",
        f"- operator KPI (REFUTED + every NEI): {payload['sensitivity']['operator_detect']}"
        f"/{payload['sensitivity']['verified']}",
        f"- LLM-validated (REFUTED + legitimate NEI): "
        f"{payload['sensitivity']['llm_validated_nei_only']}"
        f"/{payload['sensitivity']['verified']} = "
        f"{payload['sensitivity']['llm_adjusted_r_detect']}",
        f"- NEI legitimate: {payload['sensitivity']['nei_legitimate_yes']}; "
        f"not legitimate: {payload['sensitivity']['nei_legitimate_no']}",
        "",
        "A κ near 0 means the LLM annotators do not reproduce each other; it is",
        "reported, not hidden. This arm is supplementary confirmation only.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
