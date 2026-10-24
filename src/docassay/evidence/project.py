"""Project-meta inventory harvested from the analyzed repository.

The LICENSE predicate's evidence source is the project's own packaging metadata
: the manifest's ``project.license`` field plus the ``LICENSE``
file. The world is CLOSED over that inventory — a declared license makes a
mismatched claim refutable.

License names are normalized to canonical forms (§7.1): ``BSD-3-Clause`` and
``BSD 3-Clause`` fold to ``bsd`` (README prose rarely distinguishes clauses, so
folding avoids false REFUTED), ``CC-BY-4.0`` folds to ``cc-by``, and
``apache``/``apache-2.0``/``Apache 2.0`` all land on ``apache-2.0``.
"""

from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass
from pathlib import Path

from docassay.data import load, load_dict, load_list, regex_alternation
from docassay.evidence.manifests import iter_manifest_files
from docassay.vocabularies.structure import SKIPPED_DIRS

# License names and license-context words (data/project.json). A license name
# is an anchor only inside a license context (or with an explicit version).
LICENSE_NAMES: frozenset[str] = load_list("project.json", "license_names")
LICENSE_CONTEXT_WORDS: frozenset[str] = load_list("project.json", "license_context_words")

# Canonical fold for license aliases (data/project.json is the anchor list; the
# fold table lives here because several surface forms share one canonical).
_LICENSE_FOLD: dict[str, str] = load_dict("project.json", "license_fold", default={})

# Versionable license bases: when a claim/field carries a version number next
# to one of these names, the version is folded into the canonical form
# (``gpl`` + ``3.0`` → ``gpl-3.0``). ``bsd`` and ``cc-by`` deliberately do not
# fold a bare number into a clause variant (see module docstring).
_VERSIONED_LICENSE_BASES: frozenset[str] = load_list(
    "project.json", "versioned_license_bases", default=("gpl", "lgpl", "agpl", "mpl", "epl")
)

_LICENSE_NAME_RE: re.Pattern[str] = re.compile(
    r"\b(?:" + regex_alternation(LICENSE_NAMES) + r")(?:-?v?[0-9]+(?:\.[0-9]+)*)?\b",
    re.IGNORECASE,
)
_LICENSE_CTX_RE: re.Pattern[str] = re.compile(
    r"\b(?:" + regex_alternation(LICENSE_CONTEXT_WORDS) + r")\b", re.IGNORECASE
)

# ``bsd-3-clause`` / ``apache-2.0`` → (base, version) — a license name with an
# embedded version in the token itself.
_EMBEDDED_VERSION_RE = re.compile(
    r"^(?P<base>[a-z0-9]+(?:-[a-z0-9]+)*?)-(?P<ver>[0-9]+(?:\.[0-9]+)*)(?:-[a-z0-9]+)*$"
)

# Files whose content carries the project's license (data/project.json).
_LICENSE_FILE_STEMS: tuple[str, ...] = (
    "license",
    "licence",
    "copying",
    "notice",
    "copyright",
)
_MAX_LICENSE_SCAN_DEPTH = 2

# Directories whose LICENSE files belong to vendored third-party code, not to
# the analyzed project. A vendored `crates/polars-arrow/LICENSE` (Apache) must
# not make Apache the declared license of a project whose root LICENSE is MIT.
_LICENSE_VENDOR_DIRS: frozenset[str] = load_list("structure.json", "license_non_project_dirs")

# Full license texts are identified by their standard headers/bodies: the
# license name is not present as a short token near a context word. The
# patterns are a projection of the canonical license texts (GNU
# GPL/LGPL/AGPL, MPL 2.0, SPDX MIT/BSD) and live in ``data/project.json``
# (``license_header_patterns``) so their provenance is registered.
_LICENSE_HEADER_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = tuple(
    (re.compile(pattern, re.IGNORECASE), base)
    for pattern, base in load("project.json").get("license_header_patterns", [])
)
_LICENSE_HEADER_VERSION_RE = re.compile(r"version\s+([0-9]+(?:\.[0-9]+)*)", re.IGNORECASE)

@dataclass(frozen=True, slots=True)
class LicenseEvidence:
    """One declared license (manifest field or a LICENSE-file detection)."""

    evidence_id: str
    license_name: str
    source_file: str
    line_start: int | None = None
    line_end: int | None = None
    snippet: str = ""
    domain: str = ""

    @property
    def object(self) -> str:
        """The canonical license name grouping claims with evidence."""
        return self.license_name


