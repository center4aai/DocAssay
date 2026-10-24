"""Symbol inventory harvested from the analyzed repository.

The SYMBOL_EXISTS predicate's evidence source is the project's own Python AST
: every importable module, class, function, method and field. The
AST is complete for the project's own tree, which is what makes the structure
world CLOSED over project: a claim about a project symbol that is not in the
inventory is REFUTED. A claimed dotted name whose top segment is not a
project-owned top-level package is a third-party module and stays NEI.
"""

from __future__ import annotations

import ast
import functools
import hashlib
import json
import os
import re
import tomllib
import warnings
from dataclasses import dataclass
from pathlib import Path

from docassay.data import load_list
from docassay.evidence.git import tracked_subdirs
from docassay.vocabularies.structure import SKIPPED_DIRS

# AST-inventory cache. The parsed symbol inventory is deterministic for an
# unchanged tree, so a run can reuse the previous run's result instead of
# re-parsing every source file. The cache lives in the user's cache directory
# (keyed by a hash of the resolved project root), never inside the analyzed
# tree: writing ``<repo>/.docassay_cache/`` changed the listing between runs
# and violated the "tracked snapshot" contract.
_CACHE_VERSION = 3


# Source suffixes the AST inventory reads/parses. A change to any of these
# invalidates the cached inventory.
_SOURCE_SUFFIXES = (".py", ".pyi", ".pyx", ".pxd")

# Compiled extension-module suffixes (and pyo3 Rust sources): the Python-visible
# surface they carry is opaque to the AST inventory, so a module that exists
# only as one of these is a "compiled/generated surface" whose absence must not
# refute.
_COMPILED_SUFFIXES = (".pyd", ".so", ".dylib", ".dll", ".rs")

KIND_MODULE = "module"
KIND_CLASS = "class"
KIND_FUNCTION = "function"
KIND_METHOD = "method"
KIND_FIELD = "field"
KIND_REEXPORT = "reexport"

# Well-known non-code directories. Even when they hold a stray package or a
# Python file, they are not import roots (``examples/``, ``docs/``, ``tests/``):
# treating them as code roots turns example scripts into project top-level
# modules (``examples/app/myapp.py`` → ``app.myapp``) and pollutes the
# top-level set that bounds the third-party carve-out. (data/structure.json)
_NON_CODE_DIRS: frozenset[str] = load_list("structure.json", "non_code_dirs")


@dataclass(frozen=True, slots=True)
class SymbolEvidence:
    """One symbol in the project tree (module, class, function, method, field).

    ``snippet`` is the source line text of the symbol's definition, so a verdict
    can show the reviewer exactly what the code declares.
    """

    evidence_id: str
    name: str
    kind: str
    qualified_name: str
    source_file: str
    line: int
    domain: str = ""
    line_start: int | None = None
    line_end: int | None = None
    snippet: str = ""

    @property
    def object(self) -> str:
        """The normalized referent key that groups evidence with claims."""
        return self.name


def build_symbol_inventory(project_root: Path, kind: str | None = None) -> list[SymbolEvidence]:
    """Every ``kind`` symbol in the project tree (all kinds when ``None``)."""
    all_symbols = _symbols_for_root(str(project_root.resolve()))
    if kind is None:
        return list(all_symbols)
    return [s for s in all_symbols if s.kind == kind]


def has_project_python(project_root: Path) -> bool:
    """Whether the tree contains at least one importable Python module.

    The structure world is CLOSED only when the AST inventory is complete for
    the project's own tree; when no importable module exists (docs-only or a
    non-Python tree), absence must not refute — see ``Predicate.world_holds``.
    """
    return any(s.kind == KIND_MODULE for s in _symbols_for_root(str(project_root.resolve())))


def _walk_dirs(project_root: Path, dirpath: Path, dirnames: list[str]) -> None:
    """Prune the subdirectories to descend into for one walk step.

    For a git checkout the tracked snapshot decides: a
    directory with no tracked file is pruned, so real tracked source under a
    gitignore-named directory (``env/``) is kept while build scratch is not.
    A git-less tree keeps the ``SKIPPED_DIRS`` union and hidden-dir guard.
    """
    tracked = tracked_subdirs(project_root, dirpath, dirnames)
    if tracked is not None:
        dirnames[:] = tracked
    else:
        dirnames[:] = [d for d in dirnames if d not in SKIPPED_DIRS and not d.startswith(".")]


