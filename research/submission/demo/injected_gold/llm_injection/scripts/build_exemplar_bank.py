"""Build the few-shot exemplar bank for source-grounded LLM injection.

This is the bank stage of ``../../validation/protocol.md`` §2: mine the
**human-triaged real incidents** (READU true positives, plus a small manually
commit-verified harvest for the thin classes) and assign each to one of the four
predicate-backed, in-scope canonical classes with a frozen, engine-free keyword
ruleset (``exemplars/rules.json``). The READU commit-prefilter
``potential_readme_bug_scenarios`` (LLM-derived hypotheses) are collected into a
**separate, labelled pool** and are never merged into the triaged primary bank
(``protocol.md`` §2). READU false positives are collected into a ``controls``
pool (negative exemplars).

Everything is standard-library only and deterministic: the engine is never
imported, and the output is a byte-stable function of the source files and the
frozen ruleset.

Run::

    PYTHONPATH=src uv run python .../llm_injection/scripts/build_exemplar_bank.py
    PYTHONPATH=src uv run python .../llm_injection/scripts/build_exemplar_bank.py --check
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
EXEMPLARS = HERE.parents[1] / "exemplars"
DEFAULT_RULES = EXEMPLARS / "rules.json"
DEFAULT_OUT = EXEMPLARS / "bank.json"
DEFAULT_MD = EXEMPLARS / "bank.md"
EVIDENCE = EXEMPLARS / "evidence"
CURATED = EXEMPLARS / "sources" / "curated_triaged.json"

EMDASH = "\u2014"
_ENTRY_RE = re.compile(r"^### `(?P<repo>[^`]+)` " + re.escape(EMDASH) + r" `(?P<alert>[^`]+)`\s*$")
_THEME_RE = re.compile(r"^## (?P<theme>.+?) \((\d+)\)\s*$")
_FIELD_RE = re.compile(r"^-\s*(?P<key>[A-Za-z ]+):\s*(?P<value>.*)$")

_THEME_SKIP = {"Summary"}
_RAW_FIELD = {
    "Commit": "commit_url",
    "Checker": "checker",
    "Technique": "technique",
    "Location": "location",
    "Alert": "quote",
    "Triage note": "triage_note",
}


def _find_root(start: Path) -> Path:
    for parent in (start, *start.parents):
        if (parent / "pyproject.toml").is_file():
            return parent
    raise SystemExit("repository root not found")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


# --------------------------------------------------------------------------- #
# ruleset
# --------------------------------------------------------------------------- #
def load_rules(path: Path) -> dict:
    return json.loads(_read(path))


def _classify(text: str, rules: dict) -> tuple[str | None, str | None]:
    """First class in precedence whose rule matches; returns (class, rule_id)."""
    for cls in rules["precedence"]:
        rule = rules["rules"][cls]
        if "all_of" in rule and not all(re.search(p, text, re.I) for p in rule["all_of"]):
            continue
        if "any_of" in rule and not any(re.search(p, text, re.I) for p in rule["any_of"]):
            continue
        if "none_of" in rule and any(re.search(p, text, re.I) for p in rule["none_of"]):
            continue
        return cls, cls
    return None, None


# --------------------------------------------------------------------------- #
# READU themed alert files (READU_tp.md / READU_fp.md)
# --------------------------------------------------------------------------- #
def parse_alert_file(path: Path) -> list[dict]:
    """Parse ``### `repo` — `alert``` blocks under ``## Theme (N)`` headers."""
    entries: list[dict] = []
    theme: str | None = None
    current: dict | None = None
    for line in _read(path).splitlines():
        theme_m = _THEME_RE.match(line)
        if theme_m:
            theme = theme_m.group("theme")
            current = None
            continue
        entry_m = _ENTRY_RE.match(line)
        if entry_m:
            current = {
                "repo": entry_m.group("repo"),
                "alert_id": entry_m.group("alert"),
                "theme": theme,
            }
            entries.append(current)
            continue
        if current is None:
            continue
        field_m = _FIELD_RE.match(line)
        if field_m:
            key = field_m.group("key").strip()
            if key in _RAW_FIELD:
                current[_RAW_FIELD[key]] = field_m.group("value").strip()
    return entries


def _load_evidence(evidence_dir: Path, exemplar_id: str) -> dict | None:
    """Extracted before/after evidence for a triaged exemplar, if present.

    Written by ``fetch_exemplar_evidence.py`` (the one-time network step) and
    committed, so the bank build itself stays offline and deterministic.
    """
    path = evidence_dir / f"{exemplar_id.replace(':', '__')}.json"
    if not path.is_file():
        return None
    return json.loads(_read(path))


