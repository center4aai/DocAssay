"""Dependency inventory harvested from the analyzed repository.

The DEPENDENCY predicate's evidence source is the project's own manifests —
``pyproject.toml`` and ``requirements*.txt``. The inventory keeps
the version constraint the manifest actually declares so the exact-version
matching can compare against it (§6.1).
"""

from __future__ import annotations

import ast
import logging
import re
import tomllib
import warnings
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from docassay.data import load_list
from docassay.vocabularies.dependency import normalize_dependency_name
from docassay.vocabularies.structure import SKIPPED_DIRS

_log = logging.getLogger(__name__)

# Generated/vendor directories are pruned from every inventory walk; the
# directories whose manifests are NOT authoritative dependency declarations
# live in ``manifest_non_code_dirs``. (data/structure.json)
_MANIFEST_NON_CODE_DIRS: frozenset[str] = load_list("structure.json", "manifest_non_code_dirs")

# Lock files and the ``source_type`` they stamp on their evidence. A lock file
# describes the *resolved* environment (the transitive closure), not the
# project's declared dependencies: it must NOT close the presence world (a
# transitive package is not a declared dependency) and must NOT extend the
# anchor vocabulary (thousands of transitive names would bloat extraction). Its
# single role is to refine a version: when a manifest declares a dependency but
# pins no version, the resolved lock version is a legitimate witness for a doc
# version claim.
LOCK_SOURCE_TYPES: frozenset[str] = frozenset({"lock:uv", "lock:poetry"})
_LOCK_FILE_SOURCE_TYPES: dict[str, str] = {"uv.lock": "lock:uv", "poetry.lock": "lock:poetry"}

# Directories whose manifests are NOT authoritative dependency declarations.
# The DEPENDENCY world is closed only over the project's own packaging
# manifests (the resolved root or a direct code-root subdirectory such as
# ``src/``/``libs/``/``source/``). Nested test/benchmark/vendor packages and
# build output declare dependencies for *their* environment, not for the
# analyzed project — harvesting them turns an undeclared dependency into a
# false SUPPORTED (observed 2026-09-01: scipy's nested
# ``tests/_cython_examples/ilp64_test_package/pyproject.toml`` declares the
# project's own name "scipy" as a dependency). (data/structure.json)

_NAME_SPEC_RE = re.compile(r"^([A-Za-z0-9][A-Za-z0-9._-]*)\s*(.*)$")


@dataclass(frozen=True, slots=True)
class DependencyEvidence:
    """One manifest-declared dependency, with the raw version constraint.

    ``snippet`` is the source line text the declaration came from, so a verdict
    can show the reviewer exactly what the manifest says.
    """

    evidence_id: str
    package_name: str
    version_spec: str
    source_file: str
    source_type: str
    domain: str = ""
    line_start: int | None = None
    line_end: int | None = None
    snippet: str = ""

    @property
    def object(self) -> str:
        """The normalized referent key that groups evidence with claims."""
        return self.package_name


def build_dependency_inventory(project_root: Path) -> list[DependencyEvidence]:
    """Collect dependency declarations from every manifest in the tree.

    Sources: ``pyproject.toml`` (PEP 621 ``project``, PEP 735
    ``dependency-groups``, Poetry ``[tool.poetry.dependencies]`` and groups),
    ``setup.cfg``/``setup.py``, ``requirements*.txt`` (root or a
    ``requirements/`` directory), plus the resolved versions from ``uv.lock`` /
    ``poetry.lock`` (refinement only — see ``LOCK_SOURCE_TYPES``).
    """
    evidence: list[DependencyEvidence] = []
    for path, rel in iter_manifest_files(project_root):
        if path.name == "pyproject.toml":
            _extract_pyproject(evidence, path, rel)
        elif path.name == "setup.cfg":
            _extract_setup_cfg_dependencies(evidence, path, rel)
        elif path.name == "setup.py":
            _extract_setup_py_dependencies(evidence, path, rel)
        else:
            _extract_requirements(evidence, path, rel)
    for path, rel in _iter_lock_files(project_root):
        _extract_lock(evidence, path, rel)
    own_names = _own_distribution_names(project_root)
    if own_names:
        evidence = [e for e in evidence if e.package_name not in own_names]
    return _dedupe(evidence)