def _source_fingerprint(project_root: Path) -> tuple[tuple[str, int, int], ...]:
    """Stable fingerprint of the tree's source files.

    Returns a sorted tuple of ``(rel_path, mtime_ns, size)`` for every source
    file the AST inventory reads. Any add/remove/change of a source file
    changes the fingerprint and invalidates the disk cache. Only the cheap
    ``stat`` calls are made here — no parsing.
    """
    entries: list[tuple[str, int, int]] = []
    for dirpath, dirnames, filenames in project_root.walk():
        _walk_dirs(project_root, dirpath, dirnames)
        for filename in filenames:
            if filename.startswith("."):
                continue
            if not filename.endswith(_SOURCE_SUFFIXES + _COMPILED_SUFFIXES):
                continue
            path = dirpath / filename
            try:
                st = path.stat()
            except OSError:
                continue
            rel = path.relative_to(project_root).as_posix()
            entries.append((rel, st.st_mtime_ns, st.st_size))
    return tuple(sorted(entries))


def cache_file(project_root: Path) -> Path:
    """User-cache path for a project root: ``<cache>/docassay/<sha>.json``.

    The key is a stable hash of the resolved root, so the same checkout always
    hits the same cache file while different trees never collide. Honors
    ``XDG_CACHE_HOME``; falls back to ``~/.cache`` on POSIX.
    """
    base = os.environ.get("XDG_CACHE_HOME") or str(Path.home() / ".cache")
    digest = hashlib.sha256(str(project_root.resolve()).encode("utf-8")).hexdigest()[:24]
    return Path(base) / "docassay" / f"symbols-{digest}.json"