def triaged_exemplars(path: Path, rules: dict, evidence_dir: Path) -> tuple[list[dict], dict]:
    """Classified human-triaged true positives -> primary bank + gap tally."""
    out: list[dict] = []
    gaps: dict[str, int] = {}
    sources: dict[str, int] = {}
    evidence_ok = 0
    for e in parse_alert_file(path):
        quote = e.get("quote", "")
        cls, rule_id = _classify(quote, rules)
        if cls is None:
            gaps["unclassified"] = gaps.get("unclassified", 0) + 1
            continue
        sources[e.get("theme", "?")] = sources.get(e.get("theme", "?"), 0) + 1
        exemplar_id = f"triaged:{e['alert_id']}"
        evidence = _load_evidence(evidence_dir, exemplar_id)
        if evidence and evidence.get("status") == "ok" and evidence.get("files"):
            evidence_ok += 1
        out.append(
            {
                "id": exemplar_id,
                "pool": "triaged",
                "label": e.get("theme"),
                "repo": e.get("repo"),
                "commit_url": e.get("commit_url"),
                "location": e.get("location"),
                "quote": quote,
                "matched_rule": rule_id,
                "evidence": evidence,
            }
        )
    out.sort(key=lambda x: x["id"])
    return out, {
        "unclassified": gaps.get("unclassified", 0),
        "by_theme": sources,
        "evidence_ok": evidence_ok,
    }


def curated_exemplars(path: Path, rules: dict, evidence_dir: Path) -> tuple[list[dict], dict]:
    """Manually harvested, commit-verified real incidents -> triaged bank.

    The source is an additive triaged layer (never the raw LLM-hypothesis pool).
    Every row is classified by the same frozen ruleset; a declared mismatch is a
    hard error so a curated row can never silently land in the wrong class.
    """
    if not path.is_file():
        return [], {"evidence_ok": 0, "curated": 0}
    data = json.loads(_read(path))
    out: list[dict] = []
    evidence_ok = 0
    for item in sorted(data.get("incidents", []), key=lambda x: x["id"]):
        quote = item.get("quote", "")
        cls, rule_id = _classify(quote, rules)
        expected = item.get("expected_class")
        if cls is None:
            raise SystemExit(f"curated exemplar {item['id']!r} is unclassified by {path}")
        if expected and cls != expected:
            raise SystemExit(
                f"curated exemplar {item['id']!r} classified as {cls!r}, expected {expected!r}"
            )
        exemplar_id = f"triaged:{item['id']}"
        evidence = _load_evidence(evidence_dir, exemplar_id)
        if evidence and evidence.get("status") == "ok" and evidence.get("files"):
            evidence_ok += 1
        out.append(
            {
                "id": exemplar_id,
                "pool": "triaged",
                "label": item.get("label", "curated_external_real_incident"),
                "repo": item.get("repo"),
                "commit_url": item.get("commit_url"),
                "location": item.get("location"),
                "quote": quote,
                "matched_rule": rule_id,
                "evidence": evidence,
                "triage_note": item.get("triage_note", ""),
            }
        )
    return out, {"evidence_ok": evidence_ok, "curated": len(out)}


def control_exemplars(path: Path, rules: dict) -> list[dict]:
    """Human-triaged false positives -> controls pool (negative exemplars)."""
    out: list[dict] = []
    for e in parse_alert_file(path):
        out.append(
            {
                "id": f"control:{e['alert_id']}",
                "pool": "controls",
                "label": e.get("theme"),
                "repo": e.get("repo"),
                "commit_url": e.get("commit_url"),
                "location": e.get("location"),
                "quote": e.get("quote", ""),
                "triage_note": e.get("triage_note", ""),
            }
        )
    out.sort(key=lambda x: x["id"])
    return out


# --------------------------------------------------------------------------- #
# readu_raw commit-prefilter hypotheses (separate pool)
# --------------------------------------------------------------------------- #
def raw_exemplars(dataset_dir: Path, rules: dict) -> tuple[list[dict], dict]:
    out: list[dict] = []
    gaps = {"unclassified": 0}
    for path in sorted(dataset_dir.glob("*.json")):
        data = json.loads(_read(path))
        repo = data.get("repository")
        for commit in data.get("commits", []) or []:
            commit_hash = commit.get("hash")
            url = (
                f"https://github.com/{repo}/commit/{commit_hash}" if repo and commit_hash else None
            )
            for res in commit.get("pre_filter", {}).get("llm_results", []) or []:
                scenarios = res.get("potential_readme_bug_scenarios", []) or []
                for i, scen in enumerate(scenarios):
                    text = scen if isinstance(scen, str) else json.dumps(scen, ensure_ascii=False)
                    cls, rule_id = _classify(text, rules)
                    if cls is None:
                        gaps["unclassified"] += 1
                        continue
                    raw_id = (
                        f"raw:{repo}:{commit_hash}:{i}" if commit_hash else f"raw:{path.stem}:{i}"
                    )
                    out.append(
                        {
                            "id": raw_id,
                            "pool": "raw",
                            "label": "readu_raw:potential_readme_bug_scenarios",
                            "repo": repo,
                            "commit_url": url,
                            "location": None,
                            "quote": text,
                            "matched_rule": rule_id,
                        }
                    )
    out.sort(key=lambda x: x["id"])
    return out, gaps


