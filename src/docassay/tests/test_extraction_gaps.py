"""Task E extraction gaps: claims the engine currently misses.

These tests are the **measured extraction gaps** found by the document-sampled
gold (Task E). In that run two annotators enumerated checkable claims
in fixed 20-line windows over four single-project repositories and matched them
against the engine's extraction within the same window. A whole class of
human claims was systematically absent from the engine's output, concentrated in
``SYMBOL_EXISTS`` (Sphinx roles, directives, ``from`` imports, reference lists)
and ``PATH_EXISTS`` (tree-listings, checksum tables), plus ``HAS_CI_WORKFLOW``
prose mentions. (The Markdown-link gap, GAP 4, is now fixed — see below.)

Each test below states the **desired** extraction for a real missed case. The
engine is intentionally unchanged in this session, so every gap test is marked
``xfail(strict=True)``: it documents the gap and turns into a hard failure the
moment the behaviour is implemented, forcing the test to be un-marked and kept
as a regression guard.

Sources (real windows from the Task E run):
- fastapi: ``docs/en/docs/reference/responses.md`` (``::: fastapi.responses.Response``),
  ``docs/en/docs/reference/fastapi.md`` (bare ``- get`` list),
  ``docs/en/docs/tutorial/request-forms.md`` (``Form`` in prose),
  ``docs/en/docs/how-to/extending-openapi.md`` (``{* ... tutorial ... *}``),
  ``docs/en/docs/advanced/stream-data.md`` (Markdown link).
- scikit-learn: ``doc/modules/cross_validation.rst`` (``:class:`StratifiedKFold``),
  ``doc/developers/callback_support.rst`` (``:func:``/``.. currentmodule::``),
  ``doc/modules/array_api.rst`` (``:func:`` role),
  ``doc/developers/contributing.rst`` (GitHub Actions / CircleCI prose).
- pandas: ``doc/source/user_guide/indexing.rst`` (``at``/``iat``/``loc``/``iloc``),
  ``doc/cheatsheet/README.md`` (``Pandas_Cheat_Sheet.pdf`` paths),
  ``doc/source/reference/arrays.rst`` (``ArrowDtype`` in a table).
- dbt-core: ``crates/dbt-csv/README.md`` (tree-listing ``├── lib.rs``),
  ``crates/dbt-docs-server/API-CONTRACTS.md`` (referenced ``ModelDetail`` etc.).
"""

from __future__ import annotations

import pytest

from docassay.predicates.infra import ci_workflow_scan
from docassay.predicates.listing import path_exists_scan
from docassay.predicates.structure import symbol_exists_scan


def _symbols(text: str, source: str = "doc.rst") -> set[str]:
    return {c.object for c in symbol_exists_scan(text, source)}


def _paths(text: str, source: str = "README.md") -> set[str]:
    return {c.object for c in path_exists_scan(text, source)}


def _ci(text: str, source: str = "README.md") -> set[str]:
    return {c.object for c in ci_workflow_scan(text, source)}


# --- GAP 1: Sphinx roles (:class:, :func:, :meth:, :attr:, :mod:) ---------------
#
# The engine excludes *every* Sphinx role as a cross-reference
# (``is_sphinx_role_anchor``), so a documented project symbol given through a
# role is never extracted. In Task E that is the single largest ``SYMBOL_EXISTS``
# miss (e.g. ``:class:`StratifiedKFold```, ``:func:`~with_callbacks```
# ``:func:`sklearn.metrics.pairwise.paired_cosine_distances```).
# Note: this deliberately contradicts ``test_sphinx_role_is_not_anchor`` for the
# API roles; that test covers ``:mod:``/``:pypi:`` and will need to be revisited
# when the engine learns to separate project-API roles from external ones.


@pytest.mark.xfail(strict=True, reason="GAP-1: Sphinx :class: role not anchored as SYMBOL_EXISTS")
def test_sphinx_class_role_extracts_symbol() -> None:
    assert _symbols(
        "Cross-validation.\n:class:`StratifiedKFold` is a variation of K-fold.\n",
        "doc/modules/cross_validation.rst",
    ) == {"stratifiedkfold"}


@pytest.mark.xfail(strict=True, reason="GAP-1: Sphinx :func: role not anchored as SYMBOL_EXISTS")
def test_sphinx_func_role_extracts_symbol() -> None:
    # The rst ``~`` prefix marks a short reference form; the fix should still
    # yield the ``with_callbacks`` symbol (bare or qualified).
    symbols = _symbols(
        "See :func:`~with_callbacks` for details.\n",
        "doc/developers/callback_support.rst",
    )
    assert any(s.endswith("with_callbacks") for s in symbols)


@pytest.mark.xfail(strict=True, reason="GAP-1: dotted Sphinx :func: role not anchored")
def test_sphinx_func_role_dotted_extracts_symbol() -> None:
    assert _symbols(
        "- :func:`sklearn.metrics.pairwise.paired_cosine_distances`\n",
        "doc/modules/array_api.rst",
    ) == {"sklearn.metrics.pairwise.paired_cosine_distances"}


@pytest.mark.xfail(strict=True, reason="GAP-1: Sphinx :meth:/:attr: roles not anchored")
def test_sphinx_meth_and_attr_roles_extract_symbols() -> None:
    symbols = _symbols(
        "Call :meth:`Estimator.fit` and read :attr:`Estimator.coef_`.\n",
        "doc/modules/linear_model.rst",
    )
    assert {"estimator.fit", "estimator.coef_"} <= symbols


# --- GAP 2: Sphinx directives (:::, .. currentmodule::) -------------------------
#
# mkdocs ``::: module.Symbol`` blocks (fastapi reference pages) and the rst
# ``.. currentmodule::`` directive name project symbols but produce no anchor.


