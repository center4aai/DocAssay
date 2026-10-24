"""Shared corpus utilities for the injected_gold pipeline.

Standard library only. The engine (``docassay``) is **never** imported here,
so operator target selection and independent verification cannot depend on the
engine's predicate vocabulary. This is the mechanical guard behind the
circularity rule: the classes come from ``normalization.json`` and the targets
from generic document/code structure, not from ``src/docassay/predicates``.
"""

from __future__ import annotations

import ast
import re
import tomllib
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

DOC_SUFFIXES = (".md", ".rst", ".txt")
PY_SUFFIX = ".py"

# Runtime/vendor directories never sampled for targets.
SKIP_DIRS = frozenset(
    {
        ".git",
        ".hg",
        ".svn",
        ".venv",
        "venv",
        "__pycache__",
        "node_modules",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".tox",
        ".eggs",
        "build",
        "dist",
    }
)

# Change-history document genre: not a current-state target (mirrors the
# engine's exclusion intent, kept conservative so targets are real current-state
# claims). This is target hygiene, not class selection.
HISTORY_MARKERS = (
    "changelog",
    "release",
    "releases",
    "whats-new",
    "whatsnew",
    "whats_new",
    "history",
    "upgrading",
    "updating",
    "migration",
    "release-notes",
    "release_notes",
)

_IDENT = r"[A-Za-z_][A-Za-z0-9_]*"
_DOTTED_RE = re.compile(rf"{_IDENT}(?:\.{_IDENT})+")
_CALL_RE = re.compile(rf"{_IDENT}(?:\.{_IDENT})*\(\s*\)")
_BACKTICK_RE = re.compile(r"`([^`\n]+)`")
_FILE_EXT_RE = re.compile(r"\.[A-Za-z0-9]{1,6}$")
_UPPER_SNAKE_RE = re.compile(r"^[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+$")
_DEP_NAME_RE = re.compile(r"^\s*([A-Za-z0-9][A-Za-z0-9._-]*)")

# --- English-only document scope ------------------------------------------------
# Injections must land in documents the engine actually scans. The engine's
# corpus is English-only (non-Latin scripts and Latin-script translations are
# excluded), so we mirror that rule here (standard library only) rather than
# importing the engine. Localized docs are skipped by path (`docs/<lang>/`,
# `README.<lang>.md`, `i18n/<lang>/`) or by the text heuristics below.
_LANG_PATH_RE = re.compile(
    r"(?:^|/)(?:docs?|readme|i18n|locale|locales|translations?)[._/-]"
    r"([a-z]{2}(?:[-_][a-z]{2})?)(?:[._/-]|$)",
    re.IGNORECASE,
)
_ENGLISH_CODES = frozenset({"en", "en-us", "en-gb"})
# A file extension is not a language code: ``README.md`` must not be read as the
# "md" localization of a README.
_DOC_EXT_CODES = frozenset({"md", "rst", "txt", "html", "htm"})
_NON_LATIN_RE = re.compile(
    "[\u0370-\u03ff\u0400-\u04ff\u0590-\u05ff\u0600-\u06ff\u0900-\u097f"
    "\u0980-\u09ff\u0a00-\u0a7f\u0a80-\u0aff\u0b00-\u0b7f\u0b80-\u0bff"
    "\u0c00-\u0c7f\u0c80-\u0cff\u0d00-\u0d7f\u0e00-\u0e7f\u0f00-\u0fff"
    "\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af]"
)
_NON_ENGLISH_DIACRITICS = frozenset("äöüßáéíóúñàâçèêëîïôûùœãõșțăîğışí")
_DIACRITIC_RATIO = 0.008


def is_translation_path(rel: str) -> bool:
    """Whether a document path marks a non-English (localized) copy."""
    for m in _LANG_PATH_RE.finditer(rel):
        code = m.group(1).lower().replace("_", "-")
        if code in _DOC_EXT_CODES:
            continue
        if code not in _ENGLISH_CODES:
            return True
    return False


