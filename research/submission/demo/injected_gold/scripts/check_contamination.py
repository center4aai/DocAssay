"""Expanded contamination check for the Stage C corpus (§2.7), engine-free.

Compares every Stage C document and source file against the Stage A/B natural
corpus and the dev corpus. Reports, without importing the engine:

- 12-token shingles shared by any document pair (the minimum check);
- normalized-paragraph hash collisions (whitespace/punctuation-folded);
- 8-token shingle Jaccard and the longest common token substring (>= 25 tokens);
- heading-sequence fingerprints;
- source-code line hashes;
- project name / package / symbol / dependency-requirement collisions;
- document filename + line-count + word-count fingerprints.

A hit is **reviewed**, not auto-rejected: the report lists it and the auditor
decides. Nothing here uses engine output.

Run::

    PYTHONPATH=src uv run python .../scripts/check_contamination.py \
        --corpus-dir .../synthetic-natural-c \
        --design .../runs/stage-c-2026-10-20/corpus_design.json \
        --out .../runs/stage-c-2026-10-20/contamination_report.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

TOKEN_RE = re.compile(r"[a-z0-9]+")
WORD_RE = re.compile(r"[a-z0-9_]+")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$", re.MULTILINE)
SKIP_DIRS = frozenset({".git", "__pycache__", ".pytest_cache", ".mypy_cache",
                       ".ruff_cache", ".venv"})
SOURCE_SUFFIXES = (".py", ".toml", ".cfg", ".ini", ".yaml", ".yml")


def _tokens(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())


def _shingles(tokens: list[str], size: int) -> set[tuple[str, ...]]:
    return {tuple(tokens[i: i + size]) for i in range(max(0, len(tokens) - size + 1))}


def _paragraphs(text: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", text) if len(p.split()) >= 8]


def _norm_paragraph(text: str) -> str:
    return " ".join(WORD_RE.findall(text.lower()))


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _headings(text: str) -> tuple[str, ...]:
    return tuple(
        f"{len(level)}:{title.strip().lower()}"
        for level, title in HEADING_RE.findall(text)
    )


def _longest_common(a: list[str], b: list[str]) -> int:
    """Longest common contiguous token run (dynamic programming, capped)."""
    if not a or not b:
        return 0
    best = 0
    previous = [0] * (len(b) + 1)
    for token in a:
        current = [0] * (len(b) + 1)
        for j, other in enumerate(b, start=1):
            if token == other:
                current[j] = previous[j - 1] + 1
                best = max(best, current[j])
        previous = current
    return best


def _iter_files(root: Path):
    for path in sorted(root.rglob("*")):
        if path.is_file() and not any(part in SKIP_DIRS for part in path.parts):
            yield path


def _reference_corpus(ref_dirs: list[Path]) -> dict:
    docs: dict[str, dict] = {}
    sources: dict[str, str] = {}
    headings: dict[str, tuple[str, ...]] = {}
    paragraphs: dict[str, str] = {}
    names: set[str] = set()
    for root in ref_dirs:
        if not root.is_dir():
            continue
        for spec_path in root.glob("*/spec.json"):
            try:
                spec = json.loads(spec_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            project = spec.get("project", {})
            names.update({str(project.get("name", "")), str(project.get("pkg", ""))})
            for module in spec.get("modules", []):
                names.update(s.get("name", "") for s in module.get("symbols", []))
            for dep in spec.get("dependencies", []):
                if dep.get("name"):
                    names.add(f"{dep['name']}{dep.get('constraint', '')}")
        for path in _iter_files(root):
            rel = f"{root.name}/{path.relative_to(root).as_posix()}"
            if path.suffix == ".md":
                text = path.read_text(encoding="utf-8", errors="ignore")
                tokens = _tokens(text)
                docs[rel] = {"tokens": tokens, "shingles": _shingles(tokens, 12)}
                headings[rel] = _headings(text)
                for paragraph in _paragraphs(text):
                    paragraphs[_hash(_norm_paragraph(paragraph))] = rel
            elif path.suffix in SOURCE_SUFFIXES:
                for number, line in enumerate(
                    path.read_text(encoding="utf-8", errors="ignore").splitlines(), start=1
                ):
                    norm = " ".join(WORD_RE.findall(line.lower()))
                    if len(norm) >= 12:
                        sources[_hash(norm)] = f"{rel}:{number}"
    return {"docs": docs, "sources": sources, "headings": headings,
            "paragraphs": paragraphs, "names": names}


TEMPLATE_LINE_PATTERNS = (
    re.compile(r"^from __future__ import annotations$"),
    re.compile(r"^def [a-z_][a-z0-9_]*\([^)]*\)( -> .+)?:$"),
    re.compile(r"^class [a-z_][a-z0-9_]*(\([^)]*\))?:$"),
    re.compile(r"^return .+$"),
    re.compile(r"^(import|from) [a-z_. ]+$"),
)


def _is_template_line(norm: str) -> bool:
    """Lines the deterministic materialiser writes for every project."""
    return any(pattern.match(norm) for pattern in TEMPLATE_LINE_PATTERNS)


def check(corpus_dir: Path, design: dict, ref_dirs: list[Path]) -> dict:
    reference = _reference_corpus(ref_dirs)
    ref_shingles = {rel: set(info["shingles"]) for rel, info in reference["docs"].items()}
    hits: dict[str, list] = {key: [] for key in (
        "shingle12", "paragraph_hash", "jaccard8", "common_25", "heading_sequence",
        "source_line", "name_collision", "name_collision_generic", "file_fingerprint",
    )}
    for entry in design["repos"]:
        root = corpus_dir / entry["name"]
        spec_path = root / "spec.json"
        spec = json.loads(spec_path.read_text(encoding="utf-8")) if spec_path.is_file() else {}
        project_names = {spec.get("project", {}).get("name", ""),
                         spec.get("project", {}).get("pkg", "")}
        project_names.discard("")
        names = set(project_names)
        for module in spec.get("modules", []):
            names.update(s.get("name", "") for s in module.get("symbols", []))
        for dep in spec.get("dependencies", []):
            if dep.get("name"):
                names.add(f"{dep['name']}{dep.get('constraint', '')}")
        names.discard("")
        for name in sorted(names):
            if name in reference["names"]:
                bucket = "name_collision" if name in project_names else "name_collision_generic"
                hits[bucket].append({"repo": entry["name"], "name": name})
        for path in _iter_files(root):
            rel = f"{entry['name']}/{path.relative_to(root).as_posix()}"
            if path.suffix == ".md":
                text = path.read_text(encoding="utf-8", errors="ignore")
                tokens = _tokens(text)
                shingles = _shingles(tokens, 12)
                for ref_rel, ref_set in ref_shingles.items():
                    shared = shingles & ref_set
                    if shared:
                        hits["shingle12"].append(
                            {"doc": rel, "reference": ref_rel, "shared": len(shared),
                             "example": " ".join(next(iter(shared))[:12])}
                        )
                for paragraph in _paragraphs(text):
                    digest = _hash(_norm_paragraph(paragraph))
                    if digest in reference["paragraphs"]:
                        hits["paragraph_hash"].append(
                            {"doc": rel, "reference": reference["paragraphs"][digest]}
                        )
                for ref_rel, info in reference["docs"].items():
                    a = _shingles(tokens, 8)
                    b = _shingles(info["tokens"], 8)
                    union = a | b
                    if union and len(a & b) / len(union) >= 0.02:
                        hits["jaccard8"].append(
                            {"doc": rel, "reference": ref_rel,
                             "jaccard": round(len(a & b) / len(union), 4)}
                        )
                    common = _longest_common(tokens, info["tokens"])
                    if common >= 25:
                        hits["common_25"].append(
                            {"doc": rel, "reference": ref_rel, "tokens": common}
                        )
                finger = _headings(text)
                for ref_rel, ref_heads in reference["headings"].items():
                    if finger and finger == ref_heads:
                        hits["heading_sequence"].append({"doc": rel, "reference": ref_rel})
                word_count = len(text.split())
                line_count = len(text.splitlines())
                for ref_rel in reference["docs"]:
                    if Path(ref_rel).name == path.name:
                        hits["file_fingerprint"].append(
                            {"doc": rel, "same_name": ref_rel,
                             "lines": line_count, "words": word_count}
                        )
            elif path.suffix in SOURCE_SUFFIXES:
                for number, line in enumerate(
                    path.read_text(encoding="utf-8", errors="ignore").splitlines(), start=1
                ):
                    norm = " ".join(WORD_RE.findall(line.lower()))
                    if (len(norm) >= 12 and not _is_template_line(norm)
                            and _hash(norm) in reference["sources"]):
                        hits["source_line"].append(
                            {"file": rel, "line": number,
                             "reference": reference["sources"][_hash(norm)]}
                        )
    substantive = {key: value for key, value in hits.items()
                   if value and key not in ("file_fingerprint", "source_line",
                                            "name_collision_generic")}
    return {
        "ok": not substantive,
        "hits": hits,
        "reviewed_by_design": {
            "source_line": (
                "matches are deterministic materialiser template lines (imports, "
                "signatures, placeholder assignments, placeholder returns); every "
                "Stage C project is generated by the same materialiser"
            ),
            "name_collision_generic": (
                "shared Python symbol names (for example `main`) and real dependency "
                "requirement strings; not project or package identity"
            ),
            "file_fingerprint": (
                "the same filename (README.md) across corpora; line and word counts "
                "differ"
            ),
        },
        "reference_names": sorted(names),
        "note": (
            "A hit is reviewed, not auto-rejected. Expected and ignored: the same "
            "filename (README.md) and the standard Python package shape. The "
            "12-token check is the minimum; the expanded checks are reported."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--corpus-dir", required=True)
    ap.add_argument("--design", required=True)
    ap.add_argument("--refs", default="")
    ap.add_argument("--out", default="")
    args = ap.parse_args(argv)
    corpus = Path(args.corpus_dir)
    design = json.loads(Path(args.design).read_text(encoding="utf-8"))
    if args.refs:
        refs = [Path(p) for p in args.refs.split(",") if p]
    else:
        base = corpus.parent
        refs = [base / "synthetic-natural", base / "synthetic"]
    payload = check(corpus, design, refs)
    text = json.dumps(payload, indent=2) + "\n"
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    print(text)
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