@pytest.mark.xfail(strict=True, reason="GAP-2: mkdocs '::: module.Symbol' directive not anchored")
def test_mkdocs_directive_extracts_symbol() -> None:
    text = (
        "# Responses\n\n::: fastapi.responses.Response\n"
        "    options:\n        show_root_heading: true\n"
    )
    assert _symbols(text, "docs/en/docs/reference/responses.md") == {"fastapi.responses.response"}


@pytest.mark.xfail(strict=True, reason="GAP-2: '.. currentmodule::' directive not anchored")
def test_currentmodule_directive_extracts_symbol() -> None:
    assert _symbols(
        ".. currentmodule:: sklearn.callback\n",
        "doc/developers/callback_support.rst",
    ) == {"sklearn.callback"}


# --- GAP 3: import lines and attribute-set prose -------------------------------


@pytest.mark.xfail(strict=True, reason="GAP-3: 'from X import Y' line not anchored")
def test_from_import_line_extracts_symbol() -> None:
    # The documented import must yield the module and/or the imported name.
    symbols = _symbols(
        "from fastapi.staticfiles import StaticFiles\n",
        "docs/en/docs/reference/staticfiles.md",
    )
    assert any(s.endswith("staticfiles") for s in symbols)


@pytest.mark.xfail(strict=True, reason="GAP-3: attribute assignment in prose not anchored")
def test_attribute_assignment_prose_extracts_symbol() -> None:
    assert "openapi_url" in _symbols(
        "you can set `openapi_url=None` in the app.\n",
        "docs/en/docs/tutorial/metadata.md",
    )


# --- GAP 4: Markdown links (fixed) ---------------------------------------------
#
# ``[label](relative/path.md)`` is a project path reference; the extractor now
# anchors Markdown link/image targets and resolves them against the referencing
# document's directory. This test is a regression guard.


def test_markdown_link_extracts_path() -> None:
    assert _paths(
        "See [Stream JSON Lines](../tutorial/stream-json-lines.md) for details.\n",
        "docs/en/docs/advanced/stream-data.md",
    ) == {"docs/en/docs/tutorial/stream-json-lines.md"}


# --- GAP 5: tree-listings and checksum tables ----------------------------------


@pytest.mark.xfail(strict=True, reason="GAP-5: tree-listing entry not anchored as PATH_EXISTS")
def test_tree_listing_extracts_path() -> None:
    assert _paths(
        "src/\n├── lib.rs              # Public API exports\n└── reader.rs\n",
        "crates/dbt-csv/README.md",
    ) >= {"src/lib.rs", "src/reader.rs"}


@pytest.mark.xfail(strict=True, reason="GAP-5: checksum-table path not anchored")
def test_checksum_table_extracts_path() -> None:
    assert "doc/cheatsheet/pandas_cheat_sheet.pdf" in _paths(
        "| doc/cheatsheet/Pandas_Cheat_Sheet.pdf | 1.2M |\n",
        "doc/cheatsheet/README.md",
    )


# --- GAP 6: bare API-reference list entries ------------------------------------
#
# fastapi reference pages list member names as bare ``- name`` bullets; these
# are project symbols but produce no anchor.


@pytest.mark.xfail(strict=True, reason="GAP-6: bare reference-list member not anchored")
def test_reference_list_member_extracts_symbol() -> None:
    assert {"get", "put", "post"} <= _symbols(
        "- get\n- put\n- post\n- delete\n",
        "docs/en/docs/reference/fastapi.md",
    )


# --- NOT-A-GAP (finding): HAS_CI_WORKFLOW referent shape -----------------------
#
# The Task E matcher counted four human HAS_CI_WORKFLOW claims as "missed"
# (sklearn ``doc/developers/contributing.rst``: GitHub Actions / CircleCI). The
# engine *does* extract them, but with a constant object ``ci_workflow`` while
# annotators name the specific product (``github-actions`` / ``circleci``), so
# ``(predicate, object)`` matching fails. This is a referent-shape mismatch, not
# an extraction gap — recorded here as a characterization guard so the real
# behaviour is visible and does not silently change.


def test_ci_prose_mention_extracts_constant_object() -> None:
    assert _ci(
        "Github Actions are used for various tasks.\n",
        "doc/developers/contributing.rst",
    ) == {"ci_workflow"}


def test_circleci_prose_mention_extracts_constant_object() -> None:
    assert _ci(
        "CircleCI is used to build the docs for viewing.\n",
        "doc/developers/contributing.rst",
    ) == {"ci_workflow"}


# --- Characterization guards (current behaviour, must stay true) ---------------
#
# These pin the *precision* side: fixing the recalls above must not turn common
# prose words into claims. They are ordinary (passing) tests.


def test_prose_word_events_is_not_a_symbol() -> None:
    assert _symbols("Host name to associate with the sent events.\n") == set()


def test_prose_word_future_is_not_a_symbol() -> None:
    assert _symbols("It might change in the future to slack_default.\n") == set()


def test_prose_word_coverage_is_not_a_symbol() -> None:
    assert _symbols("Run nightly for coverage reporting.\n") == set()


def test_placeholder_path_is_not_anchored() -> None:
    # "path/to/file-to-be-added-or-changed.py" is a how-to placeholder.
    assert _paths("path/to/file-to-be-added-or-changed.py\n") == set()


def test_sphinx_external_pypi_role_still_not_anchor() -> None:
    # :pypi: points at PyPI, not the project tree — must remain excluded.
    assert _symbols("The backend requires the :pypi:`boto3` library.\n") == set()