def _own_distribution_names(project_root: Path) -> frozenset[str]:
    """The project's own distribution name(s), normalized.

    A sub-manifest that declares the project's own package as a dependency (a
    monorepo plugin depending on the core package) must not make the project
    name an anchor in its own docs — otherwise prose about the project
    ("[SQLFluff 2.0.0 and later]") is refuted against a plugin's version pin.
    """
    names: set[str] = set()

    def add(raw: object) -> None:
        if isinstance(raw, str) and raw.strip():
            names.add(normalize_dependency_name(raw))

    for path, rel in iter_manifest_files(project_root):
        if rel != path.name:  # root manifest only
            continue
        if path.name == "pyproject.toml":
            try:
                data = tomllib.loads(path.read_text(encoding="utf-8-sig"))
            except (OSError, ValueError):
                continue
            add((data.get("project") or {}).get("name"))
            add(((data.get("tool") or {}).get("poetry") or {}).get("name"))
        elif path.name == "setup.cfg":
            for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
                m = re.match(r"^\s*name\s*=\s*(.+?)\s*$", line)
                if m:
                    add(m.group(1))
                    break
    return frozenset(names)


def iter_manifest_files(project_root: Path):
    found: list[tuple[Path, str]] = []
    for dirpath, dirnames, filenames in Path(project_root).walk():
        dirnames[:] = sorted(d for d in dirnames if d not in SKIPPED_DIRS and not d.startswith("."))
        rel_dir = dirpath.relative_to(project_root)
        base = "" if rel_dir == Path(".") else rel_dir.as_posix() + "/"
        for filename in sorted(filenames):
            is_manifest = filename in ("pyproject.toml", "setup.cfg", "setup.py")
            is_requirements = filename.endswith(".txt") and (
                filename.startswith("requirements") or rel_dir.name == "requirements"
            )
            if not (is_manifest or is_requirements):
                continue
            if not _is_authoritative_manifest_dir(rel_dir):
                continue
            found.append((dirpath / filename, base + filename))
    return found


def _iter_lock_files(project_root: Path):
    """The lock files at the project root, as ``(path, rel)``."""
    found: list[tuple[Path, str]] = []
    for name in _LOCK_FILE_SOURCE_TYPES:
        path = project_root / name
        if path.is_file():
            found.append((path, name))
    return found


def _is_authoritative_manifest_dir(rel_dir: Path) -> bool:
    """Whether a manifest in ``rel_dir`` declares deps for the analyzed project.

    Authoritative manifests live at the resolved root or in a direct code-root
    subdirectory (``src/``, ``libs/core``, ``source/``) — at most two levels
    down — and never inside a well-known non-code directory (``tests/``,
    ``docs/``, ``subprojects/``, build output). Deeper or nested manifests
    describe their own package's environment, not the project's, so they are
    not dependency evidence.
    """
    if len(rel_dir.parts) > 2:
        return False
    return not any(part in _MANIFEST_NON_CODE_DIRS for part in rel_dir.parts)


_TOML_HEADER_RE = re.compile(r"^\s*\[\[?\s*([^\[\]]+?)\s*\]\]?\s*(?:#.*)?$")


def _toml_table_lines(lines: list[str]) -> dict[str, list[int]]:
    """Line indices of each TOML table body, keyed by the normalized header.

    ``""`` holds the lines before the first header. A table's body runs from
    its header to the next header; sub-tables are separate keys.
    """
    tables: dict[str, list[int]] = {"": []}
    current = ""
    for i, line in enumerate(lines):
        match = _TOML_HEADER_RE.match(line)
        if match:
            current = re.sub(r"[\s\"']", "", match.group(1))
            tables.setdefault(current, [])
            continue
        tables[current].append(i)
    return tables


