"""Tests for dependency-manifest authority (decided 2026-09-01).

The DEPENDENCY inventory is closed only over the project's own packaging
manifests. A manifest is authoritative when it sits at the resolved root or in
a direct code-root subdirectory (``src/``, ``libs/core``, ``source/``) — at most
two levels down — and never inside a well-known non-code directory. Deeper or
nested manifests (test packages, subprojects, build output) declare
dependencies for *their* environment, so harvesting them would turn an
undeclared dependency into a false SUPPORTED.
"""

from __future__ import annotations

from pathlib import Path

from docassay.core.pipeline import analyze_repository
from docassay.evidence.manifests import (
    LOCK_SOURCE_TYPES,
    build_dependency_inventory,
)


def _english_readme(body: str) -> str:
    return "# Demo project\nThis is the demo project that many teams use every day.\n" + body


def test_root_manifest_is_authoritative(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "demo"\nrequires-python = ">=3.12"\ndependencies = ["numpy>=2.0"]\n'
    )
    by_name = {e.package_name: e.version_spec for e in build_dependency_inventory(tmp_path)}
    assert by_name["numpy"] == ">=2.0"
    assert by_name["python"] == ">=3.12"


def test_libs_core_manifest_is_authoritative(tmp_path: Path) -> None:
    (tmp_path / "libs" / "core").mkdir(parents=True)
    (tmp_path / "libs" / "core" / "pyproject.toml").write_text(
        '[project]\nname = "core"\ndependencies = ["langsmith>=0.1"]\n'
    )
    by_name = {e.package_name for e in build_dependency_inventory(tmp_path)}
    assert "langsmith" in by_name


def test_nested_test_package_manifest_is_not_authoritative(tmp_path: Path) -> None:
    deep = tmp_path / "pkg" / "tests" / "_cython_examples" / "ilp64_test_package"
    deep.mkdir(parents=True)
    (deep / "pyproject.toml").write_text(
        '[project]\nname = "ilp64_test_package"\ndependencies = ["scipy", "numpy"]\n'
    )
    by_name = {e.package_name for e in build_dependency_inventory(tmp_path)}
    assert "scipy" not in by_name
    assert "numpy" not in by_name


def test_subproject_manifest_is_not_authoritative(tmp_path: Path) -> None:
    (tmp_path / "subprojects" / "pyprima").mkdir(parents=True)
    (tmp_path / "subprojects" / "pyprima" / "pyproject.toml").write_text(
        '[project]\nname = "pyprima"\ndependencies = ["pycutest"]\n'
    )
    by_name = {e.package_name for e in build_dependency_inventory(tmp_path)}
    assert "pycutest" not in by_name


def test_nested_only_dependency_is_nei(tmp_path: Path) -> None:
    """A claim about a dependency declared only in a nested test package stays
    NEI — the root manifest does not confirm it."""
    deep = tmp_path / "pkg" / "tests" / "_cython_examples" / "ilp64_test_package"
    deep.mkdir(parents=True)
    (deep / "pyproject.toml").write_text(
        '[project]\nname = "ilp64_test_package"\ndependencies = ["scipy"]\n'
    )
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "demo"\nrequires-python = ">=3.12"\ndependencies = ["numpy>=2.0"]\n'
    )
    (tmp_path / "README.md").write_text(
        _english_readme("The project depends on scipy and uses numpy for its internals.\n")
    )
    result = analyze_repository(tmp_path)
    refs = {r.object: r for r in result.referents if r.predicate_type == "DEPENDENCY"}
    assert refs["scipy"].assertions[0].code_verdict == "NEI"
    assert refs["numpy"].assertions[0].code_verdict == "SUPPORTED"


# --- manifest coverage: Poetry, PEP 735, setup.cfg/setup.py, requirements/ ----
#


def _by_name(inventory) -> dict[str, str]:
    return {e.package_name: e.version_spec for e in inventory}


def test_poetry_dependencies_are_read(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        "[tool.poetry.dependencies]\n"
        'python = ">=3.9"\n'
        'numpy = "^1.26"\n'
        "[tool.poetry.group.dev.dependencies]\n"
        'pytest = ">=7.0"\n'
    )
    by_name = _by_name(build_dependency_inventory(tmp_path))
    assert by_name["python"] == ">=3.9"
    assert by_name["numpy"] == "^1.26"
    assert by_name["pytest"] == ">=7.0"


def test_dependency_groups_are_read(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "demo"\n[dependency-groups]\ndev = ["pytest>=8", "mypy"]\n'
    )
    by_name = _by_name(build_dependency_inventory(tmp_path))
    assert by_name["pytest"] == ">=8"
    assert "mypy" in by_name


def test_setup_cfg_install_requires_is_read(tmp_path: Path) -> None:
    (tmp_path / "setup.cfg").write_text(
        "[metadata]\nname = demo\nversion = 1.0\n"
        "[options]\ninstall_requires =\n    requests>=2.0\n    click\n"
    )
    by_name = _by_name(build_dependency_inventory(tmp_path))
    assert by_name["requests"] == ">=2.0"
    assert "click" in by_name


