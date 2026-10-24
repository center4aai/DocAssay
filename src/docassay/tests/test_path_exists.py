"""Tests for the PATH_EXISTS predicate (structure group).

A single predicate over the unified file+directory listing: file anchors
(backtick path-shaped tokens, **Markdown link/image targets**) and directory
anchors (trailing-slash tokens, "the `X` directory" noun phrases) produce one
claim keyed by the normalized path; directory keys keep a trailing slash so they
never collide with files.
"""

from __future__ import annotations

from pathlib import Path

from docassay.core.models import Context, PredicateClaim
from docassay.core.pipeline import analyze_repository, collect_documents
from docassay.evidence.listing import PathEvidence, build_structure_inventory
from docassay.predicates.listing import (
    PATH_EXISTS_WORLD,
    path_exists_flags,
    path_exists_match,
    path_exists_scan,
)
from docassay.vocabularies.structure import normalize_path


def _scan(text: str) -> list[PredicateClaim]:
    return path_exists_scan(text, "README.md")


def _objects(text: str) -> set[str]:
    return {c.object for c in _scan(text)}


def _english_readme(body: str) -> str:
    return "# Demo project\nThis is the demo project that many teams use every day.\n" + body


# --- extraction -------------------------------------------------------------


def test_backtick_file_path_is_anchor() -> None:
    assert _objects("See `src/pkg/mod.py` for details.\n") == {"src/pkg/mod.py"}


def test_backtick_bare_extension_file_is_anchor() -> None:
    assert _objects("The `setup.py` configures the build.\n") == {"setup.py"}


def test_backtick_bare_name_is_anchor() -> None:
    assert _objects("Released under the terms of `LICENSE`.\n") == {"license"}


def test_inline_code_with_spaces_is_not_anchor() -> None:
    assert _objects("Run `pip install django` to get started.\n") == set()


def test_inline_import_is_not_anchor() -> None:
    assert _objects("Try `from x import y` in a notebook.\n") == set()


def test_version_pin_is_not_anchor() -> None:
    assert _objects("Install `django>=5.0` from PyPI.\n") == set()


def test_plain_backtick_word_is_not_anchor() -> None:
    assert _objects("The `model` class is exported.\n") == set()


def test_bare_extension_mention_is_not_anchor() -> None:
    assert _objects("SQL is stored as `*.sql` files; use `.sql` or `.rst`.\n") == set()


def test_sphinx_ref_role_is_not_anchor() -> None:
    assert _objects("See :ref:`contributing` for details.\n") == set()


def test_sphinx_doc_role_is_not_anchor() -> None:
    assert _objects("As covered in :doc:`configuration/index`.\n") == set()


def test_absolute_path_is_not_anchor() -> None:
    assert _objects("Published at `/en/latest/`.\n") == set()


def test_home_path_is_not_anchor() -> None:
    assert _objects("Profiles live in `~/.dbt/`.\n") == set()


def test_relative_navigation_is_not_anchor() -> None:
    assert _objects("Use `../` to reach the parent directory.\n") == set()
    assert _objects("Files live in `../../src/`.\n") == set()
    assert _objects("Start paths with `./`.\n") == set()


def test_build_artifact_is_not_anchor() -> None:
    assert _objects("Output goes to `docs/build/html`.\n") == set()
    assert _objects("Redirects live in `_redirects`.\n") == set()
    assert _objects("The manifest is `versions.json`.\n") == set()


def test_build_script_filename_is_anchor() -> None:
    # ``build.rs`` is a real Rust build-script file — the `build` dir filter
    # must not reject filenames that merely contain the word.
    assert _objects("The crate uses `build.rs` at build time.\n") == {"build.rs"}


def test_math_fraction_is_not_anchor() -> None:
    assert _objects("Where `1/x` is the inverse rate.\n") == set()
    assert _objects("The window is `nperseg/2` samples.\n") == set()
    assert _objects("Filter at `f_s/2` Nyquist.\n") == set()


def test_integer_division_is_not_anchor() -> None:
    assert _objects("It is `M//2`, i.e. floor division.\n") == set()
    assert _objects("Centered at `nperseg//2`.\n") == set()


def test_doi_citation_is_not_anchor() -> None:
    assert _objects("See `10.1001/jama.295.3.306` for the study.\n") == set()


def test_numeric_leading_non_file_is_not_anchor() -> None:
    assert _objects("Rates like `1/b.` are dimensionless.\n") == set()
    assert _objects("Counts at `2023/` are unsupported.\n") == set()


def test_git_ref_is_not_anchor() -> None:
    assert _objects("Merge from `origin/main`.\n") == set()
    assert _objects("Checkout `refs/tags/v1.0`.\n") == set()
    assert _objects("Sync `upstream/stable`.\n") == set()
    assert _objects("The `actions/cache` step caches deps.\n") == set()


def test_deploy_artifact_is_not_anchor() -> None:
    assert _objects("Open `index.html` in the build dir.\n") == set()


def test_build_output_dirs_are_not_anchor() -> None:
    assert _objects("Files land in `build-install/lib/`.\n") == set()
    assert _objects("Snapshots go to `results/benchmark.json`.\n") == set()


def test_real_path_mentions_stay_anchors() -> None:
    assert _objects("See `docs/index.md` for the guide.\n") == {"docs/index.md"}
    assert _objects("Source is `src/pkg/core.py`.\n") == {"src/pkg/core.py"}


def test_url_is_not_anchor() -> None:
    assert _objects("See https://example.com for the docs.\n") == set()