def read_toml_text(path: Path) -> str:
    """A TOML manifest's text; a UTF-8 byte-order mark is dropped."""
    return path.read_text(encoding="utf-8-sig")


def _extract_pyproject(evidence: list[DependencyEvidence], path: Path, rel: str) -> None:
    try:
        raw = read_toml_text(path)
        data = tomllib.loads(raw)
    except OSError:
        return
    except ValueError as exc:
        _log.warning("manifest not parsed: %s: %s", rel, exc)
        return
    lines = raw.splitlines()
    tables = _toml_table_lines(lines)

    # tomllib exposes no source positions, so each declared requirement is
    # located by a deterministic scan of the raw lines of its own table (the
    # first of ``names`` present; the whole file when none is). Within one
    # table the search resumes at the previous hit's line, mirroring the order
    # of the parsed list and allowing several entries on one line. The located
    # line text doubles as the evidence snippet.
    def finder(*names: str) -> Callable[[str], tuple[int | None, str]]:
        scope = next((tables[name] for name in names if tables.get(name)), list(range(len(lines))))
        cursor: list[int] = [0]

        def find_line(needle: str) -> tuple[int | None, str]:
            # A requirement is a whole quoted string (``"towncrier"``), so a
            # longer name containing it (``"sphinxcontrib-towncrier"``) is not
            # taken; a bare substring is the fallback for other shapes.
            for candidates in ((f'"{needle}"', f"'{needle}'"), (needle,)):
                for pos in range(cursor[0], len(scope)):
                    i = scope[pos]
                    if any(c in lines[i] for c in candidates):
                        cursor[0] = pos
                        return i + 1, lines[i].strip()
            return None, ""

        return find_line

    project = data.get("project")
    if isinstance(project, dict):
        requires_python = project.get("requires-python")
        if isinstance(requires_python, str) and requires_python.strip():
            line, snippet = finder("project")(requires_python.strip())
            evidence.append(
                DependencyEvidence(
                    evidence_id=f"python:{rel}:{requires_python.strip()}",
                    package_name="python",
                    version_spec=requires_python.strip(),
                    source_file=rel,
                    source_type="requires-python",
                    line_start=line,
                    line_end=line,
                    snippet=snippet,
                )
            )
        _extract_dep_list(
            evidence, project.get("dependencies"), rel, "dependencies", finder("project")
        )
        optional = project.get("optional-dependencies")
        if isinstance(optional, dict):
            find_optional = finder("project.optional-dependencies", "project")
            for group, deps in optional.items():
                _extract_dep_list(evidence, deps, rel, f"optional:{group}", find_optional)

    build_system = data.get("build-system")
    if isinstance(build_system, dict):
        _extract_dep_list(
            evidence, build_system.get("requires"), rel, "build-system", finder("build-system")
        )

    # PEP 735 dependency groups: ``[dependency-groups]`` maps a group name to a
    # list of PEP 508 requirements (or ``{include-group = ...}`` references).
    groups = data.get("dependency-groups")
    if isinstance(groups, dict):
        find_group = finder("dependency-groups")
        for group, deps in groups.items():
            if isinstance(deps, list):
                _extract_dep_list(evidence, deps, rel, f"dependency-group:{group}", find_group)

    # Poetry: ``[tool.poetry.dependencies]``, legacy ``dev-dependencies`` and
    # ``[tool.poetry.group.<name>.dependencies]``. Specs are Poetry constraints
    # (``^1.2``, ``~1.2``, ``>=1.2,<2``); ``parse_constraint`` expands ``^``/
    # ``~=``, so the raw spec is stored.
    poetry = (data.get("tool") or {}).get("poetry")
    if isinstance(poetry, dict):
        _extract_poetry_dep_map(
            evidence,
            poetry.get("dependencies"),
            rel,
            "poetry",
            finder("tool.poetry.dependencies", "tool.poetry"),
        )
        _extract_poetry_dep_map(
            evidence,
            poetry.get("dev-dependencies"),
            rel,
            "poetry-dev",
            finder("tool.poetry.dev-dependencies", "tool.poetry"),
        )
        poetry_groups = poetry.get("group")
        if isinstance(poetry_groups, dict):
            for group, group_value in poetry_groups.items():
                if isinstance(group_value, dict):
                    _extract_poetry_dep_map(
                        evidence,
                        group_value.get("dependencies"),
                        rel,
                        f"poetry-group:{group}",
                        finder(
                            f"tool.poetry.group.{group}.dependencies",
                            f"tool.poetry.group.{group}",
                        ),
                    )