def canonical_license(name: str, version: str | None = None) -> str:
    """Normalize a license mention to its canonical form (§7.1).

    ``name`` may carry an embedded version (``apache-2.0``); ``version`` is the
    context marker of the claim (``Apache 2.0`` → ``==2.0``). Versionable bases
    fold the version in (``gpl`` + ``3.0`` → ``gpl-3.0``); ``bsd``/``cc-by``
    fold to the bare form whatever the clause number.
    """
    token = name.strip().lower().replace("_", "-")
    # "GPLv3" → "gpl-3": a ``v`` directly between the base and the number is a
    # version marker, not part of the name.
    token = re.sub(r"(?<=[a-z])v(?=[0-9])", "-", token)
    # "BSD 3-Clause" / "BSD-3-Clause" — the clause number folds into the bare
    # form (bsd), never a clause-specific referent (README prose rarely
    # distinguishes clauses; folding avoids false REFUTED).
    token = re.sub(r"[\s-]?\d+\s*-?\s*clauses?\b", "", token).strip()
    embedded = _EMBEDDED_VERSION_RE.match(token)
    base = embedded.group("base") if embedded else token
    ver = _version_number(version) or (embedded.group("ver") if embedded else None)
    if ver and base in _VERSIONED_LICENSE_BASES:
        if "." not in ver:
            ver += ".0"  # "GPL v3" / "gpl-2" → gpl-3.0 / gpl-2.0
        return f"{base}-{ver}"
    if base in _LICENSE_FOLD:
        return _LICENSE_FOLD[base]
    return base


# An SPDX license expression: ``BSD-3-Clause AND 0BSD AND MIT AND CC0-1.0`` (or
# ``OR``/``WITH``). Each operand is a separate declared license, not one
# concatenated name.
_SPDX_SPLIT_RE = re.compile(r"\s+(?:AND|OR|WITH)\s+|,", re.IGNORECASE)


def canonical_licenses(expression: str) -> list[str]:
    """Every canonical license named in a manifest field / SPDX expression."""
    if not expression.strip():
        return []
    parts = [p.strip() for p in _SPDX_SPLIT_RE.split(expression) if p.strip()]
    out: list[str] = []
    seen: set[str] = set()
    for part in parts:
        canonical = canonical_license(part)
        if canonical and canonical not in seen:
            seen.add(canonical)
            out.append(canonical)
    if not out:
        canonical = canonical_license(expression)
        if canonical:
            out.append(canonical)
    return out


def _version_number(version: str | None) -> str | None:
    if not version:
        return None
    m = re.match(r"(?:==|>=|<=|>|<|~=|\^|!=)?\s*v?(\d+(?:\.\d+)*)", version)
    return m.group(1) if m else None


def _find_line(lines: list[str], needle: str, cursor: list[int]) -> tuple[int | None, str]:
    for i in range(cursor[0], len(lines)):
        if needle in lines[i]:
            cursor[0] = i + 1
            return i + 1, lines[i].strip()
    return None, ""


def build_license_inventory(project_root: Path) -> list[LicenseEvidence]:
    """The declared license: manifest fields plus LICENSE-file detections."""
    evidence: list[LicenseEvidence] = []
    for path, rel in iter_manifest_files(project_root):
        _extract_manifest_license(evidence, path, rel)
    for path, rel in _iter_license_files(project_root):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")[:4000]
        except OSError:
            continue
        for canonical in detect_licenses_in_text(text):
            line = _license_name_line(text, canonical)
            evidence.append(
                LicenseEvidence(
                    evidence_id=f"license:{rel}:{canonical}",
                    license_name=canonical,
                    source_file=rel,
                    line_start=line,
                    line_end=line,
                    snippet=next(
                        (
                            line.strip()
                            for line in text.splitlines()
                            if _LICENSE_NAME_RE.search(line)
                        ),
                        "",
                    ),
                )
            )
    return _dedupe(evidence)


def _extract_manifest_license(evidence: list[LicenseEvidence], path: Path, rel: str) -> None:
    if path.name == "pyproject.toml":
        try:
            raw = path.read_text(encoding="utf-8-sig")
            data = tomllib.loads(raw)
        except (OSError, ValueError):
            return
        project = data.get("project")
        if isinstance(project, dict):
            _emit_license_field(evidence, project.get("license"), rel, raw)
        poetry = (data.get("tool") or {}).get("poetry")
        if isinstance(poetry, dict):
            _emit_license_field(evidence, poetry.get("license"), rel, raw)
    elif path.name == "setup.cfg":
        _extract_setup_cfg_license(evidence, path, rel)


def _emit_license_field(
    evidence: list[LicenseEvidence],
    field: object,
    rel: str,
    raw: str,
) -> None:
    if isinstance(field, str):
        text = field
    elif isinstance(field, dict):
        text = field.get("text")
        if not isinstance(text, str) or not text.strip():
            return
    else:
        return
    canonicals = canonical_licenses(text)
    if not canonicals:
        return
    lines = raw.splitlines()
    line, snippet = _find_line(lines, text, [0])
    for canonical in canonicals:
        if canonical == "apache":
            canonical = "apache-2.0"  # an unversioned "Apache" field is 2.x
        evidence.append(
            LicenseEvidence(
                evidence_id=f"license:{rel}:{canonical}",
                license_name=canonical,
                source_file=rel,
                line_start=line,
                line_end=line,
                snippet=snippet,
            )
        )