def is_english_document(text: str) -> bool:
    """Mirror of the engine's English-only document scope (see pipeline.py)."""
    body = re.sub(r"<!--.*?-->", " ", text, flags=re.S)
    body = re.sub(r"```.*?```", " ", body, flags=re.S)
    body = re.sub(r"`[^`]+`", " ", body)
    body = re.sub(r"https?://\S+", " ", body)[:20000]
    letters = [ch for ch in body if ch.isalpha()]
    if not letters:
        return True
    if sum(1 for ch in letters if _NON_LATIN_RE.match(ch)) / len(letters) > 0.02:
        return False
    lower_letters = 0
    lower_diacritics = 0
    for word in re.findall(r"[^\W\d_]+", body):
        if word and word[0].isupper():
            continue
        lower_letters += sum(1 for ch in word if ch.isalpha())
        lower_diacritics += sum(1 for ch in word if ch in _NON_ENGLISH_DIACRITICS)
    if lower_letters and lower_diacritics / lower_letters > _DIACRITIC_RATIO:
        return False
    return True


# --------------------------------------------------------------------------- #
# Documents
# --------------------------------------------------------------------------- #
@dataclass(frozen=True, slots=True)
class DocToken:
    """One backtick-quoted token occurrence in a document."""

    doc_path: str
    line: int
    token: str
    shape: str  # path | endpoint | symbol | other
    raw_line: str
    stratum: str


def classify_stratum(raw_line: str) -> str:
    """Classify a line as direct_reference / prose_embedded / table_or_listing."""
    s = raw_line.strip()
    if s.startswith("|") and s.count("|") >= 2:
        return "table_or_listing"
    if re.match(r"^(?:[-*+]|\d+[.)])\s", s):
        return "table_or_listing"
    words = re.findall(r"[A-Za-z]{2,}", s)
    return "prose_embedded" if len(words) >= 8 else "direct_reference"


def classify_token(token: str) -> str:
    """Shape of a backtick token: path / endpoint / symbol / other."""
    t = token.strip()
    if not t or any(ch.isspace() for ch in t):
        return "other"
    if t.startswith("/"):
        return "endpoint"
    if _DOTTED_RE.fullmatch(t) or _CALL_RE.fullmatch(t):
        return "symbol"
    if "/" in t or t.endswith("/") or _FILE_EXT_RE.search(t):
        return "path"
    return "other"


def iter_doc_texts(root: Path, english_only: bool = True) -> list[tuple[str, str]]:
    """Documentation files under ``root`` as ``(rel_path, text)``.

    ``english_only`` (default) skips localized copies and non-English text, so
    injection targets never land in documents the engine's English-only corpus
    scope excludes.
    """
    root = Path(root)
    out: list[tuple[str, str]] = []
    for dirpath, _dirnames, filenames in _walk(root):
        base = dirpath.relative_to(root).as_posix()
        base = "" if base == "." else base + "/"
        for filename in sorted(filenames):
            if not filename.lower().endswith(DOC_SUFFIXES):
                continue
            rel = base + filename
            low = rel.lower()
            if any(m in low for m in HISTORY_MARKERS):
                continue
            if english_only and is_translation_path(rel):
                continue
            try:
                text = (dirpath / filename).read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            if english_only and not is_english_document(text):
                continue
            out.append((rel, text))
    return out


def _walk(root: Path):
    """``os.walk``-like generator that prunes SKIP_DIRS and dot directories."""
    import os

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(
            d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")
        )
        yield Path(dirpath), dirnames, filenames


def iter_doc_tokens(docs: list[tuple[str, str]]) -> list[DocToken]:
    """All backtick-quoted token occurrences in ``docs``."""
    tokens: list[DocToken] = []
    for rel, text in docs:
        for lineno, raw_line in enumerate(text.splitlines(), start=1):
            for m in _BACKTICK_RE.finditer(raw_line):
                tok = m.group(1).strip()
                if not tok:
                    continue
                tokens.append(
                    DocToken(
                        doc_path=rel,
                        line=lineno,
                        token=tok,
                        shape=classify_token(tok),
                        raw_line=raw_line,
                        stratum=classify_stratum(raw_line),
                    )
                )
    return tokens