def _extract_poetry_dep_map(
    evidence: list[DependencyEvidence],
    deps: object,
    rel: str,
    source_type: str,
    find_line: Callable[[str], tuple[int | None, str]],
) -> None:
    """Poetry dependency tables: ``name = "spec"`` or ``name = {version = ...}``."""
    if not isinstance(deps, dict):
        return
    for name, spec in deps.items():
        if not isinstance(name, str) or not name.strip():
            continue
        if isinstance(spec, str):
            version = spec.strip()
        elif isinstance(spec, dict):
            raw = spec.get("version")
            version = raw.strip() if isinstance(raw, str) else ""
        else:
            version = ""
        canonical = normalize_dependency_name(name)
        line, snippet = find_line(f"{name} =")
        evidence.append(
            DependencyEvidence(
                evidence_id=f"{canonical}:{rel}:{version or 'any'}",
                package_name=canonical,
                version_spec=version,
                source_file=rel,
                source_type=source_type,
                line_start=line,
                line_end=line,
                snippet=snippet,
            )
        )


def _extract_dep_list(
    evidence: list[DependencyEvidence],
    deps: object,
    rel: str,
    source_type: str,
    find_line: Callable[[str], tuple[int | None, str]],
) -> None:
    if not isinstance(deps, list):
        return
    for entry in deps:
        if not isinstance(entry, str):
            continue
        name, spec = _split_name_spec(entry)
        if not name:
            continue
        line, snippet = find_line(entry)
        evidence.append(
            DependencyEvidence(
                evidence_id=f"{name}:{rel}:{spec or 'any'}",
                package_name=name,
                version_spec=spec,
                source_file=rel,
                source_type=source_type,
                line_start=line,
                line_end=line,
                snippet=snippet,
            )
        )


def _extract_requirements(evidence: list[DependencyEvidence], path: Path, rel: str) -> None:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return
    for line_no, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith(("-", "--")):
            continue
        name, spec = _split_name_spec(stripped)
        if not name:
            continue
        evidence.append(
            DependencyEvidence(
                evidence_id=f"{name}:{rel}:{spec or 'any'}",
                package_name=name,
                version_spec=spec,
                source_file=rel,
                source_type="requirements",
                line_start=line_no,
                line_end=line_no,
                snippet=stripped,
            )
        )


def _extract_setup_cfg_dependencies(
    evidence: list[DependencyEvidence], path: Path, rel: str
) -> None:
    """``install_requires`` / ``extras_require`` lists from ``setup.cfg``.

    A value may be inline (``install_requires = numpy>=1``) or an indented
    newline-separated block; ``[options.extras_require]`` keys are groups.
    """
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return
    section = ""
    collecting: str | None = None
    for line_no, raw in enumerate(lines, start=1):
        stripped = raw.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            section = stripped[1:-1].strip().lower()
            collecting = None
            continue
        if section not in ("options", "options.extras_require"):
            continue
        key_match = re.match(r"([A-Za-z0-9_.-]+)\s*=\s*(.*)$", stripped)
        if key_match:
            key, inline = key_match.group(1), key_match.group(2).strip()
            if section == "options.extras_require":
                collecting = f"extra:{key}"
            elif key == "install_requires":
                collecting = "install_requires"
            else:
                collecting = None
            if collecting and inline:
                _append_requirement(evidence, inline, rel, collecting, line_no)
            continue
        if collecting and stripped and not stripped.startswith("#"):
            _append_requirement(evidence, stripped, rel, collecting, line_no)


