"""Tests for code-root discovery and the structure world guard.

``find_import_roots`` must locate the importable Python across layouts
(flat, src, ``source/``-wrapped, monorepo, ``libs/``, nested integration
packages). ``find_project_root`` must resolve a wrapper to the code root, and
the structure world guard must abstain (NEI) where no code exists rather than
refuting against an empty inventory.
"""

from __future__ import annotations

from pathlib import Path

from docassay.core.pipeline import _is_excluded_doc, analyze_repository, find_project_root
from docassay.evidence.symbols import (
    build_symbol_inventory,
    find_import_roots,
    has_project_python,
)


def _english_readme(body: str) -> str:
    return "# Demo project\nThis is the demo project that many teams use every day.\n" + body


def _modules(root: Path) -> set[str]:
    return {e.object for e in build_symbol_inventory(root, kind="module")}


# --- find_import_roots ---------------------------------------------------------


def test_import_roots_flat_layout(tmp_path: Path) -> None:
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "__init__.py").write_text("")
    (tmp_path / "app.py").write_text("")
    roots = {r.name for r in find_import_roots(tmp_path)}
    assert tmp_path.name in roots
    assert {"pkg", "app"} <= _modules(tmp_path)


def test_import_roots_src_layout(tmp_path: Path) -> None:
    (tmp_path / "src" / "pkg").mkdir(parents=True)
    (tmp_path / "src" / "pkg" / "__init__.py").write_text("")
    assert "pkg" in _modules(tmp_path)


def test_import_roots_wrapped_checkout(tmp_path: Path) -> None:
    (tmp_path / "source" / "celery").mkdir(parents=True)
    (tmp_path / "source" / "celery" / "__init__.py").write_text("")
    (tmp_path / "source" / "celery" / "app.py").write_text("")
    assert {"celery", "celery.app"} <= _modules(tmp_path)


def test_import_roots_monorepo(tmp_path: Path) -> None:
    (tmp_path / "airflow-core" / "src" / "airflow").mkdir(parents=True)
    (tmp_path / "airflow-core" / "src" / "airflow" / "__init__.py").write_text("")
    (tmp_path / "airflow-ctl" / "src" / "airflow_ctl").mkdir(parents=True)
    (tmp_path / "airflow-ctl" / "src" / "airflow_ctl" / "__init__.py").write_text("")
    assert {"airflow", "airflow_ctl"} <= _modules(tmp_path)


def test_import_roots_libs_layout(tmp_path: Path) -> None:
    (tmp_path / "libs" / "core" / "langchain_core").mkdir(parents=True)
    (tmp_path / "libs" / "core" / "langchain_core" / "__init__.py").write_text("")
    assert "langchain_core" in _modules(tmp_path)


def test_import_roots_nested_integration(tmp_path: Path) -> None:
    (tmp_path / "src" / "integrations" / "prefect-dbt" / "prefect_dbt").mkdir(parents=True)
    (tmp_path / "src" / "integrations" / "prefect-dbt" / "prefect_dbt" / "__init__.py").write_text(
        ""
    )
    assert "prefect_dbt" in _modules(tmp_path)


def test_import_roots_docs_only_is_empty(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "index.md").write_text("# docs\n")
    assert _modules(tmp_path) == set()


def test_fixtures_subtree_is_not_import_roots(tmp_path: Path) -> None:
    # A `tests/fixtures/project/` tree must not make `project` a top-level
    # package: poetry's fixtures produced fake tops
    # `project`/`demo`/`example` that turned TOML keys into REFUTED symbols.
    (tmp_path / "tests" / "fixtures" / "project").mkdir(parents=True)
    (tmp_path / "tests" / "fixtures" / "project" / "__init__.py").write_text("")
    (tmp_path / "tests" / "fixtures" / "project" / "settings.py").write_text("x = 1\n")
    assert _modules(tmp_path) == set()


def test_non_code_ancestor_is_not_a_namespace_package(tmp_path: Path) -> None:
    # `examples/demo/foo.py` is not an importable namespace package: the
    # non-code check looks at ancestors, not just the directory's own name.
    (tmp_path / "examples" / "demo").mkdir(parents=True)
    (tmp_path / "examples" / "demo" / "foo.py").write_text("def f():\n    return 1\n")
    assert _modules(tmp_path) == set()


def test_src_child_namespace_is_the_top_package(tmp_path: Path) -> None:
    # A direct child of a top-level `src/` is the src-layout top package, not an
    # import root: `src/acme/core/engine.py` reads as `acme.core.engine` and a
    # git option `core.autocrlf` is NOT a project symbol.
    (tmp_path / "src" / "acme" / "core").mkdir(parents=True)
    (tmp_path / "src" / "acme" / "core" / "__init__.py").write_text("")
    (tmp_path / "src" / "acme" / "core" / "engine.py").write_text("def start():\n    pass\n")
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "acme-engine"\n')
    mods = _modules(tmp_path)
    assert "acme" in mods
    assert "acme.core" in mods
    assert "acme.core.engine" in mods
    assert "core" not in mods
    assert "core.engine" not in mods