def test_external_host_is_not_anchor() -> None:
    assert _objects("See `jakewheat.github.io/sql-overview` for details.\n") == set()
    assert _objects("A copy of `web.cecs.pdx.edu/~len/sql1999.pdf`.\n") == set()


# --- markdown link / image targets -----------------------------------------


def test_markdown_link_path_is_anchor() -> None:
    assert _objects("See [guide](docs/guide.md).\n") == {"docs/guide.md"}


def test_markdown_image_path_is_anchor() -> None:
    assert _objects("![arch](docs/img/arch.png)\n") == {"docs/img/arch.png"}


def test_markdown_link_bare_name_is_anchor() -> None:
    assert _objects("See [notes](notes.md).\n") == {"notes.md"}


def test_markdown_link_fragment_is_stripped() -> None:
    assert _objects("See [x](docs/guide.md#install).\n") == {"docs/guide.md"}


def test_markdown_link_url_is_not_anchor() -> None:
    assert _objects("See [site](https://example.com/a.md).\n") == set()


def test_markdown_link_anchor_only_is_not_anchor() -> None:
    assert _objects("See [top](#section).\n") == set()


def test_markdown_link_parent_is_not_anchor() -> None:
    assert _objects("See [x](../other/page.md).\n") == set()


def test_markdown_link_drive_is_not_anchor() -> None:
    assert _objects("See [x](C:/Users/app.py).\n") == set()


def test_trailing_slash_is_anchor() -> None:
    assert _objects("The docs live in `docs/`.\n") == {"docs/"}


def test_directory_noun_phrase_is_anchor() -> None:
    assert _objects("See the `tests` directory for examples.\n") == {"tests/"}
    assert _objects("Source code is in the `src` folder.\n") == {"src/"}


def test_nested_directory_phrase_is_anchor() -> None:
    assert _objects("Guides are under the `docs/guides` subdirectory.\n") == {"docs/guides/"}


def test_absolute_directory_is_not_anchor() -> None:
    assert _objects("Published at `/en/stable/`.\n") == set()


def test_build_output_directory_is_not_anchor() -> None:
    assert _objects("HTML goes to `docs/build/`.\n") == set()


def test_objects_are_normalized() -> None:
    assert _objects("Load `SRC/MOD.PY` first.\n") == {"src/mod.py"}
    assert _objects("The entry point is `./app/main.py`.\n") == {"app/main.py"}
    assert _objects("Load files from `SRC/` first.\n") == {"src/"}


def test_polarity_attaches_to_backtick_anchor() -> None:
    claims = _scan("`src/a.py` is not present in the tree.\n")
    a_py = next(c for c in claims if c.object == "src/a.py")
    assert a_py.is_negative is True
    claims = _scan("The `docs/` directory is not present in the tree.\n")
    docs = next(c for c in claims if c.object == "docs/")
    assert docs.is_negative is True


def test_does_not_exist_negates_anchor() -> None:
    claims = _scan("The `src/a.py` file does not exist anymore.\n")
    a_py = next(c for c in claims if c.object == "src/a.py")
    assert a_py.is_negative is True


def test_removed_is_historical() -> None:
    claims = _scan("The old `legacy.py` was removed in 2.0.\n")
    legacy = next(c for c in claims if c.object == "legacy.py")
    assert path_exists_flags(legacy)["historical"] is True
    claims = _scan("The old `legacy/` directory was removed in 2.0.\n")
    legacy = next(c for c in claims if c.object == "legacy/")
    assert path_exists_flags(legacy)["historical"] is True


def test_current_mention_is_not_historical() -> None:
    claims = _scan("The `main.py` is currently the entry point.\n")
    main = next(c for c in claims if c.object == "main.py")
    assert path_exists_flags(main)["historical"] is False


def test_world_is_closed_over_listing() -> None:
    assert PATH_EXISTS_WORLD == "closed-over-listing"


def test_trailing_slash_token_is_single_directory_claim() -> None:
    # A trailing-slash token yields exactly one claim, keyed as a directory —
    # never an extra (spurious) file-shaped claim for the same token.
    claims = _scan("Start with `docs/index.md` inside `docs/`.\n")
    objects = [c.object for c in claims]
    assert sorted(objects) == ["docs/", "docs/index.md"]
    assert all(c.predicate_type == "PATH_EXISTS" for c in claims)


def test_no_spurious_file_claim_for_trailing_slash() -> None:
    assert _objects("The docs live in `docs/`.\n") == {"docs/"}


# --- normalization -----------------------------------------------------------


def test_normalize_path() -> None:
    assert normalize_path("./src/a.py") == "src/a.py"
    assert normalize_path("SRC/A.PY") == "src/a.py"
    assert normalize_path("src//a.py") == "src/a.py"
    assert normalize_path("docs/") == "docs/"


# --- inventory --------------------------------------------------------------