def _append_requirement(
    evidence: list[DependencyEvidence], entry: str, rel: str, source_type: str, line_no: int
) -> None:
    name, spec = _split_name_spec(entry)
    if not name:
        return
    evidence.append(
        DependencyEvidence(
            evidence_id=f"{name}:{rel}:{spec or 'any'}:{line_no}",
            package_name=name,
            version_spec=spec,
            source_file=rel,
            source_type=source_type,
            line_start=line_no,
            line_end=line_no,
            snippet=entry,
        )
    )


def _extract_setup_py_dependencies(
    evidence: list[DependencyEvidence], path: Path, rel: str
) -> None:
    """Literal ``install_requires`` / ``extras_require`` lists from ``setup.py``."""
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", SyntaxWarning)
            tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
    except (OSError, SyntaxError):
        return
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        for keyword in node.keywords:
            if keyword.arg in ("install_requires", "tests_require") and isinstance(
                keyword.value, (ast.List, ast.Tuple)
            ):
                _emit_setup_py_list(evidence, keyword.value.elts, rel, keyword.arg)
            elif keyword.arg in ("extras_require",) and isinstance(keyword.value, ast.Dict):
                for value in keyword.value.values:
                    if isinstance(value, (ast.List, ast.Tuple)):
                        _emit_setup_py_list(evidence, value.elts, rel, "extras_require")


def _emit_setup_py_list(
    evidence: list[DependencyEvidence], elements: list[ast.expr], rel: str, source_type: str
) -> None:
    for element in elements:
        if not isinstance(element, ast.Constant) or not isinstance(element.value, str):
            continue
        name, spec = _split_name_spec(element.value)
        if not name:
            continue
        line = getattr(element, "lineno", None)
        evidence.append(
            DependencyEvidence(
                evidence_id=f"{name}:{rel}:{spec or 'any'}:{line}",
                package_name=name,
                version_spec=spec,
                source_file=rel,
                source_type=source_type,
                line_start=line,
                line_end=line,
                snippet=element.value,
            )
        )


def _extract_lock(evidence: list[DependencyEvidence], path: Path, rel: str) -> None:
    """Resolved ``name``/``version`` pairs from ``uv.lock`` / ``poetry.lock``.

    Both lock formats serialize as a top-level ``package`` array of tables with
    ``name`` and ``version`` keys. Evidence is refinement-only (see
    ``LOCK_SOURCE_TYPES``): the pipeline never extends the anchor set from it
    and the predicate never closes presence on it.
    """
    source_type = _LOCK_FILE_SOURCE_TYPES.get(path.name, "lock")
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError):
        return
    packages = data.get("package")
    if not isinstance(packages, list):
        return
    for package in packages:
        if not isinstance(package, dict):
            continue
        name = package.get("name")
        version = package.get("version")
        if not isinstance(name, str) or not isinstance(version, str):
            continue
        if not name.strip() or not version.strip():
            continue
        canonical = normalize_dependency_name(name)
        evidence.append(
            DependencyEvidence(
                evidence_id=f"{canonical}:{rel}:{version.strip()}",
                package_name=canonical,
                version_spec=f"=={version.strip()}",
                source_file=rel,
                source_type=source_type,
                snippet=f"{name}=={version.strip()}",
            )
        )


def _split_name_spec(entry: str) -> tuple[str, str]:
    """Split ``name[extra] (>=1.2,<2) ; marker`` into (name, spec)."""
    head = entry.split(";", 1)[0].strip()
    head = re.sub(r"\[[^\]]*\]", "", head)
    match = _NAME_SPEC_RE.match(head)
    if not match:
        return "", ""
    name = normalize_dependency_name(match.group(1))
    spec = match.group(2).strip()
    if spec.startswith("(") and spec.endswith(")"):
        spec = spec[1:-1].strip()
    return name, spec


def _dedupe(evidence: list[DependencyEvidence]) -> list[DependencyEvidence]:
    seen: set[str] = set()
    out: list[DependencyEvidence] = []
    for item in evidence:
        if item.evidence_id in seen:
            continue
        seen.add(item.evidence_id)
        out.append(item)
    return out