def test_namespace_package_with_only_subpackages_is_importable(tmp_path: Path) -> None:
    # A namespace package that carries no direct `.py` (only subpackages) is
    # still importable — the tool's own `src/docassay/` and poetry's
    # `src/poetry/` are such trees.
    (tmp_path / "src" / "foo" / "bar").mkdir(parents=True)
    (tmp_path / "src" / "foo" / "bar" / "__init__.py").write_text("")
    (tmp_path / "src" / "foo" / "bar" / "baz.py").write_text("x = 1\n")
    mods = _modules(tmp_path)
    assert "foo" in mods
    assert "foo.bar" in mods
    assert "foo.bar.baz" in mods
    assert "bar" not in mods


def test_metadata_top_prevents_namespace_top_split(tmp_path: Path) -> None:
    # hatch `packages = ["src/pkg"]` declares `pkg` as the top-level package;
    # `src/pkg` (a namespace package without `__init__.py`) must NOT become an
    # import root whose subpackages are fake top levels (`core` instead of
    # `pkg.core`).
    (tmp_path / "src" / "pkg" / "core").mkdir(parents=True)
    (tmp_path / "src" / "pkg" / "core" / "__init__.py").write_text("")
    (tmp_path / "src" / "pkg" / "core" / "app.py").write_text("")
    (tmp_path / "src" / "pkg" / "_base.py").write_text("x = 1\n")
    (tmp_path / "pyproject.toml").write_text(
        '[tool.hatch.build.targets.wheel]\npackages = ["src/pkg"]\n'
    )
    mods = _modules(tmp_path)
    assert "pkg" in mods
    assert "pkg.core" in mods
    assert "core" not in mods
    assert "core.app" not in mods


def test_poetry_metadata_keeps_package_under_root(tmp_path: Path) -> None:
    # poetry `packages = [{include = "poetry", from = "src"}]` declares the top
    # package `poetry`; `src/poetry/console/application.py` must read as
    # `poetry.console.application`, not `console.application`.
    (tmp_path / "src" / "poetry" / "console").mkdir(parents=True)
    (tmp_path / "src" / "poetry" / "console" / "__init__.py").write_text("")
    (tmp_path / "src" / "poetry" / "console" / "application.py").write_text("x = 1\n")
    (tmp_path / "src" / "poetry" / "_version.py").write_text('__version__ = "1.0"\n')
    (tmp_path / "pyproject.toml").write_text(
        '[tool.poetry]\npackages = [{ include = "poetry", from = "src" }]\n'
    )
    mods = _modules(tmp_path)
    assert "poetry.console.application" in mods
    assert "console.application" not in mods


# --- has_project_python --------------------------------------------------------


def test_has_project_python_true_with_code(tmp_path: Path) -> None:
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "__init__.py").write_text("")
    assert has_project_python(tmp_path) is True