# --------------------------------------------------------------------------- #
# assembly
# --------------------------------------------------------------------------- #
def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_bank(root: Path, rules_path: Path, evidence_dir: Path = EVIDENCE) -> dict:
    rules = load_rules(rules_path)
    readu = root / "other_instruments" / "readu" / "data"
    tp = readu / "analysis" / "READU_tp.md"
    fp = readu / "analysis" / "READU_fp.md"
    dataset = readu / "dataset"

    readu_triaged, readu_meta = triaged_exemplars(tp, rules, evidence_dir)
    curated, curated_meta = curated_exemplars(CURATED, rules, evidence_dir)
    triaged = sorted(readu_triaged + curated, key=lambda x: x["id"])
    triaged_meta = {
        "evidence_ok": readu_meta["evidence_ok"] + curated_meta["evidence_ok"],
        "unclassified": readu_meta["unclassified"],
        "by_source": {"readu": len(readu_triaged), "curated": len(curated)},
    }
    raw, raw_meta = raw_exemplars(dataset, rules)
    controls = control_exemplars(fp, rules)

    classes: dict[str, dict] = {}
    for cls, meta in rules["target_classes"].items():
        members = [e for e in triaged if e["matched_rule"] == cls]
        raw_members = [e for e in raw if e["matched_rule"] == cls]
        classes[cls] = {
            "artifact_class": meta["artifact_class"],
            "predicate": meta["predicate"],
            "unit": meta["unit"],
            "exemplar_count": len(members) + len(raw_members),
            "triaged": members,
            "raw": raw_members,
        }

    gaps = [cls for cls, body in classes.items() if body["exemplar_count"] == 0]

    def rel(p: Path) -> str:
        return str(p.relative_to(root))

    bank = {
        "schema_version": "1.0",
        "bank_id": "llm_injection.exemplars",
        "generated_by": rel(HERE),
        "generated_from": {
            "ruleset": rel(rules_path),
            "ruleset_sha256": _sha256(rules_path),
            "ruleset_version": rules["version"],
            "curated_source": rel(CURATED) if CURATED.is_file() else None,
            "curated_sha256": _sha256(CURATED) if CURATED.is_file() else None,
            "evidence_dir": rel(evidence_dir),
        },
        "pools": {
            "triaged": {
                "kind": "human_triaged_true_positive",
                "source": rel(tp),
                "curated_source": rel(CURATED) if CURATED.is_file() else None,
                "note": (
                    "READU post-judge true positives plus a small, manually commit-verified "
                    "harvest of real project-version and symbol-rename incidents. Primary bank; "
                    "never merged with raw or controls."
                ),
            },
            "raw": {
                "kind": "llm_hypotheses",
                "source": rel(dataset),
                "note": (
                    "readu_raw prefilter potential_readme_bug_scenarios. A separate, "
                    "clearly labelled pool; never mixed into 'triaged' (protocol.md §2)."
                ),
            },
            "controls": {
                "kind": "human_triaged_false_positive",
                "source": rel(fp),
                "note": "READU false positives, grouped by triage reason. Negative exemplars.",
            },
        },
        "counts": {
            "triaged": len(triaged),
            "raw": len(raw),
            "controls": len(controls),
            "triaged_with_evidence": triaged_meta["evidence_ok"],
            "triaged_by_source": triaged_meta["by_source"],
            "unclassified_triaged": triaged_meta["unclassified"],
            "unclassified_raw": raw_meta["unclassified"],
            "per_class": {cls: body["exemplar_count"] for cls, body in classes.items()},
            "per_class_triaged": {cls: len(body["triaged"]) for cls, body in classes.items()},
        },
        "coverage_note": (
            "Deterministic keyword assignment over READU remains thin and noisy; the thin "
            "classes are topped up by a small curated source of real public commits whose "
            "parent tree already carried the renamed identifier. READU's many 'default X "
            "but code Y' incidents are config defaults with no engine predicate and mostly "
            "land in 'unclassified'. 'external-dependency-drift' inherits READU's broader "
            "external-resource theme. Exemplars anchor which kind of artifact tends to "
            "drift, not phrasing or a 1:1 class match."
        ),
        "gaps": gaps,
        "classes": classes,
        "controls_by_theme": _group(controls, "label"),
    }
    return bank