def _extract_setup_cfg_license(evidence: list[LicenseEvidence], path: Path, rel: str) -> None:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return
    for line_no, line in enumerate(lines, start=1):
        m = re.match(r"^\s*license\s*=\s*(.+?)\s*$", line)
        if not m or not m.group(1).strip():
            continue
        canonical = canonical_license(m.group(1).strip())
        evidence.append(
            LicenseEvidence(
                evidence_id=f"license:{rel}:{canonical}",
                license_name=canonical,
                source_file=rel,
                line_start=line_no,
                line_end=line_no,
                snippet=line.strip(),
            )
        )
        return


def _iter_license_files(project_root: Path):
    found: list[tuple[Path, str]] = []
    for dirpath, dirnames, filenames in Path(project_root).walk():
        rel_dir = dirpath.relative_to(project_root)
        if len(rel_dir.parts) > _MAX_LICENSE_SCAN_DEPTH:
            dirnames[:] = []
            continue
        dirnames[:] = sorted(d for d in dirnames if d not in SKIPPED_DIRS and not d.startswith("."))
        base = "" if rel_dir == Path(".") else rel_dir.as_posix() + "/"
        if any(part in _LICENSE_VENDOR_DIRS for part in rel_dir.parts):
            continue
        for filename in sorted(filenames):
            stem = Path(filename).stem.lower()
            if not any(stem.startswith(prefix) for prefix in _LICENSE_FILE_STEMS):
                continue
            found.append((dirpath / filename, base + filename))
    return found


def detect_licenses_in_text(text: str) -> list[str]:
    """Canonical license names detected in a text (first 2000 chars).

    Prefers matches with an adjacent version or near a license-context word, so
    ``Apache License 2.0`` yields ``apache-2.0`` and ``released under the MIT
    license`` yields ``mit``. Full license texts (GNU GPL/LGPL/AGPL, MPL) carry
    their name in a standard header rather than as a short token, so headers are
    detected explicitly. Deterministic order (position, then
    longest canonical first).
    """
    head = text[:2000].lower()
    found: list[tuple[int, int, str]] = []
    for m in _LICENSE_NAME_RE.finditer(head):
        start = m.start()
        token = m.group(0)
        end = m.end()
        after = head[end : end + 12]
        ver_m = re.match(r"\s*(?:v)?\s*([0-9]+(?:\.[0-9]+)*)", after)
        version = ver_m.group(1) if ver_m else None
        near = _LICENSE_CTX_RE.search(head[max(0, start - 40) : end + 40])
        if not version and not near:
            continue
        canonical = canonical_license(token, f"=={version}" if version else None)
        if canonical == "apache" and not version:
            canonical = "apache-2.0"
        found.append((start, -len(canonical), canonical))
    for start, (_pattern, base) in _license_header_hits(text):
        version_match = _LICENSE_HEADER_VERSION_RE.search(text[start : start + 400])
        canonical = canonical_license(
            base, f"=={version_match.group(1)}" if version_match else None
        )
        if canonical:
            found.append((start, -len(canonical), canonical))
    seen: set[str] = set()
    out: list[str] = []
    for _start, _prio, canonical in sorted(found, key=lambda f: (f[0], f[1])):
        if canonical in seen:
            continue
        seen.add(canonical)
        out.append(canonical)
    return out


def _license_header_hits(text: str) -> list[tuple[int, tuple[re.Pattern[str], str]]]:
    """``(position, (pattern, base))`` for every full-license header in ``text``."""
    hits: list[tuple[int, tuple[re.Pattern[str], str]]] = []
    for pattern, base in _LICENSE_HEADER_PATTERNS:
        match = pattern.search(text)
        if match:
            hits.append((match.start(), (pattern, base)))
    hits.sort(key=lambda item: item[0])
    return hits


def _license_name_line(text: str, canonical: str) -> int | None:
    base = canonical.rsplit("-", 1)[0] if canonical[-1:].isdigit() else canonical
    header_re = next((pattern for pattern, name in _LICENSE_HEADER_PATTERNS if name == base), None)
    for idx, line in enumerate(text.splitlines(), start=1):
        if _LICENSE_NAME_RE.search(line):
            return idx
        if header_re is not None and header_re.search(line):
            return idx
    return None


def has_packaging_manifest(project_root: Path) -> bool:
    """Whether the tree carries an authoritative packaging manifest."""
    return any(iter_manifest_files(project_root))


def has_license_inventory(project_root: Path) -> bool:
    """Whether the tree declares a license (manifest field or LICENSE file)."""
    if has_packaging_manifest(project_root):
        return True
    return any(_iter_license_files(project_root))


def _dedupe(items) -> list:
    seen: set[str] = set()
    out = []
    for item in items:
        if item.evidence_id in seen:
            continue
        seen.add(item.evidence_id)
        out.append(item)
    return out