# --------------------------------------------------------------------------- #
# Inventory
# --------------------------------------------------------------------------- #
@dataclass(slots=True)
class SymbolDef:
    """One class/function definition located in a Python file."""

    qualname: str
    name: str
    kind: str  # class | function | method
    file: str
    lineno: int  # the ``def`` / ``class`` line
    end_lineno: int
    start_lineno: int = 0  # first decorator line (<= lineno); for whole-block deletion


@dataclass(slots=True)
class RepoInventory:
    """Generic repository structure built with the standard library."""

    root: Path
    files: set[str] = field(default_factory=set)
    dirs: set[str] = field(default_factory=set)
    basename_count: dict[str, int] = field(default_factory=dict)
    symbols: set[str] = field(default_factory=set)
    defs: list[SymbolDef] = field(default_factory=list)
    modules: set[str] = field(default_factory=set)
    top_packages: set[str] = field(default_factory=set)
    deps: dict[str, str] = field(default_factory=dict)
    dep_file: dict[str, str] = field(default_factory=dict)
    str_literals: dict[str, list[tuple[str, int]]] = field(default_factory=dict)
    py_files: list[str] = field(default_factory=list)

    @property
    def has_python(self) -> bool:
        return bool(self.py_files)


def _module_name(rel: str) -> str:
    rel = rel[: -len(PY_SUFFIX)] if rel.endswith(PY_SUFFIX) else rel
    parts = rel.split("/")
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def _collect_defs(tree: ast.Module, module: str, rel: str, out: list[SymbolDef]) -> None:
    def start_of(node: ast.AST) -> int:
        decos = getattr(node, "decorator_list", [])
        return min([node.lineno, *(d.lineno for d in decos)])

    def walk(node: ast.AST, prefix: str, nested: bool) -> None:
        for child in getattr(node, "body", []):
            if isinstance(child, ast.ClassDef):
                q = f"{prefix}.{child.name}" if prefix else child.name
                out.append(
                    SymbolDef(
                        q, child.name, "class", rel,
                        child.lineno, child.end_lineno or child.lineno, start_of(child),
                    )
                )
                walk(child, q, nested=True)
            elif isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                q = f"{prefix}.{child.name}" if prefix else child.name
                kind = "method" if nested else "function"
                out.append(
                    SymbolDef(
                        q, child.name, kind, rel,
                        child.lineno, child.end_lineno or child.lineno, start_of(child),
                    )
                )

    walk(tree, module, nested=False)


def _split_dep(spec: str) -> tuple[str, str] | None:
    m = _DEP_NAME_RE.match(spec)
    if not m:
        return None
    name = m.group(1)
    return name.lower().replace("_", "-"), spec[len(name) :].strip()


def build_inventory(root: Path) -> RepoInventory:
    """Build the generic structural inventory of a repository."""
    root = Path(root)
    inv = RepoInventory(root=root)

    for dirpath, dirnames, filenames in _walk(root):
        base = dirpath.relative_to(root).as_posix()
        base = "" if base == "." else base
        for d in dirnames:
            inv.dirs.add((base + "/" + d + "/").lstrip("/"))
        for filename in filenames:
            rel = (base + "/" + filename).lstrip("/")
            inv.files.add(rel)
            inv.basename_count[filename] = inv.basename_count.get(filename, 0) + 1
            if filename.endswith(PY_SUFFIX):
                inv.py_files.append(rel)

    _harvest_python(inv)
    _harvest_manifest(inv)
    return inv


def _harvest_python(inv: RepoInventory) -> None:
    root = inv.root
    for rel in sorted(inv.py_files):
        try:
            text = (root / rel).read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        module = _module_name(rel)
        if module:
            inv.modules.add(module.lower())
            inv.top_packages.add(module.split(".")[0].lower())
        try:
            tree = ast.parse(text, filename=rel)
        except SyntaxError:
            continue
        defs: list[SymbolDef] = []
        _collect_defs(tree, module, rel, defs)
        for d in defs:
            inv.defs.append(d)
            inv.symbols.add(d.qualname.lower())
            if "." not in d.qualname:
                inv.symbols.add(d.name.lower())
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str) and node.value:
                inv.str_literals.setdefault(node.value, []).append((rel, node.lineno))


