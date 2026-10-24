"""Engine-free control candidates for Stage B.

A **consistent-present** control is a current-state documentation claim about an
artifact that exists and is consistent with the repository.  The tool must not
refute it; a refutation is a false positive.  This script only *proposes*
candidates from the docs and the structural inventory.  It never imports the
engine and never reads a tool claim, so control selection cannot be conditioned
on the tool's behaviour.

The proposals are reviewed before scoring (the doc line must be a current-state
claim).  ``--snapshots`` also creates a clean ``<repo>__control`` snapshot pair
for ``score_injections.py``.

Run::

    PYTHONPATH=src uv run python .../scripts/build_controls.py \
        --out .../runs/stage-b-2026-10-20/controls.jsonl \
        --snapshots .../runs/stage-b-2026-10-20/snapshots
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
INJECTED_GOLD = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(INJECTED_GOLD))
import _corpus  # noqa: E402
import classify_claim_context as clf  # noqa: E402
from engine import grammar  # noqa: E402

NATURAL = INJECTED_GOLD / "synthetic-natural"

_BACKTICK = re.compile(r"`([^`\n]+)`")
_LINK = re.compile(r"\]\(([^)\s]+)\)")
_NEGATIVE = (
    "not ",
    "no ",
    "never",
    "historical",
    "deprecated",
    "removed",
    "placeholder",
    "unimplemented",
    "does not",
    "doesn't",
    "will not",
    "planned",
    "roadmap",
    "not yet",
)
_POSITIVE_DEP = ("depend", "requires", "install", ">=", "<=", "==", "~=", "- `")


def _looks_current(line: str) -> bool:
    low = line.lower()
    return not any(marker in low for marker in _NEGATIVE)


def _iter_lines(text: str):
    """Yield ``(lineno, line, in_fence)``; fenced code is marked and skipped."""
    in_fence = False
    for lineno, line in enumerate(text.splitlines(), start=1):
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            yield lineno, line, True
            continue
        yield lineno, line, in_fence


def _path_candidates(inv, docs):
    out = []
    for doc_path, text in docs:
        for lineno, line, in_fence in _iter_lines(text):
            if in_fence or not _looks_current(line):
                continue
            tokens = [m.group(1).strip() for m in _BACKTICK.finditer(line)]
            tokens += [m.group(1).strip().split("#", 1)[0] for m in _LINK.finditer(line)]
            for token in tokens:
                if not token or "://" in token or token.startswith("#"):
                    continue
                resolved = _corpus.resolve_path(inv, token, doc_path)
                if resolved and (resolved.endswith("/") or "." in Path(resolved).name):
                    out.append(
                        {
                            "canonical_class": "path-location-drift",
                            "artifact_class": "path",
                            "target": token,
                            "old": token,
                            "resolved": resolved,
                            "doc_path": doc_path,
                            "line": lineno,
                            "doc_line_text": line,
                        }
                    )
                    break
            if out and out[-1]["doc_path"] == doc_path and out[-1]["line"] == lineno:
                continue
    return out


def _dependency_candidates(inv, docs):
    out = []
    names = sorted(inv.deps)
    for doc_path, text in docs:
        for lineno, line, in_fence in _iter_lines(text):
            if in_fence or not _looks_current(line):
                continue
            low = line.lower()
            if not any(marker in low for marker in _POSITIVE_DEP):
                continue
            for name in names:
                if re.search(rf"(?<![A-Za-z0-9_-]){re.escape(name)}(?![A-Za-z0-9_-])", low):
                    out.append(
                        {
                            "canonical_class": "external-dependency-drift",
                            "artifact_class": "dependency",
                            "target": name,
                            "old": name,
                            "symbol": name,
                            "doc_path": doc_path,
                            "line": lineno,
                            "doc_line_text": line,
                        }
                    )
                    break
    return out


def _symbol_candidates(inv, docs):
    out = []
    # ``qualname`` is module-qualified; methods are a separate kind, so this
    # keeps top-level classes and functions only.
    defs = [d for d in inv.defs if d.kind in ("class", "function")]
    for doc_path, text in docs:
        for lineno, line, in_fence in _iter_lines(text):
            if in_fence or not _looks_current(line):
                continue
            for d in defs:
                name = d.name
                # Prefer a standalone backticked mention (`` `Name` `` or
                # `` `Name()` ``) over headings such as `` `class Name` ``.
                if re.search(rf"`{re.escape(name)}(?:\(\))?`", line):
                    hits = _corpus.resolve_symbol(inv, name)
                    if len(hits) == 1:
                        out.append(
                            {
                                "canonical_class": "identifier-drift",
                                "artifact_class": "identifier",
                                "target": name,
                                "old": name,
                                "symbol": name,
                                "doc_path": doc_path,
                                "line": lineno,
                                "doc_line_text": line,
                            }
                        )
                        break
    return out


def _pick(candidates, limit=1):
    """Deterministic first-N, one per doc line, preferring prose over headings."""
    seen = set()
    picked = []
    for cand in sorted(
        candidates,
        key=lambda c: (c["doc_path"] != "README.md", c["doc_path"], c["line"], c["target"]),
    ):
        key = (cand["canonical_class"], cand["target"].lower())
        line_key = (cand["doc_path"], cand["line"])
        if key in seen or line_key in seen:
            continue
        seen.add(key)
        picked.append(cand)
        if len(picked) >= limit:
            break
    return picked


# --------------------------------------------------------------------------- #
# Stage C control families (A1–A4, B, C)
# --------------------------------------------------------------------------- #

_FAMILY_CLASS = {
    "A1": ("path-location-drift", "path"),
    "A2": ("external-dependency-drift", "dependency"),
    "A3": ("identifier-drift", "identifier"),
    "A4": ("identifier-drift", "identifier"),
    "B": ("identifier-drift", "identifier"),
    "C": ("path-location-drift", "path"),
}


def _qualified_symbol_candidates(inv, docs):
    """Stage C A3: a document-written dotted name whose top is project-owned."""
    out = []
    tops = set(inv.top_packages) or {m.split(".", 1)[0] for m in inv.modules}
    qualnames = {d.qualname for d in inv.defs}
    for doc_path, text in docs:
        for lineno, line, in_fence in _iter_lines(text):
            if in_fence or not _looks_current(line):
                continue
            for match in _BACKTICK.finditer(line):
                token = match.group(1).strip()
                if "." not in token or token.split(".", 1)[0] not in tops:
                    continue
                if token in qualnames:
                    out.append({
                        "canonical_class": "identifier-drift",
                        "artifact_class": "identifier",
                        "target": token,
                        "old": token,
                        "symbol": token,
                        "doc_path": doc_path,
                        "line": lineno,
                        "doc_line_text": line,
                    })
                    break
    return out


def _bare_token(line: str) -> str | None:
    for match in _BACKTICK.finditer(line):
        token = clf._member_token(match.group(1))
        if token:
            return token
    return None


def _stage_c_candidates(inv, docs, families: set[str]) -> dict[str, list[dict]]:
    modules = frozenset(inv.modules)
    deps = frozenset(name.lower() for name in inv.deps)
    paths = frozenset(inv.files | inv.dirs)
    out: dict[str, list[dict]] = {family: [] for family in families}
    for doc_path, text in docs:
        if "A1" in families:
            for cand in _path_candidates(inv, [(doc_path, text)]):
                out["A1"].append(cand)
        if "A2" in families:
            for cand in _dependency_candidates(inv, [(doc_path, text)]):
                out["A2"].append(cand)
        if "A3" in families:
            for cand in _qualified_symbol_candidates(inv, [(doc_path, text)]):
                out["A3"].append(cand)
        rows = clf.classify_document(text, modules=modules, dependencies=deps, paths=paths)
        for row in rows:
            line = row["text"]
            if row["claim_form"] == "section_qualified" and "A4" in families:
                token = _bare_token(line)
                module = row.get("context_module")
                if not token or not module:
                    continue
                qualified = f"{module}.{token}"
                if any(d.qualname == qualified for d in inv.defs):
                    out["A4"].append({
                        "canonical_class": "identifier-drift",
                        "artifact_class": "identifier",
                        "target": token,
                        "old": token,
                        "symbol": qualified,
                        "doc_path": doc_path,
                        "line": row["line"],
                        "doc_line_text": line,
                        "context_module": module,
                        "context_source": row["context_source"],
                    })
            elif row["claim_form"] in ("bare", "bare_call") and "B" in families:
                token = _bare_token(line)
                if not token:
                    continue
                if not any(d.name == token for d in inv.defs):
                    continue
                if not line.lstrip().startswith(("#", "-", "*", "|")):
                    continue
                out["B"].append({
                    "canonical_class": "identifier-drift",
                    "artifact_class": "identifier",
                    "target": token,
                    "old": token,
                    "symbol": token,
                    "doc_path": doc_path,
                    "line": row["line"],
                    "doc_line_text": line,
                })
        if "C" in families:
            for lineno, line, in_fence in _iter_lines(text):
                if in_fence or not _looks_current(line):
                    continue
                low = line.lower()
                if not re.search(r"\b(?:does not|doesn't|no|without|not)\b", low):
                    continue
                for name in sorted(deps):
                    if re.search(rf"(?<![A-Za-z0-9_-]){re.escape(name)}(?![A-Za-z0-9_-])", low):
                        out["C"].append({
                            "canonical_class": "external-dependency-drift",
                            "artifact_class": "dependency",
                            "target": name,
                            "old": name,
                            "symbol": name,
                            "doc_path": doc_path,
                            "line": lineno,
                            "doc_line_text": line,
                            "expected_absence": True,
                        })
                        break
    return out


def build_stage_c(
    repos: list[str],
    corpus_dir: Path,
    families: list[str],
    snapshots: Path | None = None,
) -> list[dict]:
    controls: list[dict] = []
    for repo in repos:
        root = corpus_dir / repo
        inv = _corpus.build_inventory(root)
        docs = _corpus.iter_doc_texts(root)
        per_family = _stage_c_candidates(inv, docs, set(families))
        for family in families:
            chosen = _pick(per_family.get(family, []), limit=1)
            for cand in chosen:
                canonical, artifact = _FAMILY_CLASS[family]
                cand.update({
                    "repo": f"{repo}__control",
                    "repo_name": repo,
                    "control": family,
                    "family": family,
                    "canonical_class": canonical,
                    "artifact_class": artifact,
                    "expected_verdict": "not_refuted",
                    "selection": (
                        f"engine-free {family} candidate; "
                        "reviewed as a current-state claim"
                    ),
                })
                controls.append(cand)
        if snapshots is not None:
            snapshots.mkdir(parents=True, exist_ok=True)
            grammar.snapshot(root, snapshots / f"{repo}__control__baseline")
            grammar.snapshot(root, snapshots / f"{repo}__control__injected")
    return controls


def build(repos: list[str], snapshots: Path | None = None) -> list[dict]:
    controls: list[dict] = []
    for repo in repos:
        root = NATURAL / repo
        inv = _corpus.build_inventory(root)
        docs = _corpus.iter_doc_texts(root)
        chosen = []
        chosen += _pick(_path_candidates(inv, docs), limit=1)
        chosen += _pick(_dependency_candidates(inv, docs), limit=1)
        chosen += _pick(_symbol_candidates(inv, docs), limit=1)
        for cand in chosen:
            cand.update(
                {
                    "repo": f"{repo}__control",
                    "repo_name": repo,
                    "control": "consistent_present",
                    "expected_verdict": "not_refuted",
                    "selection": "engine-free candidate; reviewed as a current-state claim",
                }
            )
            controls.append(cand)
        if snapshots is not None:
            snapshots.mkdir(parents=True, exist_ok=True)
            grammar.snapshot(root, snapshots / f"{repo}__control__baseline")
            grammar.snapshot(root, snapshots / f"{repo}__control__injected")
    return controls


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repos", default="", help="comma-separated; default: all natural repos")
    ap.add_argument("--out", required=True)
    ap.add_argument("--snapshots", default="")
    ap.add_argument("--corpus-dir", default=str(NATURAL), help="Stage C corpus root")
    ap.add_argument(
        "--families",
        default="",
        help="Stage C families (A1,A2,A3,A4,B,C); empty = Stage B path/dependency/symbol",
    )
    args = ap.parse_args(argv)

    corpus_dir = Path(args.corpus_dir)
    repos = [r for r in args.repos.split(",") if r] or sorted(
        p.name for p in corpus_dir.iterdir() if p.is_dir()
    )
    if args.families:
        controls = build_stage_c(
            repos,
            corpus_dir,
            [f.strip() for f in args.families.split(",") if f.strip()],
            Path(args.snapshots) if args.snapshots else None,
        )
    else:
        controls = build(repos, Path(args.snapshots) if args.snapshots else None)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        "".join(json.dumps(c, ensure_ascii=False) + "\n" for c in controls), encoding="utf-8"
    )
    print(f"wrote {len(controls)} control candidates -> {out}")
    for c in controls:
        print(f"  {c['repo_name']:12s} {c['canonical_class']:28s} {c['target']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