def test_setup_py_install_requires_is_read(tmp_path: Path) -> None:
    (tmp_path / "setup.py").write_text(
        "from setuptools import setup\n"
        "setup(\n"
        '    name="demo",\n'
        '    install_requires=["numpy>=1.26", "requests"],\n'
        ")\n"
    )
    by_name = _by_name(build_dependency_inventory(tmp_path))
    assert by_name["numpy"] == ">=1.26"
    assert "requests" in by_name


def test_requirements_directory_is_read(tmp_path: Path) -> None:
    (tmp_path / "requirements").mkdir()
    (tmp_path / "requirements" / "base.txt").write_text("numpy>=1.26\n")
    (tmp_path / "requirements" / "dev.txt").write_text("pytest>=8\n")
    by_name = _by_name(build_dependency_inventory(tmp_path))
    assert by_name["numpy"] == ">=1.26"
    assert by_name["pytest"] == ">=8"


def test_lock_evidence_is_marked_refinement_only(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "demo"\ndependencies = ["numpy"]\n')
    (tmp_path / "uv.lock").write_text(
        'version = 1\n[[package]]\nname = "numpy"\nversion = "2.1.0"\n'
        '[[package]]\nname = "transitive-only"\nversion = "9.9.9"\n'
    )
    inventory = build_dependency_inventory(tmp_path)
    lock = [
        e for e in inventory if e.package_name == "numpy" and e.source_type in LOCK_SOURCE_TYPES
    ]
    assert [e.version_spec for e in lock] == ["==2.1.0"]
    # A package that appears only in the lock is transitive: it must not extend
    # the scan anchor vocabulary (no claim can anchor it).
    (tmp_path / "README.md").write_text(
        "# Demo project that many teams use every day.\n"
        "The project depends on transitive-only for its internals.\n"
    )
    result = analyze_repository(tmp_path)
    objects = {r.object for r in result.referents if r.predicate_type == "DEPENDENCY"}
    assert "transitive-only" not in objects


def test_lock_only_dependency_presence_is_nei(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "demo"\n')
    (tmp_path / "uv.lock").write_text('version = 1\n[[package]]\nname = "idna"\nversion = "3.6"\n')
    (tmp_path / "README.md").write_text(
        "# Demo project that many teams use every day.\nThe project uses idna.\n"
    )
    result = analyze_repository(tmp_path)
    refs = {r.object: r for r in result.referents if r.predicate_type == "DEPENDENCY"}
    assert refs["idna"].assertions[0].code_verdict == "NEI"


def test_project_is_not_its_own_dependency(tmp_path: Path) -> None:
    # A monorepo plugin declaring the core package must not make the project
    # name an anchor in its own docs.
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "corepkg"\nversion = "2.0.0"\n')
    (tmp_path / "plugins" / "extra").mkdir(parents=True)
    (tmp_path / "plugins" / "extra" / "pyproject.toml").write_text(
        '[project]\nname = "extra"\ndependencies = ["corepkg>=1.0", "requests"]\n'
    )
    by_name = _by_name(build_dependency_inventory(tmp_path))
    assert "corepkg" not in by_name
    assert "requests" in by_name


def test_line_numbers_follow_each_toml_table(tmp_path: Path) -> None:
    # ``[build-system]`` before ``[project]`` and two requirements on one line:
    # every declared requirement keeps its own source line.
    (tmp_path / "pyproject.toml").write_text(
        '[build-system]\nrequires = ["setuptools>=61", "wheel"]\n'
        'build-backend = "setuptools.build_meta"\n\n'
        '[project]\nname = "demo"\nrequires-python = ">=3.10"\n'
        'dependencies = ["numpy>=1.26", "requests>=2.31"]\n'
    )
    lines = {e.package_name: e.line_start for e in build_dependency_inventory(tmp_path)}
    assert lines == {"setuptools": 2, "wheel": 2, "python": 7, "numpy": 8, "requests": 8}


def test_manifest_with_byte_order_mark_is_read(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '\ufeff[project]\nname = "demo"\ndependencies = ["requests>=2.31"]\n', encoding="utf-8"
    )
    (tmp_path / "demo").mkdir()
    (tmp_path / "demo" / "__init__.py").write_text("")
    (tmp_path / "README.md").write_text(
        _english_readme("This project requires requests 2.28 or newer.\n")
    )
    assert _by_name(build_dependency_inventory(tmp_path))["requests"] == ">=2.31"
    result = analyze_repository(tmp_path)
    verdicts = {
        r.object: r.assertions[0].code_verdict
        for r in result.referents
        if r.predicate_type == "DEPENDENCY"
    }
    assert verdicts["requests"] == "REFUTED"


def test_line_number_prefers_whole_quoted_requirement(tmp_path: Path) -> None:
    # ``towncrier`` must not land on the ``sphinxcontrib-towncrier`` line.
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "demo"\n\n[project.optional-dependencies]\n'
        'docs = [\n  "sphinxcontrib-towncrier",\n  "towncrier",\n]\n'
    )
    lines = {e.package_name: e.line_start for e in build_dependency_inventory(tmp_path)}
    assert lines["sphinxcontrib-towncrier"] == 6
    assert lines["towncrier"] == 7