def _harvest_manifest(inv: RepoInventory) -> None:
    root = inv.root
    pyproject = root / "pyproject.toml"
    if pyproject.is_file():
        try:
            data = tomllib.loads(pyproject.read_text(encoding="utf-8", errors="ignore"))
        except (tomllib.TOMLDecodeError, OSError):
            data = {}
        _deps_from_mapping(data.get("project", {}), inv, "pyproject.toml")
        _deps_from_mapping(data.get("tool", {}).get("poetry", {}), inv, "pyproject.toml")

    for req in sorted(root.glob("requirements*.txt")):
        try:
            lines = req.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue
        for spec in lines:
            spec = spec.split("#", 1)[0].strip()
            if not spec or spec.startswith("-"):
                continue
            pair = _split_dep(spec)
            if pair and pair[0] not in inv.deps:
                inv.deps[pair[0]] = pair[1]
                inv.dep_file[pair[0]] = req.name


def _deps_from_mapping(mapping: dict, inv: RepoInventory, file: str) -> None:
    deps = mapping.get("dependencies") if isinstance(mapping, dict) else None
    if isinstance(deps, list):
        for spec in deps:
            if isinstance(spec, str):
                pair = _split_dep(spec)
                if pair:
                    inv.deps.setdefault(pair[0], pair[1])
                    inv.dep_file.setdefault(pair[0], file)
    optional = mapping.get("optional-dependencies") if isinstance(mapping, dict) else None
    if isinstance(optional, dict):
        for group in optional.values():
            if isinstance(group, list):
                for spec in group:
                    pair = _split_dep(spec) if isinstance(spec, str) else None
                    if pair:
                        inv.deps.setdefault(pair[0], pair[1])
                        inv.dep_file.setdefault(pair[0], file)


# --------------------------------------------------------------------------- #
# Resolution
# --------------------------------------------------------------------------- #
def resolve_path(inv: RepoInventory, token: str, doc_path: str) -> str | None:
    """Resolve a documented path token to a repo-relative file or dir key."""
    t = token.strip().strip("`").lstrip("./")
    if not t:
        return None
    if t in inv.files:
        return t
    if t.endswith("/") and t in inv.dirs:
        return t
    rel = (PurePosixPath(doc_path).parent / t).as_posix()
    if rel in inv.files or rel in inv.dirs:
        return rel
    file_hits = [f for f in inv.files if f == t or f.endswith("/" + t)]
    if len(file_hits) == 1:
        return file_hits[0]
    dir_hits = [d for d in inv.dirs if d.endswith("/" + t)]
    if len(dir_hits) == 1:
        return dir_hits[0]
    return None


def resolve_symbol(inv: RepoInventory, token: str) -> list[SymbolDef]:
    """Definitions a documented symbol token resolves to."""
    t = token.strip().strip("`")
    if t.endswith("()"):
        t = t[:-2].strip()
    t = t.lower()
    if not t:
        return []
    out: list[SymbolDef] = []
    for d in inv.defs:
        q = d.qualname.lower()
        if "." in t:
            if q == t or q.endswith("." + t) or t.endswith("." + q):
                out.append(d)
        elif d.name.lower() == t:
            out.append(d)
    return out


def is_unique_basename(inv: RepoInventory, rel: str) -> bool:
    return inv.basename_count.get(Path(rel).name, 0) == 1


def sample(pool: list, n: int, rng) -> list:
    """Deterministic uniform sample of ``n`` items from ``pool``."""
    pool = sorted(pool, key=lambda x: str(x))
    if n <= 0:
        return []
    if len(pool) <= n:
        return list(pool)
    return rng.sample(pool, n)