def _load_symbols_cached(
    project_root: Path, fingerprint: tuple[tuple[str, int, int], ...]
) -> tuple[SymbolEvidence, ...]:
    """Symbol inventory, reusing the repo-local disk cache when valid.

    On a cache hit the parsed inventory is restored without re-parsing the
    tree; on a miss (no cache, or the source fingerprint changed) it is rebuilt
    and written back. A corrupt or unreadable cache is treated as a miss.
    ``fingerprint`` is passed in by the caller (computed once per analysis) so
    the in-memory cache key includes it.
    """
    cache_path = cache_file(project_root)
    cached = None
    if cache_path.is_file():
        try:
            data = json.loads(cache_path.read_text(encoding="utf-8"))
            if (
                isinstance(data, dict)
                and data.get("version") == _CACHE_VERSION
                and data.get("root") == str(project_root.resolve())
                and data.get("fingerprint") == [list(e) for e in fingerprint]
            ):
                cached = data.get("symbols")
        except (OSError, ValueError):
            cached = None
    if cached is not None:
        try:
            return tuple(_symbol_from_json(entry) for entry in cached)
        except (TypeError, KeyError):
            pass

    evidence = tuple(_walk_symbols(project_root))
    try:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(
            json.dumps(
                {
                    "version": _CACHE_VERSION,
                    "root": str(project_root.resolve()),
                    "fingerprint": list(fingerprint),
                    "symbols": [_symbol_to_json(s) for s in evidence],
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
    except OSError:
        pass
    return evidence


def _symbol_to_json(s: SymbolEvidence) -> dict:
    return {
        "evidence_id": s.evidence_id,
        "name": s.name,
        "kind": s.kind,
        "qualified_name": s.qualified_name,
        "source_file": s.source_file,
        "line": s.line,
        "line_start": s.line_start,
        "line_end": s.line_end,
        "snippet": s.snippet,
    }


def _symbol_from_json(entry: dict) -> SymbolEvidence:
    return SymbolEvidence(
        evidence_id=entry["evidence_id"],
        name=entry["name"],
        kind=entry["kind"],
        qualified_name=entry["qualified_name"],
        source_file=entry["source_file"],
        line=entry["line"],
        line_start=entry.get("line_start"),
        line_end=entry.get("line_end"),
        snippet=entry.get("snippet", ""),
    )


@functools.lru_cache(maxsize=32)
def symbols_cached(
    project_root: Path, fingerprint: tuple[tuple[str, int, int], ...]
) -> tuple[SymbolEvidence, ...]:
    return _load_symbols_cached(project_root, fingerprint)


def _symbols_for_root(root_str: str) -> tuple[SymbolEvidence, ...]:
    root = Path(root_str)
    # The cache key includes the tree fingerprint, so a source-file change
    # (add/remove/edit) yields a new key and a fresh parse even when the disk
    # cache is unchanged — the web process must not serve a stale AST
    # inventory after the repository changes (B19).
    return symbols_cached(root, _source_fingerprint(root))


def _has_non_code_ancestor(path: Path, project_root: Path) -> bool:
    """Whether any ancestor of ``path`` up to ``project_root`` is a non-code dir.

    The non-code check used to look only at a directory's own name, so a
    ``tests/fixtures/project/`` tree made ``project``/``demo``/``example`` into
    top-level packages and polluted the third-party carve-out.
    A directory inside ``tests/``, ``docs/``, ``examples/``, ``fixtures/`` …
    is not code regardless of its own name.
    """
    try:
        parts = path.relative_to(project_root).parts
    except ValueError:
        return False
    return any(part in _NON_CODE_DIRS for part in parts[:-1])


def _packaging_roots_and_tops(project_root: Path) -> tuple[set[Path], set[str]]:
    """Import roots and top-level package names declared by packaging metadata.

    Reads the resolved root's ``pyproject.toml`` for the four modern backends
    : ``[tool.setuptools.packages.find] where``, hatch wheel
    ``packages``, ``[tool.poetry] packages`` and ``[tool.flit.module] name``.
    Metadata is authoritative where it exists — the heuristic must not turn a
    declared top-level package (``poetry`` under ``src/``) into an import root
    whose subpackages become fake top levels (``console.application``).
    """
    roots: set[Path] = set()
    tops: set[str] = set()
    pyproject = project_root / "pyproject.toml"
    if not pyproject.is_file():
        return roots, tops
    try:
        data = tomllib.loads(pyproject.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError):
        return roots, tops
    tool = data.get("tool") or {}
    setuptools = tool.get("setuptools") or {}
    if isinstance(setuptools, dict):
        packages = setuptools.get("packages") or {}
        if isinstance(packages, dict):
            find = packages.get("find") or {}
            if isinstance(find, dict):
                for where in find.get("where") or ["."]:
                    if isinstance(where, str) and where.strip():
                        roots.add((project_root / where.strip()).resolve())
    hatch = tool.get("hatch") or {}
    wheel = (hatch.get("build") or {}).get("targets", {}).get("wheel") or {}
    if isinstance(wheel, dict):
        for entry in wheel.get("packages") or []:
            if isinstance(entry, str) and entry.strip():
                p = Path(entry.strip())
                roots.add((project_root / p.parent).resolve())
                tops.add(p.name)
    poetry = tool.get("poetry") or {}
    if isinstance(poetry, dict):
        for entry in poetry.get("packages") or []:
            if isinstance(entry, str) and entry.strip():
                tops.add(entry.strip().split("/")[-1].split(".")[0])
            elif isinstance(entry, dict):
                include = entry.get("include")
                if isinstance(include, str) and include.strip():
                    tops.add(include.strip().split("/")[-1].split(".")[0])
                where = entry.get("from")
                if isinstance(where, str) and where.strip():
                    roots.add((project_root / where.strip()).resolve())
    flit = tool.get("flit") or {}
    mod = flit.get("module") or {}
    if isinstance(mod, dict):
        name = mod.get("name")
        if isinstance(name, str) and name.strip():
            tops.add(name.strip().split(".")[0])
            roots.add(project_root.resolve())
    return roots, tops


def find_import_roots(project_root: Path) -> list[Path]:
    """The directory roots whose children are importable top-level names.

    An import root is a directory whose children are importable as top-level
    packages/modules: the given root itself, explicit layout dirs (``src``,
    ``lib``, ``libs``), the roots declared by the packaging metadata (REPORT
    P6, B13) and every directory that directly holds an outermost package (a
    package whose parent is not itself a package). The last rule is what makes
    monorepos (``airflow-core/src/airflow``), ``libs/`` layouts
    (``libs/core/langchain_core``), nested integration packages
    (``src/integrations/prefect-dbt/prefect_dbt``) and ``source/``-wrapped
    checkouts resolvable.

    Two guards keep the top-level set honest: a directory is
    not a root when it lies inside a non-code ancestor (``tests/``,
    ``fixtures/``, ``examples/``, ``docs/``, …), and a metadata-declared
    top-level package sitting directly under an already-rooted parent
    (``src/poetry`` with poetry's ``packages = [{include=..., from=src}]``) is
    treated as the package it is, not as another import root.
    """
    metadata_roots, metadata_tops = _packaging_roots_and_tops(project_root)
    roots: set[Path] = {project_root} | metadata_roots
    top_src = project_root / "src"
    for name in ("src", "lib", "libs"):
        candidate = project_root / name
        if candidate.is_dir():
            roots.add(candidate)
    for dirpath, dirnames, _filenames in project_root.walk():
        _walk_dirs(project_root, dirpath, dirnames)
        if (dirpath / "__init__.py").is_file():
            continue
        if _has_non_code_ancestor(dirpath, project_root):
            continue
        if dirpath != project_root and dirpath.name in _NON_CODE_DIRS:
            continue
        # A direct child of a top-level ``src/`` is the standard src-layout
        # top-level package (``src/poetry`` is the ``poetry`` package), never an
        # import root whose subpackages become fake top levels.
        # Nested groupings one level deeper (``src/integrations/prefect-dbt``)
        # still become roots, so monorepo integration packages keep resolving.
        if dirpath.parent == top_src:
            continue
        if dirpath.name in metadata_tops and dirpath.parent in roots:
            continue
        if any((dirpath / d / "__init__.py").is_file() for d in dirnames):
            roots.add(dirpath)
    return sorted(roots, key=lambda p: len(p.parts))


def _walk_symbols(project_root: Path) -> list[SymbolEvidence]:
    evidence: list[SymbolEvidence] = []
    roots = find_import_roots(project_root)
    module_public: dict[str, set[str]] = {}
    module_all: dict[str, set[str]] = {}
    # Parsed trees of importable ``.py``/``.pyi`` modules, keyed by
    # repository-relative path, so the re-export pass reuses them instead of
    # re-reading and re-parsing every file.
    parsed: dict[str, ast.Module] = {}
    for dirpath, dirnames, filenames in project_root.walk():
        _walk_dirs(project_root, dirpath, dirnames)
        _emit_namespace_modules(evidence, dirpath, roots, project_root)
        for filename in sorted(filenames):
            if filename.startswith("."):
                continue
            suffix = Path(filename).suffix
            if suffix in _COMPILED_SUFFIXES:
                _emit_compiled_module(evidence, dirpath, filename, roots, project_root)
                continue
            if suffix not in (".py", ".pyi", ".pyx", ".pxd"):
                continue
            file_path = dirpath / filename
            import_root = _import_root_for(file_path, roots)
            if import_root is None:
                continue
            rel = file_path.relative_to(import_root)
            if not _is_importable(import_root, rel, project_root):
                continue
            rel_project = file_path.relative_to(project_root).as_posix()
            module_dotted = _module_dotted_name(rel)
            if module_dotted:
                _emit_module(evidence, module_dotted, rel_project)
            if suffix == ".pyx" or suffix == ".pxd":
                _emit_cython_symbols(evidence, module_dotted, file_path, rel_project)
                continue
            public, all_names, tree = _emit_symbols(evidence, module_dotted, file_path, rel_project)
            if tree is not None:
                parsed[rel_project] = tree
            if module_dotted:
                if public:
                    module_public[module_dotted] = public
                if all_names:
                    module_all[module_dotted] = all_names
    _emit_reexports(evidence, project_root, roots, module_public, module_all, parsed)
    return evidence


def _emit_reexports(
    evidence: list[SymbolEvidence],
    project_root: Path,
    roots: list[Path],
    module_public: dict[str, set[str]],
    module_all: dict[str, set[str]],
    parsed: dict[str, ast.Module],
) -> None:
    """Record public names re-exported through relative ``from`` imports.

    Real packages build their public API by re-exporting private modules
    (``scipy/signal/__init__.py``: ``from ._support_alternative_backends import
    *``; ``scipy/stats/__init__.py``: ``from ._stats_py import *``,
    ``from ._variation import variation``). The AST inventory only records the
    *definitions* in the private modules, so a claim about the public name
    (``scipy.signal.hilbert``, ``scipy.stats.mode``) would be REFUTED or
    ambiguous. This pass emits an ``alias`` evidence key ``{module}.{public}``
    for every relative import whose target definition exists, iterating to a
    fixpoint so chained re-exports resolve too.

    ``parsed`` maps each importable module's repository-relative path to its
    already-parsed AST (produced once in ``_walk_symbols``), so the fixpoint
    never re-reads or re-parses a file.
    """
    files: list[tuple[Path, str, str, bool]] = []
    for dirpath, dirnames, filenames in project_root.walk():
        _walk_dirs(project_root, dirpath, dirnames)
        for filename in sorted(filenames):
            if filename.startswith(".") or not filename.endswith(".py"):
                continue
            file_path = dirpath / filename
            import_root = _import_root_for(file_path, roots)
            if import_root is None:
                continue
            rel = file_path.relative_to(import_root)
            if not _is_importable(import_root, rel, project_root):
                continue
            rel_project = file_path.relative_to(project_root).as_posix()
            module_dotted = _module_dotted_name(rel)
            if module_dotted:
                files.append((file_path, rel_project, module_dotted, rel.name == "__init__.py"))

    # Iterate to a fixpoint so chained re-exports resolve at any depth. The
    # safety cap guards against pathological import cycles that add one alias
    # per round forever; real packages converge in a handful of rounds.
    for _round in range(64):
        existing = {e.name for e in evidence}
        project_tops = {k.split(".")[0] for k in existing}
        added = 0
        for _file_path, rel_project, module_dotted, is_package in files:
            tree = parsed.get(rel_project)
            if tree is None:
                continue
            for node in _top_level_imports(tree):
                if not isinstance(node, ast.ImportFrom):
                    continue
                if node.level >= 1:
                    target_prefix = _relative_base(module_dotted, is_package, node.level)
                    if target_prefix is None:
                        continue
                    if node.module:
                        target_prefix = ".".join(target_prefix.split(".") + node.module.split("."))
                else:
                    if not node.module or node.module.split(".")[0] not in project_tops:
                        continue
                    target_prefix = node.module
                added += _handle_import_names(
                    module_dotted,
                    node,
                    target_prefix,
                    module_public,
                    module_all,
                    rel_project,
                    evidence,
                    existing,
                )
        if added == 0:
            return


def _top_level_imports(tree: ast.Module):
    """Import nodes at the module's top level, including inside guarded blocks.

    Guarded imports are common in real packages — ``try`` blocks
    (``try: from scipy.__config__ import show as show_config``) and feature-flag
    ``if`` guards (``if not IS_TRACING_SDK_ONLY: from mlflow.client import
    MlflowClient``) — and their re-exported names are still public API. Imports
    inside functions/classes are lazy and do not create module-level names, so
    they are excluded. ``if __name__ == "__main__":`` guards are never API.
    """
    for stmt in tree.body:
        yield from _guarded_imports(stmt)


def _guarded_imports(stmt: ast.stmt):
    """Recurse through top-level ``try``/``if`` guards; stop at functions."""
    if isinstance(stmt, (ast.Import, ast.ImportFrom)):
        yield stmt
    elif isinstance(stmt, ast.Try):
        for block in (stmt.body, stmt.handlers, stmt.orelse, stmt.finalbody):
            for inner in block:
                yield from _guarded_imports(inner)
    elif isinstance(stmt, ast.If) and not _is_main_guard(stmt.test):
        for inner in stmt.body + stmt.orelse:
            yield from _guarded_imports(inner)


def _is_main_guard(test: ast.expr) -> bool:
    """Whether an ``if`` test references ``__name__`` (a ``__main__`` guard)."""
    return any(isinstance(node, ast.Name) and node.id == "__name__" for node in ast.walk(test))


def _handle_import_names(
    module_dotted: str,
    node: ast.ImportFrom,
    target_prefix: str,
    module_public: dict[str, set[str]],
    module_all: dict[str, set[str]],
    rel_project: str,
    evidence: list[SymbolEvidence],
    existing: set[str],
) -> int:
    """One ``from ... import ...`` statement → alias evidence keys.

    The alias is emitted for any name imported from a *project-owned* module:
    the ``__init__`` re-export is source-level truth that the public name
    exists, even when its definition lives in a build-generated module absent
    from the tree (``from scipy.__config__ import show as show_config``).
    """
    added = 0
    for name in node.names:
        if name.name == "*":
            public = module_all.get(target_prefix) or module_public.get(target_prefix)
            for pub in sorted(public or ()):
                added += _add_reexport(
                    module_dotted, pub, f"{target_prefix}.{pub}", rel_project, evidence, existing
                )
        else:
            public = name.asname or name.name
            added += _add_reexport(
                module_dotted,
                public,
                f"{target_prefix}.{name.name}",
                rel_project,
                evidence,
                existing,
            )
    return added


def _relative_base(module_dotted: str, is_package: bool, level: int) -> str | None:
    """The package a relative import of ``level`` dots resolves against.

    Mirrors the importlib rule: ``base = package.rsplit('.', level - 1)[0]``,
    where ``package`` is the importing module's ``__package__`` — the module's
    own package for a submodule, the package itself for an ``__init__.py``.
    ``None`` when the import would escape the project root.
    """
    package = module_dotted if is_package else ".".join(module_dotted.split(".")[:-1])
    parts = package.split(".")
    drop = level - 1
    if drop >= len(parts):
        return None
    return ".".join(parts[: len(parts) - drop])


def _add_reexport(
    module_dotted: str,
    public: str,
    target_key: str,
    rel_project: str,
    evidence: list[SymbolEvidence],
    existing: set[str],
) -> int:
    alias_key = f"{module_dotted}.{public}".lower()
    if alias_key == target_key.lower() or alias_key in existing:
        return 0
    existing.add(alias_key)
    evidence.append(
        SymbolEvidence(
            evidence_id=f"alias:{alias_key}:{rel_project}:0",
            name=alias_key,
            kind=KIND_REEXPORT,
            qualified_name=alias_key,
            source_file=rel_project,
            line=0,
        )
    )
    return 1


def _emit_namespace_modules(
    evidence: list[SymbolEvidence],
    dirpath: Path,
    roots: list[Path],
    project_root: Path,
) -> None:
    """Emit module facts for namespace-package directories (no ``__init__.py``).

    PEP-420 namespace packages (``airflow/datasets`` without an ``__init__.py``)
    are importable when every ancestor up to the import root is a package; the
    directory itself must be a package (a direct ``.py`` file or a child classic
    package — ``src/poetry/`` carries only subpackages yet is the ``poetry``
    namespace package).
    """
    if dirpath == project_root or (dirpath / "__init__.py").is_file():
        return
    import_root = _import_root_for(dirpath, roots)
    if import_root is None or import_root == dirpath:
        return
    if not _is_package_dir(dirpath, project_root):
        return
    rel = dirpath.relative_to(import_root)
    if not rel.parts:
        return
    dotted = _module_dotted_name(rel)
    if dotted:
        _emit_module(evidence, dotted, dirpath.relative_to(project_root).as_posix())


def _import_root_for(path: Path, roots: list[Path]) -> Path | None:
    best: Path | None = None
    for root in roots:
        if path.is_relative_to(root):
            if best is None or len(root.parts) > len(best.parts):
                best = root
    return best


def _is_package_dir(directory: Path, project_root: Path | None = None) -> bool:
    """Whether a directory is a package or namespace package.

    ``__init__.py`` makes a classic package; otherwise the directory is a
    namespace package (PEP 420) when it directly holds a Python file **or** a
    child classic package — ``src/foo/bar/__init__.py`` makes ``foo`` a
    namespace package even though ``foo`` carries no ``.py`` of its own (the
    tool's own ``src/docassay/`` and poetry's ``src/poetry/`` are such
    trees). A well-known non-code directory (``docs/``, ``examples/``,
    ``scripts/``) or a directory inside one — a ``tests/fixtures/*`` subtree —
    is not importable code no matter its own name.
    """
    if (directory / "__init__.py").is_file():
        return True
    if directory.name in _NON_CODE_DIRS:
        return False
    if project_root is not None and _has_non_code_ancestor(directory, project_root):
        return False
    try:
        for entry in directory.iterdir():
            if entry.is_file() and entry.suffix == ".py":
                return True
            if entry.is_dir() and (entry / "__init__.py").is_file():
                return True
    except OSError:
        return False
    return False


def _is_importable(import_root: Path, rel: Path, project_root: Path | None = None) -> bool:
    """Whether a module is reachable by ``import``.

    A file directly under the import root is a top-level module; otherwise every
    directory down to the file must be a (namespace) package.
    """
    if len(rel.parts) == 1:
        return True
    current = import_root
    for part in rel.parts[:-1]:
        current = current / part
        if not _is_package_dir(current, project_root):
            return False
    return True


def _module_dotted_name(rel: Path) -> str:
    """The importable dotted name of a module file relative to its root."""
    if rel.stem == "__init__":
        return ".".join(rel.parts[:-1])
    return ".".join(rel.with_suffix("").parts)


def _emit_module(evidence: list[SymbolEvidence], dotted: str, rel_project: str) -> None:
    evidence.append(
        SymbolEvidence(
            evidence_id=f"module:{dotted}:{rel_project}",
            name=dotted,
            kind=KIND_MODULE,
            qualified_name=dotted,
            source_file=rel_project,
            line=1,
            line_start=1,
            line_end=None,
        )
    )


def _emit_compiled_module(
    evidence: list[SymbolEvidence],
    dirpath: Path,
    filename: str,
    roots: list[Path],
    project_root: Path,
) -> None:
    """Emit an opaque module fact for a compiled extension file (``.pyd``/``.so``).

    The Python-visible surface of a compiled extension is opaque to the AST
    inventory, but the module it *is* (``_speedups`` from
    ``_speedups.cp312-win_amd64.pyd``) is real. Emitting it as a module whose
    source file carries a compiled suffix lets the match layer abstain (NEI)
    on a missing symbol there instead of REFUTING. Only the
    first dot-segment of the stem is used: the rest is the ABI tag.
    """
    import_root = _import_root_for(dirpath, roots)
    if import_root is None:
        return
    if dirpath.name in _NON_CODE_DIRS or _has_non_code_ancestor(dirpath, project_root):
        return
    module = ".".join(dirpath.relative_to(import_root).parts)
    stem_part = filename.split(".", 1)[0]
    dotted = f"{module}.{stem_part}" if module else stem_part
    rel_project = (dirpath / filename).relative_to(project_root).as_posix()
    evidence.append(
        SymbolEvidence(
            evidence_id=f"module:{dotted}:{rel_project}",
            name=dotted,
            kind=KIND_MODULE,
            qualified_name=dotted,
            source_file=rel_project,
            line=1,
            line_start=1,
            line_end=None,
        )
    )


def _is_type_checking_guard(test: ast.expr) -> bool:
    """Whether an ``if`` test is a ``TYPE_CHECKING`` guard.

    Matches ``if TYPE_CHECKING:`` and ``if typing.TYPE_CHECKING:`` — the two
    forms that gate type-only definitions. A runtime-version guard
    (``if sys.version_info >= …``) is not a type guard: its definitions are
    still importable and stay part of the module API.
    """
    if isinstance(test, ast.Name):
        return test.id == "TYPE_CHECKING"
    return (
        isinstance(test, ast.Attribute)
        and test.attr == "TYPE_CHECKING"
        and isinstance(test.value, ast.Name)
        and test.value.id == "typing"
    )


def _emit_scope(
    evidence: list[SymbolEvidence],
    body: list[ast.stmt],
    module_dotted: str,
    scope: str,
    public: set[str],
    all_names: set[str],
    rel_project: str,
    snippet,
) -> None:
    """Emit symbols from one statement list, recursing into nested classes.

    ``scope`` is the qualified name prefix: ``module_dotted`` at module level
    (definitions → module functions/fields), ``module.Class`` inside a class
    (functions → methods, assignments → fields). Nested ``class`` blocks recurse
    so classes inside classes are emitted too. Names only join ``public`` /
    ``__all__`` at module scope.
    """
    in_class = scope != module_dotted
    for node in body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not in_class and not node.name.startswith("_"):
                public.add(node.name)
            _add_symbol(
                evidence,
                KIND_METHOD if in_class else KIND_FUNCTION,
                scope,
                node.name,
                rel_project,
                node.lineno,
                line_end=node.end_lineno or node.lineno,
                snippet=snippet(node.lineno),
            )
        elif isinstance(node, ast.ClassDef):
            if not in_class and not node.name.startswith("_"):
                public.add(node.name)
            _add_symbol(
                evidence,
                KIND_CLASS,
                scope,
                node.name,
                rel_project,
                node.lineno,
                line_end=node.end_lineno or node.lineno,
                snippet=snippet(node.lineno),
            )
            _emit_scope(
                evidence,
                node.body,
                module_dotted,
                f"{scope}.{node.name}",
                public,
                all_names,
                rel_project,
                snippet,
            )
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            for name in _assign_target_names(node):
                if not in_class:
                    if name == "__all__":
                        all_names |= _all_list_values(node)
                    elif not name.startswith("_"):
                        public.add(name)
                _add_symbol(
                    evidence,
                    KIND_FIELD,
                    scope,
                    name,
                    rel_project,
                    node.lineno,
                    line_end=node.end_lineno or node.lineno,
                    snippet=snippet(node.lineno),
                )


def _emit_symbols(
    evidence: list[SymbolEvidence],
    module_dotted: str,
    file_path: Path,
    rel_project: str,
) -> tuple[set[str], set[str], ast.Module | None]:
    """Emit definition symbols; return the module's ``(public_names, __all__,
    tree)``.

    ``public_names`` are top-level definitions not starting with ``_``;
    ``__all__`` is the explicit export list when the module declares one. Both
    feed the re-export pass (``import *`` uses ``__all__`` when present). The
    parsed ``tree`` is returned (or ``None`` on a parse error) so the re-export
    pass can reuse it instead of re-reading and re-parsing the file.

    Emission walks the module body *and* ``if TYPE_CHECKING:`` guards, recursing
    into nested ``class`` scopes: type-only classes and nested classes are part
    of the module's importable surface and must resolve (previously they were
    silent resolution gaps).
    """
    public: set[str] = set()
    all_names: set[str] = set()
    try:
        source_text = file_path.read_text(encoding="utf-8")
        with warnings.catch_warnings():
            # Parsing foreign code can emit SyntaxWarning to stderr; the parse
            # result is what matters, not Python's warnings.
            warnings.simplefilter("ignore", SyntaxWarning)
            tree = ast.parse(source_text)
    except (OSError, UnicodeDecodeError, SyntaxError):
        return public, all_names, None
    source_lines = source_text.splitlines()

    def snippet(lineno: int) -> str:
        if 1 <= lineno <= len(source_lines):
            return source_lines[lineno - 1].strip()
        return ""

    bodies: list[list[ast.stmt]] = [tree.body]
    for node in tree.body:
        if isinstance(node, ast.If) and _is_type_checking_guard(node.test):
            bodies.append(node.body)
    for body in bodies:
        _emit_scope(
            evidence,
            body,
            module_dotted,
            module_dotted,
            public,
            all_names,
            rel_project,
            snippet,
        )
    return public, all_names, tree


def _all_list_values(node: ast.Assign | ast.AnnAssign) -> set[str]:
    """The string members of an ``__all__ = [...]`` assignment (empty otherwise)."""
    if isinstance(node, ast.Assign) and isinstance(node.value, (ast.List, ast.Tuple)):
        return {
            elt.value
            for elt in node.value.elts
            if isinstance(elt, ast.Constant) and isinstance(elt.value, str)
        }
    return set()


# Cython modules define the Python-visible surface with ``def``/``cpdef``
# functions and ``cdef class`` types at column 0. ``cdef``-only functions,
# ``cdef struct``/``enum`` and ``cdef extern`` blocks are C-internal and do not
# produce Python symbols.
_CYTHON_FUNC_RE = re.compile(
    r"^(?:def|cpdef)\s+(?:[A-Za-z_][A-Za-z0-9_.<>]*\s+)*([A-Za-z_]\w*)\s*\("
)
_CYTHON_CLASS_RE = re.compile(r"^cdef\s+class\s+([A-Za-z_]\w*)")


def _emit_cython_symbols(
    evidence: list[SymbolEvidence],
    module_dotted: str,
    file_path: Path,
    rel_project: str,
) -> None:
    """Emit Python-visible symbols from a Cython ``.pyx``/``.pxd`` file."""
    try:
        lines = file_path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return
    for lineno, line in enumerate(lines, start=1):
        m = _CYTHON_CLASS_RE.match(line)
        if m:
            _add_symbol(
                evidence,
                KIND_CLASS,
                module_dotted,
                m.group(1),
                rel_project,
                lineno,
                line_end=lineno,
                snippet=line.strip(),
            )
            continue
        m = _CYTHON_FUNC_RE.match(line)
        if m:
            _add_symbol(
                evidence,
                KIND_FUNCTION,
                module_dotted,
                m.group(1),
                rel_project,
                lineno,
                line_end=lineno,
                snippet=line.strip(),
            )


def _assign_target_names(node: ast.Assign | ast.AnnAssign) -> list[str]:
    targets: list[ast.expr]
    if isinstance(node, ast.Assign):
        targets = list(node.targets)
    elif isinstance(node.target, ast.Name):
        targets = [node.target]
    else:
        return []
    names: list[str] = []
    for target in targets:
        if isinstance(target, ast.Name):
            names.append(target.id)
        elif isinstance(target, (ast.Tuple, ast.List)):
            for elt in target.elts:
                if isinstance(elt, ast.Name):
                    names.append(elt.id)
    return names


def _add_symbol(
    evidence: list[SymbolEvidence],
    kind: str,
    scope: str,
    name: str,
    rel_project: str,
    line: int,
    line_end: int | None = None,
    snippet: str = "",
) -> None:
    qualified = f"{scope}.{name}"
    evidence.append(
        SymbolEvidence(
            evidence_id=f"{kind}:{qualified}:{rel_project}:{line}",
            name=qualified.lower(),
            kind=kind,
            qualified_name=qualified,
            source_file=rel_project,
            line=line,
            line_start=line,
            line_end=line_end,
            snippet=snippet,
        )
    )