def test_has_project_python_false_docs_only(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("# docs\n")
    assert has_project_python(tmp_path) is False


# --- find_project_root ---------------------------------------------------------


def test_find_project_root_unchanged_for_real_root(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\n")
    assert find_project_root(tmp_path) == tmp_path


def test_find_project_root_descends_into_single_wrapper(tmp_path: Path) -> None:
    (tmp_path / "source" / "celery").mkdir(parents=True)
    (tmp_path / "source" / "celery" / "__init__.py").write_text("")
    (tmp_path / "source" / "pyproject.toml").write_text("[project]\n")
    assert find_project_root(tmp_path) == tmp_path / "source"


def test_find_project_root_ambiguous_stays(tmp_path: Path) -> None:
    for repo in ("repo_a", "repo_b"):
        (tmp_path / repo).mkdir()
        (tmp_path / repo / "pyproject.toml").write_text("[project]\n")
    assert find_project_root(tmp_path) == tmp_path


def test_find_project_root_docs_subdir_stays(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "index.md").write_text("# docs\n")
    assert find_project_root(tmp_path / "docs") == tmp_path / "docs"


def test_find_project_root_descends_through_pure_wrapper(tmp_path: Path) -> None:
    # Uploading a parent folder (Project/checkout/...) must still resolve to the
    # checkout, even when the wrapper itself has no repository markers.
    checkout = tmp_path / "DocAssay" / "docassay"
    (checkout / "src").mkdir(parents=True)
    (checkout / "pyproject.toml").write_text("[project]\n")
    assert find_project_root(tmp_path) == checkout


# --- structure world guard -----------------------------------------------------


def test_structure_world_guard_docs_only_root_nei(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text(
        _english_readme("The `pkg.mod` module defines `parse()` and the `run` method.\n")
    )
    result = analyze_repository(tmp_path)
    structure = {r.predicate_type for r in result.referents}
    assert "SYMBOL_EXISTS" in structure
    for ref in result.referents:
        if ref.predicate_type == "SYMBOL_EXISTS":
            assert ref.assertions[0].code_verdict == "NEI", ref.object


def test_structure_world_guard_code_root_refutes(tmp_path: Path) -> None:
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "__init__.py").write_text("")
    (tmp_path / "pkg" / "core.py").write_text("def real():\n    return 1\n")
    (tmp_path / "README.md").write_text(
        _english_readme("The `pkg.core` module exposes the `pkg.ghost` function.\n")
    )
    result = analyze_repository(tmp_path)
    refs = {r.object: r for r in result.referents if r.predicate_type == "SYMBOL_EXISTS"}
    assert "pkg.ghost" in refs
    assert refs["pkg.ghost"].assertions[0].code_verdict == "REFUTED"


# --- non-claim document classes -------------------------------------------------


def test_is_excluded_doc() -> None:
    assert _is_excluded_doc("docs/upgrading_to_v3.rst")
    assert _is_excluded_doc("docs/migrating.md")
    assert _is_excluded_doc("docs/older_versions.md")
    assert _is_excluded_doc("java-sdk/README.md")
    assert _is_excluded_doc("go-sdk/README.md")
    assert _is_excluded_doc("docs/adr/0001-migration.md")
    assert not _is_excluded_doc("docs/howto/using-the-api.rst")


def test_release_notes_paths_are_excluded() -> None:
    assert _is_excluded_doc("doc/source/release/0.19.0-notes.rst")
    assert _is_excluded_doc("doc/source/release/1.2.0.rst")
    assert _is_excluded_doc("docs/releases/index.rst")
    assert _is_excluded_doc("docs/whatsnew/3.4.rst")
    assert _is_excluded_doc("NEWS.md")
    assert _is_excluded_doc("docs/changelog.rst")
    assert _is_excluded_doc("docs/v2-3-release-notes.md")
    assert not _is_excluded_doc("docs/howto/release-process.rst")


def test_release_notes_heading_excludes_content() -> None:
    from docassay.core.pipeline import _is_release_notes_document

    assert _is_release_notes_document(
        "===========\n"
        "SciPy 0.19.0 Release Notes\n"
        "===========\n\n"
        "This release requires Python 2.7.\n"
    )
    assert _is_release_notes_document("# What's New in 1.2\n\nNew features.\n")
    assert _is_release_notes_document("# Changelog\n\n- fixed a bug\n")
    assert not _is_release_notes_document(
        "# User Guide\nSee the release notes for details about the previous version.\n"
    )
    assert not _is_release_notes_document("# Getting Started\n\nImport the library today.\n")


def test_release_notes_requires_top_level_heading() -> None:
    # (G2): a section-level "## News"/"## What's New" does NOT
    # make a README a release-notes document — FastChat's README must be scanned.
    from docassay.core.pipeline import _is_release_notes_document

    assert not _is_release_notes_document(
        "# FastChat\n\n## News\n- We released v1.0 this week.\n\n## Install\n"
    )
    assert not _is_release_notes_document("# Docs\n\n### What's New\n- feature\n")
    assert _is_release_notes_document("# Release Notes\n\n- 0.1.0\n")


def test_release_notes_doc_is_not_scanned(tmp_path: Path) -> None:
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "__init__.py").write_text("")
    (tmp_path / "README.md").write_text(_english_readme("The `pkg.mod` module defines the API.\n"))
    (tmp_path / "doc" / "source" / "release").mkdir(parents=True)
    (tmp_path / "doc" / "source" / "release" / "0.19.0-notes.rst").write_text(
        "================\nSciPy 0.19.0 Release Notes\n================\n"
        "This release requires Python 2.7 and the old `pkg.removed` module.\n"
    )
    result = analyze_repository(tmp_path)
    assert "0.19.0-notes.rst" not in {c.source for c in result.claims}
    refs = {r.object for r in result.referents if r.predicate_type == "SYMBOL_EXISTS"}
    assert refs == {"pkg.mod"}


def test_upgrading_doc_is_not_scanned(tmp_path: Path) -> None:
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "__init__.py").write_text("")
    (tmp_path / "README.md").write_text(_english_readme("The `pkg.mod` module defines the API.\n"))
    (tmp_path / "upgrading_to_v2.rst").write_text(
        "Old `pkg.removed` module and `airflow.hooks.base.BaseHook` are gone.\n"
    )
    result = analyze_repository(tmp_path)
    assert "upgrading_to_v2.rst" not in {c.source for c in result.claims}
    refs = {r.object for r in result.referents if r.predicate_type == "SYMBOL_EXISTS"}
    assert refs == {"pkg.mod"}


# --- pipeline at a wrapper parent -----------------------------------------------


def test_analyze_repository_resolves_wrapper(tmp_path: Path) -> None:
    (tmp_path / "source" / "src" / "pylib").mkdir(parents=True)
    (tmp_path / "source" / "src" / "pylib" / "__init__.py").write_text("")
    (tmp_path / "source" / "src" / "pylib" / "core.py").write_text("def render(t):\n    return t\n")
    (tmp_path / "source" / "README.md").write_text(
        _english_readme("The `pylib.core` module defines `render()`.\n")
    )
    result = analyze_repository(tmp_path)
    by_object = {r.object: r for r in result.referents if r.predicate_type == "SYMBOL_EXISTS"}
    assert result.project_root.endswith("source")
    assert by_object["pylib.core"].assertions[0].code_verdict == "SUPPORTED"
    assert by_object["render"].assertions[0].code_verdict == "SUPPORTED"