def _group(items: list[dict], key: str) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for it in items:
        out.setdefault(str(it.get(key)), []).append(it)
    return dict(sorted(out.items()))


def render_md(bank: dict) -> str:
    lines: list[str] = [
        "# Few-shot exemplar bank (generated)",
        "",
        f"Generated from `{bank['generated_from']['ruleset']}` "
        f"(sha256 `{bank['generated_from']['ruleset_sha256'][:16]}…`).",
        "Do not edit by hand; regenerate with `scripts/build_exemplar_bank.py`.",
        "",
        "## Counts",
        "",
        f"- triaged (primary): {bank['counts']['triaged']} "
        f"({bank['counts']['triaged_with_evidence']} with before/after evidence)",
        f"- raw (separate pool): {bank['counts']['raw']}",
        f"- controls (negatives): {bank['counts']['controls']}",
        f"- triaged by source: {bank['counts']['triaged_by_source']}",
        "",
        "| canonical_class | artifact | predicate | triaged | raw | total |",
        "|---|---|---|---:|---:|---:|",
    ]
    for cls, body in bank["classes"].items():
        lines.append(
            f"| `{cls}` | `{body['artifact_class']}` | `{body['predicate']}` | "
            f"{len(body['triaged'])} | {len(body['raw'])} | {body['exemplar_count']} |"
        )
    lines += ["", f"Gaps (no exemplar): {bank['gaps'] or 'none'}", ""]
    for cls, body in bank["classes"].items():
        lines += [f"## `{cls}` — {body['artifact_class']} ({body['predicate']})", ""]
        if body["triaged"]:
            lines.append("**Triaged (primary)**")
            for e in body["triaged"]:
                lines.append(f"- `{e['id']}` — {e['quote']}  \n  {e['commit_url']}")
                lines.extend(_render_evidence_md(e.get("evidence")))
            lines.append("")
        if body["raw"]:
            lines.append("**Raw (separate pool)**")
            for e in body["raw"][:15]:
                lines.append(f"- `{e['id']}` — {e['quote']}")
            if len(body["raw"]) > 15:
                lines.append(f"- … {len(body['raw']) - 15} more in `bank.json`")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _render_evidence_md(evidence: dict | None, cap: int = 6) -> list[str]:
    if not evidence or evidence.get("status") != "ok" or not evidence.get("files"):
        return []
    out = ["  before/after (real commit):"]
    for f in evidence["files"]:
        tag = "matched" if f.get("matched_location") else "fallback"
        out.append(f"  - `{f['path']}` ({f['side']}, {tag})")
        for line in f.get("removed", [])[:cap]:
            out.append(f"    - {line}")
        for line in f.get("added", [])[:cap]:
            out.append(f"    + {line}")
    return out


def _dump(bank: dict) -> str:
    return json.dumps(bank, ensure_ascii=False, indent=2) + "\n"


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default="", help="repository root (default: autodetect)")
    ap.add_argument("--rules", default=str(DEFAULT_RULES))
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--md", default=str(DEFAULT_MD))
    ap.add_argument("--check", action="store_true", help="rebuild and compare; do not write")
    args = ap.parse_args(argv)

    root = Path(args.root).resolve() if args.root else _find_root(HERE)
    bank = build_bank(root, Path(args.rules))
    text = _dump(bank)
    md = render_md(bank)

    if args.check:
        out, md_out = Path(args.out), Path(args.md)
        problems = []
        if not out.is_file() or out.read_text(encoding="utf-8") != text:
            problems.append(f"{out} is stale or missing")
        if not md_out.is_file() or md_out.read_text(encoding="utf-8") != md:
            problems.append(f"{md_out} is stale or missing")
        for cls, body in bank["classes"].items():
            if body["exemplar_count"] == 0:
                problems.append(f"target class has no exemplar: {cls}")
        if problems:
            print("EXEMPLAR BANK CHECK FAILED")
            for p in problems:
                print(f"  - {p}")
            return 1
        print("EXEMPLAR BANK CHECK OK")
        print(
            f"  triaged={bank['counts']['triaged']} raw={bank['counts']['raw']} "
            f"controls={bank['counts']['controls']} per_class={bank['counts']['per_class']}"
        )
        return 0

    Path(args.out).write_text(text, encoding="utf-8")
    Path(args.md).write_text(md, encoding="utf-8")
    print(f"wrote {args.out} and {args.md}")
    print(
        f"  triaged={bank['counts']['triaged']} raw={bank['counts']['raw']} "
        f"controls={bank['counts']['controls']} per_class={bank['counts']['per_class']}"
    )
    if bank["gaps"]:
        print(f"  WARNING gaps (no exemplar): {bank['gaps']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