def test_file_inventory(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").write_text("x = 1\n")
    (tmp_path / "setup.py").write_text("")
    (tmp_path / ".github").mkdir()
    (tmp_path / ".github" / "workflows").mkdir()
    (tmp_path / ".github" / "workflows" / "ci.yml").write_text("")
    (tmp_path / ".gitignore").write_text("")
    inventory = build_structure_inventory(tmp_path, kind="file")
    objects = {e.object for e in inventory}
    assert "src/a.py" in objects
    assert "setup.py" in objects
    assert ".github/workflows/ci.yml" in objects
    assert ".gitignore" in objects


def test_directory_inventory(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "pkg").mkdir()
    (tmp_path / "src" / "a.py").write_text("x = 1\n")
    (tmp_path / "docs").mkdir()
    (tmp_path / ".github").mkdir()
    inventory = build_structure_inventory(tmp_path, kind="dir")
    objects = {e.object for e in inventory}
    assert "src/" in objects
    assert "src/pkg/" in objects
    assert "docs/" in objects
    assert ".github/" in objects
    assert "src/a.py" not in objects


def test_unified_inventory(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "index.md").write_text("# Docs\n")
    (tmp_path / "setup.py").write_text("")
    inventory = build_structure_inventory(tmp_path, kind="both")
    objects = {e.object for e in inventory}
    assert "docs/" in objects
    assert "docs/index.md" in objects
    assert "setup.py" in objects


# --- matching ---------------------------------------------------------------


def _evidence(paths: list[str]) -> dict[str, list[PathEvidence]]:
    by_name: dict[str, list[PathEvidence]] = {}
    for path in paths:
        kind = "dir" if path.endswith("/") else "file"
        key = normalize_path(path)
        by_name.setdefault(key, []).append(
            PathEvidence(
                evidence_id=f"{kind}:{key}",
                path=key,
                raw_path=path,
                kind=kind,
            )
        )
    return by_name


def _match(path: str, polarity: frozenset[str] | None, evidence: dict, **flags) -> tuple[str, ...]:
    context = Context(polarity=frozenset(polarity or ()))
    verdict, support, refute, *_ = path_exists_match(path, context, evidence, **flags)
    return (verdict, *support, *refute)


def test_match_file_present_supported() -> None:
    assert _match("src/a.py", None, _evidence(["src/a.py"]))[0] == "SUPPORTED"


def test_match_file_absent_refuted_closed_world() -> None:
    # A missing file under a *present* top-level directory is a CLOSED finding.
    assert _match("src/a.py", None, _evidence(["src/"]))[0] == "REFUTED"


def test_match_file_absent_nested_directory_is_anchored() -> None:
    # A doc-relative claim (``proj/celeryx.py``) whose head ``proj`` is not a
    # top-level segment but *is* a nested directory (``examples/django/proj/``)
    # is still anchored — a stale reference, not a reader-space mention.
    ev = _evidence(["examples/django/proj/celery.py", "examples/django/proj/"])
    assert _match("proj/celeryx.py", None, ev)[0] == "REFUTED"


def test_match_file_absent_unanchored_is_nei() -> None:
    # A missing path whose first segment is absent from the listing is not a
    # stale reference into the tree.
    assert _match("src/a.py", None, {})[0] == "NEI"
    assert _match("z/ghost.py", None, _evidence(["docs/"]))[0] == "NEI"
    assert _match("z/ghost.py", None, {})[0] == "NEI"


def test_match_dir_present_supported() -> None:
    assert _match("docs/", None, _evidence(["docs/"]))[0] == "SUPPORTED"


def test_match_dir_absent_refuted_closed_world() -> None:
    # A missing *nested* directory under a present top-level is a finding.
    assert _match("docs/ghost/", None, _evidence(["docs/"]))[0] == "REFUTED"


def test_match_dir_absent_unanchored_is_nei() -> None:
    assert _match("docs/", None, {})[0] == "NEI"


def test_match_negation_with_evidence_refuted() -> None:
    assert _match("src/a.py", frozenset({"not"}), _evidence(["src/a.py"]))[0] == "REFUTED"
    assert _match("docs/", frozenset({"not"}), _evidence(["docs/"]))[0] == "REFUTED"


def test_match_negation_without_evidence_nei() -> None:
    assert _match("src/a.py", frozenset({"not"}), {})[0] == "NEI"
    assert _match("docs/", frozenset({"not"}), {})[0] == "NEI"


def test_usage_negation_is_not_existence_negation() -> None:
    # "blackd will not use `pyproject.toml`" is a usage statement, not an
    # existence claim — no "not" polarity on the path claim.
    claims = _scan("Please note `blackd` will not use `pyproject.toml` configuration.\n")
    c = next(x for x in claims if x.object == "pyproject.toml")
    assert "not" not in c.context.polarity


def test_hypothetical_negation_is_not_existence_negation() -> None:
    # "If there is no `poetry.lock` file" and "Installing without
    # `poetry.lock`" are hypothetical/instructional, not existence claims.
    claims = _scan("If there is no `poetry.lock` file, Poetry will create one.\n")
    c = next(x for x in claims if x.object == "poetry.lock")
    assert "not" not in c.context.polarity
    claims = _scan("### Installing without `poetry.lock`\n")
    c = next(x for x in claims if x.object == "poetry.lock")
    assert "not" not in c.context.polarity


def test_match_historical_absent_nei() -> None:
    assert _match("src/a.py", None, {}, historical=True)[0] == "NEI"
    assert _match("docs/", None, {}, historical=True)[0] == "NEI"


def test_match_historical_present_supported() -> None:
    assert _match("src/a.py", None, _evidence(["src/a.py"]), historical=True)[0] == "SUPPORTED"


def test_match_instructional_absent_nei() -> None:
    assert _match("x.py", None, {}, instructional=True)[0] == "NEI"
    assert _match("docs/", None, {}, instructional=True)[0] == "NEI"


def test_match_exemplary_absent_nei() -> None:
    assert _match("x.py", None, {}, exemplary=True)[0] == "NEI"


# --- path resolution (repo-root / doc-relative / basename-unique) ------------


def test_match_doc_relative_resolution() -> None:
    # `conftest.py` from test/AGENTS.md resolves to test/conftest.py.
    ev = _evidence(["test/conftest.py"])
    verdict, support, *_ = path_exists_match("conftest.py", Context(), ev, source="test/AGENTS.md")
    assert verdict == "SUPPORTED"
    assert support == ("file:test/conftest.py",)


def test_match_dir_doc_relative_resolution() -> None:
    # `assets/` from docs/guide.md resolves to docs/assets/.
    ev = _evidence(["docs/assets/"])
    verdict, support, _, *_ = path_exists_match("assets/", Context(), ev, source="docs/guide.md")
    assert verdict == "SUPPORTED"
    assert support == ("dir:docs/assets/",)


def test_match_bare_name_doc_relative_beats_root() -> None:
    ev = _evidence(["conftest.py", "test/conftest.py"])
    verdict, support, *_ = path_exists_match("conftest.py", Context(), ev, source="test/AGENTS.md")
    assert verdict == "SUPPORTED"
    assert support == ("file:test/conftest.py",)


def test_match_path_root_beats_doc_relative() -> None:
    ev = _evidence(["src/a.py", "docs/src/a.py"])
    verdict, support, _, *_ = path_exists_match("src/a.py", Context(), ev, source="docs/index.md")
    assert verdict == "SUPPORTED"
    assert support == ("file:src/a.py",)


def test_match_slash_path_suffix_resolution() -> None:
    # `flaskr/db.py` from a tutorial references examples/tutorial/flaskr/db.py:
    # a slash path resolves when it is a segment-aligned suffix of a key.
    ev = _evidence(["examples/tutorial/flaskr/db.py"])
    verdict, support, _, *_ = path_exists_match(
        "flaskr/db.py", Context(), ev, source="docs/tutorial.rst"
    )
    assert verdict == "SUPPORTED"
    assert support == ("file:examples/tutorial/flaskr/db.py",)


def test_match_slash_path_same_basename_other_dir_refuted() -> None:
    # `src/old/utils.py` with only `src/new/utils.py` in the tree: the old
    # unique-basename fallback confirmed it — a suffix match must not.
    ev = _evidence(["src/new/utils.py"])
    assert _match("src/old/utils.py", None, ev, source="README.md")[0] == "REFUTED"


def test_match_slash_path_moved_into_subdir_refuted() -> None:
    # A file that moved from `a/legacy/name.py` to `a/name.py` is a stale
    # reference: the claimed path is not a suffix of any key (mutation recall).
    ev = _evidence(["a/name.py"])
    assert _match("a/legacy/name.py", None, ev, source="README.md")[0] == "REFUTED"


def test_match_slash_path_suffix_ambiguous_picks_first() -> None:
    # Two keys ending in the same suffix: deterministic pick of the first
    # sorted match, never a unique-basename collision.
    ev = _evidence(["a/x/y.py", "b/x/y.py"])
    assert _match("x/y.py", None, ev, source="README.md")[0] == "SUPPORTED"


# --- case-only spelling differences are not findings --------------------------


def _match_case(
    raw_object: str, evidence: dict, *, flags: dict | None = None, source: str = "README.md"
) -> tuple[str, ...]:
    kwargs = dict(flags or {})
    kwargs.setdefault("source", source)
    kwargs.setdefault("raw_object", raw_object)
    context = Context()
    verdict, support, refute, *_ = path_exists_match(
        normalize_path(raw_object), context, evidence, **kwargs
    )
    return (verdict, *support, *refute)


def test_match_case_only_difference_is_supported() -> None:
    # `docs/guide.md` against a tree with `docs/Guide.md` is the same path:
    # documentation routinely folds the case of file names, so a case-only
    # difference resolves as SUPPORTED, never as a refuted finding.
    ev = _evidence(["docs/Guide.md"])
    result = _match_case("docs/guide.md", ev)
    assert result[0] == "SUPPORTED"
    assert result[1:] == ("file:docs/guide.md",)


def test_match_case_exact_supported() -> None:
    ev = _evidence(["docs/Guide.md"])
    assert _match_case("docs/Guide.md", ev)[0] == "SUPPORTED"


def test_match_case_dot_slash_prefix_is_supported() -> None:
    ev = _evidence(["docs/index.md"])
    assert _match_case("./docs/index.md", ev)[0] == "SUPPORTED"


def test_match_case_doc_relative_path_is_supported() -> None:
    ev = _evidence(["test/conftest.py"])
    assert _match_case("conftest.py", ev, source="test/AGENTS.md")[0] == "SUPPORTED"


def test_match_basename_unique_resolution() -> None:
    # `parser.rs` from sqlfluffrs/ENGINE.md → the unique frame.rs anywhere.
    ev = _evidence(["sqlfluffrs/sqlfluffrs_parser/src/parser/frame.rs"])
    verdict, support, _, *_ = path_exists_match(
        "parser/frame.rs", Context(), ev, source="sqlfluffrs/ENGINE.md"
    )
    assert verdict == "SUPPORTED"
    assert support == ("file:sqlfluffrs/sqlfluffrs_parser/src/parser/frame.rs",)


def test_match_basename_ambiguous_exists_is_supported() -> None:
    # A bare name that exists in several places is a true existence claim.
    ev = _evidence(["a/x.py", "b/x.py"])
    verdict, support, _, *_ = path_exists_match("x.py", Context(), ev)
    assert verdict == "SUPPORTED"
    assert support == ("file:a/x.py", "file:b/x.py")


def test_match_multi_instance_init_py_supported() -> None:
    ev = _evidence(["pkg1/__init__.py", "pkg2/__init__.py"])
    verdict, support, _, *_ = path_exists_match("__init__.py", Context(), ev)
    assert verdict == "SUPPORTED"
    assert support == ("file:pkg1/__init__.py", "file:pkg2/__init__.py")


def test_match_bare_dir_ambiguous_exists_is_supported() -> None:
    # A bare directory name that exists in several places is a true claim.
    result = _match("examples/", None, _evidence(["docs/examples/", "src/examples/"]))
    assert result[0] == "SUPPORTED"
    assert result[1:] == ("dir:docs/examples/", "dir:src/examples/")


def test_match_slash_path_absent_stays_refuted() -> None:
    # A slash path that genuinely does not exist is still a finding when its
    # first segment is a real top-level directory.
    ev = _evidence(["docs/examples/", "a/only.py", "src/"])
    assert _match("src/ghost/", None, ev)[0] == "REFUTED"
    # ... but a path whose first segment is absent is unanchored → NEI.
    assert _match("z/ghost.py", None, ev)[0] == "NEI"


def test_match_extensionless_slash_absent_is_nei() -> None:
    # An extensionless slash token is often an enumeration of variants
    # (``gzip/bz2``, ``apache/airflow``), not a project file: the CLOSED world
    # abstains instead of refuting it.
    assert _match("gzip/bz2", None, {})[0] == "NEI"
    assert _match("try/except", None, {})[0] == "NEI"
    assert _match("apache/airflow", None, {})[0] == "NEI"
    assert _match("google-t5/t5-small", None, {})[0] == "NEI"


def test_match_extensionless_slash_present_is_supported() -> None:
    # A real extensionless slash path still resolves to evidence → SUPPORTED.
    ev = _evidence(["dev/breeze"])
    verdict, support, _, *_ = path_exists_match("dev/breeze", Context(), ev, source="README.md")
    assert verdict == "SUPPORTED"
    assert support == ("file:dev/breeze",)


def test_match_extensionless_slash_bare_name_last_segment_stays_refuted() -> None:
    # The final segment being a known bare-file name (``dockerfile``) keeps the
    # token a reliable anchor; a missing one under a real top-level is a finding.
    assert _match("dbt/dockerfile", None, _evidence(["dbt/"]))[0] == "REFUTED"
    assert _match("docs/readme", None, _evidence(["docs/"]))[0] == "REFUTED"


def test_match_extensionless_slash_unanchored_is_nei() -> None:
    # Without the top-level directory the extensionless slash mention is
    # unanchored → NEI (a bare-file last segment no longer forces REFUTED).
    assert _match("dbt/dockerfile", None, {})[0] == "NEI"
    assert _match("docs/readme", None, {})[0] == "NEI"


def test_match_trailing_slash_dir_without_extension_stays_refuted() -> None:
    # Trailing-slash directory claims are reliable anchors when the top-level
    # directory exists.
    assert _match("src/ghost/", None, _evidence(["src/"]))[0] == "REFUTED"


def test_match_trailing_slash_dir_unanchored_is_nei() -> None:
    assert _match("examples/", None, {})[0] == "NEI"


# --- downgrade signals: instruction / example / user config -------------------


def test_match_user_config_absent_is_nei() -> None:
    assert _match("airflow.cfg", None, {}, user_config=True)[0] == "NEI"


def test_match_user_config_with_evidence_is_supported() -> None:
    ev = _evidence(["airflow.cfg"])
    assert _match("airflow.cfg", None, ev, user_config=True)[0] == "SUPPORTED"


def test_match_user_config_negation_unchanged() -> None:
    assert _match("airflow.cfg", frozenset({"not"}), {}, user_config=True)[0] == "NEI"
    assert (
        _match("airflow.cfg", frozenset({"not"}), _evidence(["airflow.cfg"]), user_config=True)[0]
        == "REFUTED"
    )


def test_match_instructional_with_evidence_is_supported() -> None:
    assert _match("x.py", None, _evidence(["x.py"]), instructional=True)[0] == "SUPPORTED"


def test_instructional_flag_from_window() -> None:
    claims = _scan("Create a file called `x.py` for the new feature.\n")
    x_py = next(c for c in claims if c.object == "x.py")
    assert path_exists_flags(x_py)["instructional"] is True
    assert path_exists_flags(x_py)["exemplary"] is False
    claims = _scan("Create a directory called `artifacts/` for outputs.\n")
    artifacts = next(c for c in claims if c.object == "artifacts/")
    assert path_exists_flags(artifacts)["instructional"] is True


def test_exemplary_flag_from_window() -> None:
    claims = _scan("Add a file like `example.py` for tests.\n")
    example = next(c for c in claims if c.object == "example.py")
    assert path_exists_flags(example)["exemplary"] is True


def test_user_config_flag_from_window() -> None:
    claims = _scan("Configure your `airflow.cfg` before starting.\n")
    cfg = next(c for c in claims if c.object == "airflow.cfg")
    assert path_exists_flags(cfg)["user_config"] is True


def test_bare_dev_config_mention_is_not_user_config() -> None:
    # A bare mention of a dev-tool config that lives in the repo (``pytest.ini``)
    # or a code path ending in ``config.py`` stays a claim: only a config-shaped
    # artifact inside a configuring window is a runtime configuration.
    claims = _scan("The tests read the `pytest.ini` we ship.\n")
    ini = next(c for c in claims if c.object == "pytest.ini")
    assert path_exists_flags(ini)["user_config"] is False
    claims = _scan("`shared/config.py` you would have imported.\n")
    py = next(c for c in claims if c.object == "shared/config.py")
    assert path_exists_flags(py)["user_config"] is False


def test_reader_space_flag_from_window() -> None:
    # : second-person / tutorial / "will be saved to" cues mark a
    # reader-space mention — a would-be REFUTED path in such a window is not a
    # stale-repo-path finding.
    claims = _scan("Create a file called `app.py` in your project.\n")
    app = next(c for c in claims if c.object == "app.py")
    assert path_exists_flags(app)["reader_space"] is True
    claims = _scan("The output will be saved to `results.csv`.\n")
    res = next(c for c in claims if c.object == "results.csv")
    assert path_exists_flags(res)["reader_space"] is True
    # A plain descriptive mention stays a claim.
    claims = _scan("The project ships `results.csv`.\n")
    plain = next(c for c in claims if c.object == "results.csv")
    assert path_exists_flags(plain)["reader_space"] is False


def test_reader_space_absent_path_is_nei() -> None:
    assert _match("app.py", None, {}, reader_space=True)[0] == "NEI"


def test_reader_file_flag_from_name() -> None:
    claims = _scan("Set the version in `.cz.toml`.\n")
    cz = next(c for c in claims if c.object == ".cz.toml")
    assert path_exists_flags(cz)["reader_file"] is True
    # A slash path names a repo-relative location, not a reader file.
    claims = _scan("See `py-polars/cargo.toml`.\n")
    cargo = next(c for c in claims if c.object == "py-polars/cargo.toml")
    assert path_exists_flags(cargo)["reader_file"] is False


def test_reader_file_absent_is_nei() -> None:
    # A bare reader-project config/manifest that is absent is not a finding.
    assert _match(".cz.toml", None, {}, reader_file=True)[0] == "NEI"
    assert _match("pytest.toml", None, {}, reader_file=True)[0] == "NEI"


def test_reader_file_present_is_supported() -> None:
    ev = _evidence([".cz.toml"])
    assert _match(".cz.toml", None, ev)[0] == "SUPPORTED"


def test_reader_file_slashed_path_stays_refuted() -> None:
    # A slash-carrying repo-relative path keeps the CLOSED finding.
    ev = _evidence(["src/"])
    assert _match("py-polars/cargo.toml", None, ev)[0] == "NEI"  # unanchored head
    assert _match("src/py-polars/cargo.toml", None, ev)[0] == "REFUTED"


def test_external_software_name_is_nei() -> None:
    assert _match("python.h", None, {})[0] == "NEI"
    assert _match("robots.txt", None, {})[0] == "NEI"
    # A slash-carrying path under a real dir stays adjudicated.
    assert _match("src/python.h", None, _evidence(["src/"]))[0] == "REFUTED"


def test_generated_artifact_is_nei() -> None:
    # A ``*module.c`` f2py/swig wrapper is generated output (pattern-based).
    assert _match("fib1module.c", None, {})[0] == "NEI"
    # A project-specific generated name is not hardcoded; absence is refuted.
    assert _match("grammar.rs", None, {})[0] == "REFUTED"


def test_generated_mention_is_nei() -> None:
    claims = _scan("the generated header `dispatch_table.h` contains all definitions.\n")
    c = next(x for x in claims if x.object == "dispatch_table.h")
    assert path_exists_flags(c)["generated"] is True


def test_dot_fragment_name_is_nei() -> None:
    assert _match(".feature.rst", None, {})[0] == "NEI"


def test_placeholder_segment_path_is_nei() -> None:
    assert _match("src/mypkg/", None, _evidence(["src/"]))[0] == "NEI"
    assert _match("foo/bar/tests/test_foo.py", None, {})[0] == "NEI"
    assert _match("my_extension.pyx", None, {})[0] == "NEI"


def test_hidden_tool_dir_is_nei_but_tracked_dot_dirs_are_not() -> None:
    assert _match(".venv/", None, {})[0] == "NEI"
    assert _match(".git/", None, {})[0] == "NEI"
    # A tracked repo dot dir (``.cargo/``) stays adjudicated.
    assert _match(".cargo/config.toml", None, _evidence([".cargo/config.toml"]))[0] == "SUPPORTED"
    assert _match(".cargo/configx.toml", None, _evidence([".cargo/config.toml"]))[0] == "REFUTED"


def test_sphinx_file_role_bare_example_is_nei(tmp_path: Path) -> None:
    # ``:file:`` naming a bare example filename is a tutorial's reader-space
    # file, not a repo path claim (refined: ``:file:`` is a role,
    # not a reader-space cue by itself).
    (tmp_path / "README.md").write_text(
        _english_readme("The `:file:`layout.html` template defines the page skeleton.\n")
    )
    result = analyze_repository(tmp_path)
    refs = {r.object: r for r in result.referents if r.predicate_type == "PATH_EXISTS"}
    assert refs["layout.html"].assertions[0].code_verdict == "NEI"


def test_sphinx_file_role_slashed_path_is_adjudicated(tmp_path: Path) -> None:
    # A slash-carrying ``:file:`` role is a repo-relative path claim: a missing
    # file is a stale reference (REFUTED), not a reader-space example.
    (tmp_path / "requirements").mkdir()
    (tmp_path / "requirements" / "prod.txt").write_text("x\n")
    (tmp_path / "README.md").write_text(
        _english_readme("The full list is in `:file:`requirements/base.txt`.\n")
    )
    result = analyze_repository(tmp_path)
    refs = {r.object: r for r in result.referents if r.predicate_type == "PATH_EXISTS"}
    assert refs["requirements/base.txt"].assertions[0].code_verdict == "REFUTED"


def test_existence_verb_is_not_instructional() -> None:
    # "provides/include" are existence verbs, not generative instructions.
    claims = _scan("The project provides `utils/rustify.py`.\n")
    rustify = next(c for c in claims if c.object == "utils/rustify.py")
    assert path_exists_flags(rustify)["instructional"] is False


# --- pipeline over a real filesystem ----------------------------------------


def test_analyze_repository_supported(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").write_text("x = 1\n")
    (tmp_path / "README.md").write_text(_english_readme("The entry point lives in `src/a.py`.\n"))
    result = analyze_repository(tmp_path)
    refs = {r.object: r for r in result.referents if r.predicate_type == "PATH_EXISTS"}
    assert "src/a.py" in refs
    assert refs["src/a.py"].assertions[0].code_verdict == "SUPPORTED"


def test_analyze_repository_missing_file_is_finding(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "README.md").write_text(_english_readme("See `src/ghost.py`.\n"))
    result = analyze_repository(tmp_path)
    refs = {r.object: r for r in result.referents if r.predicate_type == "PATH_EXISTS"}
    assert "src/ghost.py" in refs
    assert refs["src/ghost.py"].assertions[0].code_verdict == "REFUTED"


def test_analyze_repository_missing_unanchored_file_is_nei(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text(_english_readme("See `src/ghost.py`.\n"))
    result = analyze_repository(tmp_path)
    refs = {r.object: r for r in result.referents if r.predicate_type == "PATH_EXISTS"}
    assert "src/ghost.py" in refs
    assert refs["src/ghost.py"].assertions[0].code_verdict == "NEI"


def test_analyze_repository_negation_with_present_file(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").write_text("x = 1\n")
    (tmp_path / "README.md").write_text(
        _english_readme("Note that `src/a.py` does not exist in this release.\n")
    )
    result = analyze_repository(tmp_path)
    refs = {r.object: r for r in result.referents if r.predicate_type == "PATH_EXISTS"}
    assert "src/a.py" in refs
    assert refs["src/a.py"].assertions[0].code_verdict == "REFUTED"


def test_analyze_repository_doc_relative_resolution(tmp_path: Path) -> None:
    (tmp_path / "test").mkdir()
    (tmp_path / "test" / "conftest.py").write_text("x = 1\n")
    (tmp_path / "test" / "AGENTS.md").write_text(
        _english_readme("Reusable test setup lives in `conftest.py`.\n")
    )
    result = analyze_repository(tmp_path)
    refs = {r.object: r for r in result.referents if r.predicate_type == "PATH_EXISTS"}
    assert "conftest.py" in refs
    assert refs["conftest.py"].assertions[0].code_verdict == "SUPPORTED"


def test_analyze_repository_supported_dir(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "README.md").write_text(_english_readme("Guides live in `docs/`.\n"))
    result = analyze_repository(tmp_path)
    refs = {r.object: r for r in result.referents if r.predicate_type == "PATH_EXISTS"}
    assert "docs/" in refs
    assert refs["docs/"].assertions[0].code_verdict == "SUPPORTED"


def test_analyze_repository_missing_directory_is_finding(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "README.md").write_text(_english_readme("See the `docs/ghost` directory.\n"))
    result = analyze_repository(tmp_path)
    refs = {r.object: r for r in result.referents if r.predicate_type == "PATH_EXISTS"}
    assert "docs/ghost/" in refs
    assert refs["docs/ghost/"].assertions[0].code_verdict == "REFUTED"


def test_analyze_repository_missing_top_level_directory_is_nei(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text(_english_readme("See the `examples` directory.\n"))
    result = analyze_repository(tmp_path)
    refs = {r.object: r for r in result.referents if r.predicate_type == "PATH_EXISTS"}
    assert "examples/" in refs
    assert refs["examples/"].assertions[0].code_verdict == "NEI"


def test_file_and_directory_referents_do_not_collide(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "index.md").write_text("# Docs\n")
    (tmp_path / "README.md").write_text(
        _english_readme("The docs live in `docs/`, with the entry point `docs/index.md`.\n")
    )
    result = analyze_repository(tmp_path)
    refs = {r.object: r for r in result.referents if r.predicate_type == "PATH_EXISTS"}
    assert set(refs) == {"docs/", "docs/index.md"}
    assert refs["docs/"].assertions[0].code_verdict == "SUPPORTED"
    assert refs["docs/index.md"].assertions[0].code_verdict == "SUPPORTED"


def test_evidence_sources_use_resolved_key(tmp_path: Path) -> None:
    # A bare name resolved doc-relative (``lib/README.md`` → ``lib/a.py``) must
    # surface its resolved source in evidence_sources, not stay empty because
    # the raw claim object (``a.py``) is not an inventory key.
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "demo"\n')
    (tmp_path / "lib").mkdir()
    (tmp_path / "lib" / "a.py").write_text("x = 1\n")
    (tmp_path / "lib" / "README.md").write_text(_english_readme("See `a.py` for the helper.\n"))
    result = analyze_repository(tmp_path)
    refs = {r.object: r for r in result.referents if r.predicate_type == "PATH_EXISTS"}
    assertion = refs["a.py"].assertions[0]
    assert assertion.code_verdict == "SUPPORTED"
    assert assertion.supporting_evidence == ("file:lib/a.py",)
    assert assertion.evidence_sources == ("lib/a.py",)


def test_refuted_wins_over_nei_in_cluster(tmp_path: Path) -> None:
    # A historical mention downgrades its own claim to NEI, but the cluster
    # also holds a plain claim about the same missing path: REFUTED wins and
    # code_conflicts pin the refuting claim.
    (tmp_path / "src").mkdir()
    (tmp_path / "README.md").write_text(
        "# Demo\n"
        "This is the demo project that many teams use every day.\n"
        "\n"
        "The previous `src/ghost.py` was removed in 2.0.\n"
        "\n"
        "But `src/ghost.py` is used by the runner.\n"
    )
    result = analyze_repository(tmp_path)
    refs = {r.object: r for r in result.referents if r.predicate_type == "PATH_EXISTS"}
    assertion = refs["src/ghost.py"].assertions[0]
    assert assertion.code_verdict == "REFUTED"
    assert assertion.code_conflicts == ("README.md:3:5",)
    assert assertion.refuting_evidence == ()


# --- git-tracked snapshot -----------------------------------


def _git_repo(root: Path, files: dict[str, str]) -> None:
    """Initialise a minimal git checkout with the given tracked files."""
    import subprocess

    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    subprocess.run(["git", "-C", str(root), "config", "user.email", "t@t"], check=True)
    subprocess.run(["git", "-C", str(root), "config", "user.name", "t"], check=True)
    subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(root), "commit", "-q", "-m", "init"], check=True)


def test_git_listing_ignores_untracked_files(tmp_path: Path) -> None:
    # A tracked doc reference is SUPPORTED; an untracked scratch file is NOT in
    # the CLOSED listing.
    _git_repo(
        tmp_path,
        {
            "README.md": _english_readme("The entry point lives in `src/a.py`.\n"),
            "src/a.py": "x = 1\n",
        },
    )
    (tmp_path / "scratch.py").write_text("y = 2\n")
    result = analyze_repository(tmp_path)
    refs = {r.object: r for r in result.referents if r.predicate_type == "PATH_EXISTS"}
    assert refs["src/a.py"].assertions[0].code_verdict == "SUPPORTED"
    assert "scratch.py" not in refs
    assert "scratch.py" not in {e.object for e in result.evidence}


def test_git_docs_not_pruned_by_skipped_dirs(tmp_path: Path) -> None:
    # ``sites/`` is a tracked documentation tree; SKIPPED_DIRS must not drop it
    # from the document set or the PATH_EXISTS listing (— paramiko's
    # sites/, sqlalchemy's doc/build/). ``sites`` is a gitignore-union member,
    # not an anchor-gated build artifact, so a reference to it is adjudicated.
    _git_repo(
        tmp_path,
        {
            "README.md": _english_readme("Guides are in `sites/`.\n"),
            "sites/index.md": "# Generated guide\nSee `sites/index.md` for details.\n",
        },
    )
    result = analyze_repository(tmp_path)
    assert any(rel == "sites/index.md" for rel, _ in collect_documents(tmp_path))
    assert {e.object for e in result.evidence if e.object.startswith("sites")} >= {
        "sites/",
        "sites/index.md",
    }
    assert any(
        r.predicate_type == "PATH_EXISTS"
        and r.object == "sites/"
        and r.assertions[0].code_verdict == "SUPPORTED"
        for r in result.referents
    )


def test_git_listing_refreshed_between_analyses(tmp_path: Path) -> None:
    # A long-lived process re-analyzes a clone updated in place under the same
    # root: the second analysis must see the newly committed file.
    import subprocess

    _git_repo(
        tmp_path,
        {"README.md": _english_readme("The helper lives in `src/b.py`.\n"), "src/a.py": "x = 1\n"},
    )
    first = analyze_repository(tmp_path)
    refs = {r.object: r for r in first.referents if r.predicate_type == "PATH_EXISTS"}
    assert refs["src/b.py"].assertions[0].code_verdict == "REFUTED"
    (tmp_path / "src" / "b.py").write_text("y = 2\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(tmp_path), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "commit", "-q", "-m", "add b"], check=True)
    second = analyze_repository(tmp_path)
    refs = {r.object: r for r in second.referents if r.predicate_type == "PATH_EXISTS"}
    assert refs["src/b.py"].assertions[0].code_verdict == "SUPPORTED"


def test_case_only_match_is_supported_with_hint(tmp_path: Path) -> None:
    # Case-insensitive matching stays; the reader still learns the tree spelling.
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "Guide.md").write_text("# Guide\n", encoding="utf-8")
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").write_text("x = 1\n", encoding="utf-8")
    (tmp_path / "README.md").write_text(
        _english_readme("Read `docs/guide.md` first, then `src/a.py`.\n"), encoding="utf-8"
    )
    result = analyze_repository(tmp_path)
    refs = {r.object: r for r in result.referents if r.predicate_type == "PATH_EXISTS"}
    guide = refs["docs/guide.md"].assertions[0]
    assert guide.code_verdict == "SUPPORTED"
    assert guide.code_verdict_layer == ""
    assert guide.code_verdict_reason == "case differs: docs/Guide.md"
    assert refs["src/a.py"].assertions[0].code_verdict_reason == ""


def test_unanchored_path_abstains_in_claim_gate() -> None:
    # The listing is complete, so a path under no top-level directory of the
    # repository is a claim-gate abstention, not an inventory gap (WORLD).
    from docassay.predicates.listing import path_exists_match

    for path in ("z/ghost.py", "z/ghost/"):
        verdict = path_exists_match(path, Context(), _evidence(["docs/"]))
        assert (verdict.outcome, verdict.layer) == ("NEI", "CLAIM_GATE")
        assert verdict.reason == "top-level directory absent from repository"
