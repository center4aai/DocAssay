"""Tests for the SYMBOL_EXISTS predicate (structure group).

One predicate for every structural symbol of the project's own code (modules,
classes, functions, methods, fields). Extraction is anchor-first over dotted,
call and noun-gated tokens; matching is presence against the project's own
Python AST inventory (CLOSED over project), with third-party, builtin and bare
call mentions staying NEI.
"""

from __future__ import annotations

from pathlib import Path

from docassay.core.models import Context, PredicateClaim
from docassay.core.pipeline import analyze_repository
from docassay.evidence.symbols import SymbolEvidence, build_symbol_inventory
from docassay.predicates.structure import (
    SYMBOL_EXISTS_WORLD,
    symbol_exists_flags,
    symbol_exists_match,
    symbol_exists_scan,
)
from docassay.vocabularies.structure import resolve_symbol_key


def _scan(text: str) -> list[PredicateClaim]:
    return symbol_exists_scan(text, "README.md")


def _objects(text: str) -> set[str]:
    return {c.object for c in _scan(text)}


def _english_readme(body: str) -> str:
    return "# Demo project\nThis is the demo project that many teams use every day.\n" + body


# --- extraction: dotted --------------------------------------------------------


def test_dotted_token_is_anchor() -> None:
    assert _objects("Import `pkg.mod` for details.\n") == {"pkg.mod"}


def test_nested_dotted_class_is_anchor() -> None:
    assert _objects("The `pkg.mod.Class` defines the API.\n") == {"pkg.mod.class"}


def test_dotted_module_noun_phrase_is_anchor() -> None:
    assert _objects("The `pkg.mod` module defines the API.\n") == {"pkg.mod"}


def test_dotted_method_noun_phrase_is_anchor() -> None:
    assert _objects("The `engine.run` method handles tasks.\n") == {"engine.run"}


def test_single_package_noun_phrase_is_anchor() -> None:
    assert _objects("See the `airflow` package for core types.\n") == {"airflow"}


def test_class_noun_phrase_is_anchor() -> None:
    assert _objects("The `Linter` class is exported.\n") == {"linter"}


# --- extraction: call ----------------------------------------------------------


def test_bare_call_is_anchor() -> None:
    assert _objects("Call `parse()` to load data.\n") == {"parse"}


def test_dotted_call_is_anchor() -> None:
    assert _objects("Call `obj.parse()` now.\n") == {"obj.parse"}


# --- extraction: noun-gated fields ----------------------------------------------


def test_field_noun_phrase_is_anchor() -> None:
    assert _objects("The `status` attribute is set.\n") == {"status"}
    assert _objects("Set the `max_iters` field.\n") == {"max_iters"}
    assert _objects("Read the `result` property.\n") == {"result"}
    assert _objects("The argument `n_jobs` controls this.\n") == {"n_jobs"}


# --- extraction: non-anchors ----------------------------------------------------


def test_plain_backtick_word_is_not_anchor() -> None:
    assert _objects("The `model` is exported.\n") == set()


def test_path_token_is_not_anchor() -> None:
    assert _objects("See `src/a.py` for the entry point.\n") == set()
    assert _objects("Guides live in `docs/`.\n") == set()


def test_file_extension_token_is_not_anchor() -> None:
    assert _objects("The build config is `pkg.mod.py`.\n") == set()


def test_numeric_version_is_not_anchor() -> None:
    assert _objects("Requires version `2.4.1` or higher.\n") == set()


def test_sphinx_role_is_not_anchor() -> None:
    assert _objects("See :mod:`pkg.mod` for details.\n") == set()


def test_pypi_role_is_not_anchor() -> None:
    assert _objects("The backend requires the :pypi:`boto3` library.\n") == set()


def test_hostname_is_not_a_closed_finding() -> None:
    # A backticked project-owned domain (``airflow.apache.org``) is a *scan*
    # anchor candidate, but an unresolved dotted claim whose last segment is a
    # host TLD abstains (NEI) instead of REFUTING — the scan must not silently
    # drop dotted tokens on an arbitrary TLD allowlist, because real modules end
    # in ``.io``/``.app``/``.ai`` (``airflow.providers.common.io``).
    assert _objects("Published on `airflow.apache.org`.\n") == {"airflow.apache.org"}
    assert _match("airflow.apache.org", evidence=_evidence(["airflow"]))[0] == "NEI"


def test_chart_value_in_configuring_window_is_not_anchor() -> None:
    assert _objects("Set `airflow.enabled` inside your `values.yaml`.\n") == set()


def test_entrypoint_group_is_not_anchor() -> None:
    assert _objects("The entrypoint group must be `airflow.policy`.\n") == set()


def test_placeholder_dotted_is_not_anchor() -> None:
    assert _objects("See `sklearn.foo.bar` in the dev docs.\n") == set()


def test_non_identifier_field_is_not_anchor() -> None:
    assert _objects("The `data-testid` attribute is used.\n") == set()
    assert _objects("The `*time.Time` field is populated.\n") == set()
    assert _objects("Pass the `--source` argument.\n") == set()


def test_whitespace_token_is_not_anchor() -> None:
    assert _objects("Run `pip install django` to get started.\n") == set()


# --- context / flags ------------------------------------------------------------


def test_negation_attaches_to_dotted_symbol() -> None:
    claims = _scan("The `pkg.mod` module does not exist anymore.\n")
    pkg_mod = next(c for c in claims if c.object == "pkg.mod")
    assert pkg_mod.is_negative is True


def test_anchor_type_is_recorded() -> None:
    calls = _scan("Call `parse()` to load data.\n")
    assert next(c for c in calls if c.object == "parse").anchor_type == "call"
    dotted = _scan("Import `pkg.mod` for details.\n")
    assert next(c for c in dotted if c.object == "pkg.mod").anchor_type == "dotted"
    noun = _scan("The `limit` field caps rows.\n")
    assert next(c for c in noun if c.object == "limit").anchor_type == "noun"


def test_removed_is_historical() -> None:
    claims = _scan("The old `legacy_func` function was removed in 2.0.\n")
    legacy = next(c for c in claims if c.object == "legacy_func")
    assert symbol_exists_flags(legacy)["historical"] is True


def test_instructional_flag_from_window() -> None:
    claims = _scan("Create the `load_config` function for the new feature.\n")
    load_config = next(c for c in claims if c.object == "load_config")
    assert symbol_exists_flags(load_config)["instructional"] is True


def test_instructional_flag_requires_sentence_initial_verb() -> None:
    # c: a descriptive sentence that merely CONTAINS a
    # generative verb ("imported") is not an instruction — the flag must not
    # silence a stale-symbol finding.
    claims = _scan("The `pkg.old_module.helper()` function is imported lazily.\n")
    helper = next(c for c in claims if c.object == "pkg.old_module.helper")
    assert symbol_exists_flags(helper)["instructional"] is False


def test_exemplary_flag_from_window() -> None:
    claims = _scan("Add a `parse` function, such as the one in the example.\n")
    parse = next(c for c in claims if c.object == "parse")
    assert symbol_exists_flags(parse)["exemplary"] is True


def test_world_is_closed_over_project() -> None:
    assert SYMBOL_EXISTS_WORLD == "closed-over-project"


# --- inventory -----------------------------------------------------------------


def _write_package(tmp_path: Path) -> None:
    (tmp_path / "src" / "pkg").mkdir(parents=True)
    (tmp_path / "src" / "pkg" / "__init__.py").write_text("")
    (tmp_path / "src" / "pkg" / "mod.py").write_text(
        'CONFIG = "x"\n\n'
        "def parse(data):\n"
        "    return data\n\n"
        "class Parser:\n"
        "    limit = 10\n"
        "    def parse_string(self):\n"
        '        return ""\n'
    )
    (tmp_path / "app.py").write_text("def main():\n    pass\n")


def _objects_by_kind(tmp_path: Path, kind: str) -> set[str]:
    return {e.object for e in build_symbol_inventory(tmp_path, kind=kind)}


def test_module_inventory(tmp_path: Path) -> None:
    _write_package(tmp_path)
    assert _objects_by_kind(tmp_path, "module") == {"pkg", "pkg.mod", "app"}


def test_class_inventory(tmp_path: Path) -> None:
    _write_package(tmp_path)
    assert _objects_by_kind(tmp_path, "class") == {"pkg.mod.parser"}


def test_function_inventory(tmp_path: Path) -> None:
    _write_package(tmp_path)
    assert _objects_by_kind(tmp_path, "function") == {"app.main", "pkg.mod.parse"}


def test_method_inventory(tmp_path: Path) -> None:
    _write_package(tmp_path)
    assert _objects_by_kind(tmp_path, "method") == {"pkg.mod.parser.parse_string"}


def test_field_inventory(tmp_path: Path) -> None:
    _write_package(tmp_path)
    assert _objects_by_kind(tmp_path, "field") == {"pkg.mod.config", "pkg.mod.parser.limit"}


def test_namespace_package_is_importable(tmp_path: Path) -> None:
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "mod.py").write_text("def f():\n    return 1\n")
    assert "pkg" in _objects_by_kind(tmp_path, "module")
    assert "pkg.mod" in _objects_by_kind(tmp_path, "module")


def test_non_package_dir_is_not_importable(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "index.rst").write_text("docs\n")
    assert _objects_by_kind(tmp_path, "module") == set()


def test_namespace_dir_with_python_is_importable(tmp_path: Path) -> None:
    (tmp_path / "worker").mkdir()
    (tmp_path / "worker" / "helper.py").write_text("def x():\n    pass\n")
    assert "worker" in _objects_by_kind(tmp_path, "module")
    assert "worker.helper" in _objects_by_kind(tmp_path, "module")


def test_type_checking_and_nested_classes_are_emitted(tmp_path: Path) -> None:
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "__init__.py").write_text("")
    (tmp_path / "pkg" / "mod.py").write_text(
        "from typing import TYPE_CHECKING\n"
        "class Outer:\n"
        "    class Inner:\n"
        "        def method(self):\n"
        "            pass\n"
        "    def outer_method(self):\n"
        "        pass\n"
        "if TYPE_CHECKING:\n"
        "    class TypeOnly:\n"
        "        def f(self):\n"
        "            pass\n"
    )
    objects = _objects_by_kind(tmp_path, "class") | _objects_by_kind(tmp_path, "method")
    assert "pkg.mod.outer" in objects
    assert "pkg.mod.outer.inner" in objects
    assert "pkg.mod.outer.inner.method" in objects
    assert "pkg.mod.outer.outer_method" in objects
    assert "pkg.mod.typeonly" in objects
    assert "pkg.mod.typeonly.f" in objects


def test_long_reexport_chain_resolves(tmp_path: Path) -> None:
    # A re-export chain longer than the old 4-round fixpoint cap must still
    # converge (a → b → … → h → __init__).
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "__init__.py").write_text("from .h import X\n")
    (tmp_path / "pkg" / "a.py").write_text("X = 1\n")
    for letter in "bcdefgh":
        previous = chr(ord(letter) - 1)
        (tmp_path / "pkg" / f"{letter}.py").write_text(f"from .{previous} import X\n")
    by_name: dict[str, list[SymbolEvidence]] = {}
    for e in build_symbol_inventory(tmp_path):
        by_name.setdefault(e.object, []).append(e)
    assert "pkg.x" in by_name
    assert "pkg.h.x" in by_name
    assert "pkg.b.x" in by_name
    assert resolve_symbol_key("pkg.x", by_name) == "pkg.x"


def test_non_code_dir_is_not_a_namespace_package(tmp_path: Path) -> None:
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "helper.py").write_text("def x():\n    pass\n")
    assert _objects_by_kind(tmp_path, "module") == set()


# --- matching ------------------------------------------------------------------


def _evidence(objects: list[str], kind: str = "module") -> dict[str, list[SymbolEvidence]]:
    by_name: dict[str, list[SymbolEvidence]] = {}
    for i, name in enumerate(objects):
        by_name.setdefault(name, []).append(
            SymbolEvidence(
                evidence_id=f"{kind}:{name}:{i}",
                name=name,
                kind=kind,
                qualified_name=name,
                source_file="mod.py",
                line=1,
            )
        )
    return by_name


def _match(
    object: str,
    polarity: frozenset[str] | None = None,
    evidence: dict | None = None,
    **flags,
) -> tuple:
    context = Context(polarity=frozenset(polarity or ()))
    verdict, support, refute, *_ = symbol_exists_match(object, context, evidence or {}, **flags)
    return (verdict, *support, *refute)


def test_match_present_supported() -> None:
    assert _match("pkg.mod", evidence=_evidence(["pkg.mod"]))[0] == "SUPPORTED"


def test_match_class_reference_supported() -> None:
    ev = _evidence(["airflow.datasets.dataset"], kind="class")
    assert _match("airflow.datasets.dataset", evidence=ev)[0] == "SUPPORTED"


def test_match_class_shaped_name_against_module_is_refuted() -> None:
    # ``mypkg.Client`` names a class; only the module ``mypkg.client`` exists,
    # so the class the doc references is absent.
    ev = _evidence(["mypkg.client"], kind="module")
    assert _match("mypkg.client", evidence=ev, raw_object="mypkg.Client")[0] == "REFUTED"


def test_match_lowercased_class_reference_stays_supported() -> None:
    # Docs routinely lowercase CamelCase classes; a lowercase doc name is not a
    # class-vs-module finding.
    ev = _evidence(["pkg.mod.parser"], kind="class")
    assert _match("pkg.mod.parser", evidence=ev, raw_object="pkg.mod.Parser")[0] == "SUPPORTED"


def test_match_capitalized_module_own_spelling_supported() -> None:
    # A module whose own name is capitalized is not the lowercase-neighbour case.
    ev = {
        "pkg.mymodule": [
            SymbolEvidence(
                evidence_id="module:pkg.MyModule:x",
                name="pkg.mymodule",
                kind="module",
                qualified_name="pkg.MyModule",
                source_file="MyModule.py",
                line=1,
            )
        ]
    }
    assert _match("pkg.mymodule", evidence=ev, raw_object="pkg.MyModule")[0] == "SUPPORTED"


def test_match_suffix_resolution_supported() -> None:
    ev = _evidence(["airflow.hooks.base.basehook.get_connection"], kind="method")
    assert _match("basehook.get_connection", evidence=ev)[0] == "SUPPORTED"


def test_match_last_segment_fallback_supported() -> None:
    # A re-exported symbol: the claim names a different intermediate module than
    # the fact, but its tail after the top package (``logging.critical``) is a
    # suffix of the key.
    ev = _evidence(["transformers.utils.logging.critical"], kind="function")
    assert _match("transformers.logging.critical", evidence=ev)[0] == "SUPPORTED"


def test_match_third_party_dotted_is_nei_not_supported() -> None:
    # ``logging.debug`` shares a last segment with a project symbol but its top
    # segment is not a project package: last-segment resolution must not match
    # it (previously a false SUPPORTED against ``mlflow.…debug``).
    ev = _evidence(["mlflow.entities.span_log_level.spanloglevel.debug"], kind="method")
    assert _match("logging.debug", evidence=ev)[0] == "NEI"
    assert _match("os.path.join", evidence=ev)[0] == "NEI"


def test_match_suffix_reference_across_third_party_top_stays() -> None:
    # A shortened reference whose claimed name is a *suffix* of the resolved
    # key stays SUPPORTED even when the claimed top segment is not a top-level
    # package (``basehook`` is a class, not a package).
    ev = _evidence(["airflow.hooks.base.basehook.get_connection"], kind="method")
    assert _match("basehook.get_connection", evidence=ev)[0] == "SUPPORTED"


def test_reexport_from_guarded_if_is_emitted(tmp_path: Path) -> None:
    # Feature-flag guarded re-exports are public API (``if not FLAG: from .m
    # import X``) and must emit the alias (the mlflow.autolog gap).
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "__init__.py").write_text(
        "FLAG = False\nif not FLAG:\n    from .m import autolog\n"
    )
    (tmp_path / "pkg" / "m.py").write_text("def autolog():\n    pass\n")
    by_name: dict[str, list[SymbolEvidence]] = {}
    for e in build_symbol_inventory(tmp_path):
        by_name.setdefault(e.object, []).append(e)
    assert "pkg.autolog" in by_name
    assert resolve_symbol_key("pkg.autolog", by_name) == "pkg.autolog"
    assert _match("pkg.autolog", evidence=by_name)[0] == "SUPPORTED"


def test_match_bare_unique_supported() -> None:
    ev = _evidence(["pkg.mod.parse"], kind="function")
    assert _match("parse", evidence=ev)[0] == "SUPPORTED"


def test_match_bare_ambiguous_supported() -> None:
    ev = _evidence(["a.parse", "b.parse"], kind="function")
    result = _match("parse", evidence=ev)
    assert result[0] == "SUPPORTED"
    assert len(result[1:]) == 2


def test_match_dotted_absent_project_refuted() -> None:
    ev = _evidence(["pkg", "pkg.mod"])
    assert _match("pkg.ghost", evidence=ev)[0] == "REFUTED"


def test_match_dotted_third_party_nei() -> None:
    assert _match("flask.sessions", evidence={})[0] == "NEI"


def test_match_dotted_stdlib_nei() -> None:
    assert _match("datetime.now", evidence={})[0] == "NEI"


def test_match_bare_unresolved_nei() -> None:
    # A bare mention is never a CLOSED finding: it could be a parameter, a
    # builtin or an external symbol.
    assert _match("issubclass")[0] == "NEI"
    assert _match("get_chat_model")[0] == "NEI"
    assert _match("ghost")[0] == "NEI"


def test_match_negation_with_evidence_refuted() -> None:
    ev = _evidence(["pkg.mod"])
    assert _match("pkg.mod", polarity=frozenset({"not"}), evidence=ev)[0] == "REFUTED"


def test_match_negation_without_evidence_nei() -> None:
    assert _match("pkg.mod", polarity=frozenset({"not"}))[0] == "NEI"


def test_match_historical_absent_nei() -> None:
    assert _match("pkg.ghost", evidence=_evidence(["pkg"]), historical=True)[0] == "NEI"


def test_match_instructional_absent_nei() -> None:
    assert _match("pkg.ghost", evidence=_evidence(["pkg"]), instructional=True)[0] == "NEI"


# --- pipeline over a real filesystem -------------------------------------------


def test_analyze_repository_symbols_supported(tmp_path: Path) -> None:
    _write_package(tmp_path)
    (tmp_path / "README.md").write_text(
        _english_readme(
            "The `pkg.mod` module defines `parse()` and the `Parser` class; "
            "the `limit` field controls the parser.\n"
        )
    )
    result = analyze_repository(tmp_path)
    by_object = {r.object: r for r in result.referents if r.predicate_type == "SYMBOL_EXISTS"}
    assert by_object["pkg.mod"].assertions[0].code_verdict == "SUPPORTED"
    assert by_object["parse"].assertions[0].code_verdict == "SUPPORTED"
    assert by_object["parser"].assertions[0].code_verdict == "SUPPORTED"
    assert by_object["limit"].assertions[0].code_verdict == "SUPPORTED"


def test_analyze_repository_missing_symbol_is_finding(tmp_path: Path) -> None:
    _write_package(tmp_path)
    (tmp_path / "README.md").write_text(
        _english_readme("The `pkg.ghost` module provides the CLI.\n")
    )
    result = analyze_repository(tmp_path)
    refs = {r.object: r for r in result.referents if r.predicate_type == "SYMBOL_EXISTS"}
    assert "pkg.ghost" in refs
    assert refs["pkg.ghost"].assertions[0].code_verdict == "REFUTED"


def test_analyze_repository_third_party_symbol_is_nei(tmp_path: Path) -> None:
    _write_package(tmp_path)
    (tmp_path / "README.md").write_text(
        _english_readme("The `flask.sessions` module provides web helpers.\n")
    )
    result = analyze_repository(tmp_path)
    refs = {r.object: r for r in result.referents if r.predicate_type == "SYMBOL_EXISTS"}
    assert "flask.sessions" in refs
    assert refs["flask.sessions"].assertions[0].code_verdict == "NEI"


# --- segment-overlap resolution (2026-09-01, tightened 2026-09-13 P2/B3) --------


def test_match_three_segment_claim_does_not_guess_intermediate_module() -> None:
    # A 3+ segment claim whose tail after the top package is NOT a suffix of a
    # key no longer resolves through a shared last segment:
    # ``scipy.stats.bernoulli`` must not be confirmed by
    # ``scipy.special._basic.bernoulli`` — the public alias must exist in the
    # inventory (the re-export pass emits it), not be guessed from a fragment.
    ev = _evidence(
        ["scipy.special._basic.bernoulli", "scipy.stats._discrete_distns.bernoulli"],
        kind="field",
    )
    assert _match("scipy.stats.bernoulli", evidence=ev)[0] == "REFUTED"


def test_match_three_segment_tail_after_top_suffix_supported() -> None:
    # ``transformers.logging.critical`` → ``transformers.utils.logging.critical``:
    # the tail after the top package (``logging.critical``) is a suffix of the
    # key with the same top, so the shortened reference stays SUPPORTED.
    ev = _evidence(["transformers.utils.logging.critical"], kind="function")
    assert _match("transformers.logging.critical", evidence=ev)[0] == "SUPPORTED"


def test_match_three_segment_renamed_module_refuted() -> None:
    # ``pkg.legacy.func`` when the module was renamed to ``pkg.cli.func``: the
    # tail ``legacy.func`` is not a suffix of any key — a genuine stale claim.
    ev = _evidence(["pkg.cli.func"], kind="function")
    assert _match("pkg.legacy.func", evidence=ev)[0] == "REFUTED"


def test_match_three_segment_suffix_of_key_supported() -> None:
    # A claim that IS a segment suffix of a key (``symbolic.op.array`` of
    # ``numpy.f2py.symbolic.op.array``) still resolves; a last-segment-only
    # overlap (``numpy.array_api.array`` — the B3 false SUPPORTED) does not.
    ev = _evidence(["numpy.f2py.symbolic.op.array"], kind="field")
    assert _match("numpy.array_api.array", evidence=ev)[0] == "REFUTED"
    assert _match("symbolic.op.array", evidence=ev)[0] == "SUPPORTED"


def test_match_cython_named_module_is_nei() -> None:
    ev = _evidence(["pkg.linalg"], kind="module")
    assert _match("pkg.linalg.cython_blas", evidence=ev)[0] == "NEI"


# --- re-exports, stubs and Cython surfaces (2026-09-01) -------------------------


def test_reexport_alias_resolves_public_name(tmp_path: Path) -> None:
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "__init__.py").write_text("from ._impl import make_thing\n")
    (tmp_path / "pkg" / "_impl.py").write_text("def make_thing():\n    return 1\n")
    (tmp_path / "README.md").write_text(
        _english_readme("The `pkg.make_thing` function builds the widget.\n")
    )
    result = analyze_repository(tmp_path)
    refs = {r.object: r for r in result.referents if r.predicate_type == "SYMBOL_EXISTS"}
    assert refs["pkg.make_thing"].assertions[0].code_verdict == "SUPPORTED"


def test_reexport_alias_in_try_block(tmp_path: Path) -> None:
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "__init__.py").write_text(
        "try:\n    from pkg.__config__ import show as show_config\nexcept ImportError:\n    raise\n"
    )
    (tmp_path / "pkg" / "__config__.py").write_text("def show():\n    return None\n")
    (tmp_path / "README.md").write_text(
        _english_readme("The `pkg.show_config` command inspects the build.\n")
    )
    result = analyze_repository(tmp_path)
    refs = {r.object: r for r in result.referents if r.predicate_type == "SYMBOL_EXISTS"}
    assert refs["pkg.show_config"].assertions[0].code_verdict == "SUPPORTED"


def test_reexport_public_name_from_generated_module(tmp_path: Path) -> None:
    """A re-export from a module absent from the tree (build-generated) is still
    source-level truth that the public name exists."""
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "__init__.py").write_text(
        "from pkg.__config__ import show as show_config\n"
    )
    (tmp_path / "README.md").write_text(
        _english_readme("The `pkg.show_config` command inspects the build.\n")
    )
    result = analyze_repository(tmp_path)
    refs = {r.object: r for r in result.referents if r.predicate_type == "SYMBOL_EXISTS"}
    assert refs["pkg.show_config"].assertions[0].code_verdict == "SUPPORTED"


def test_pyi_stub_symbol_is_supported(tmp_path: Path) -> None:
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "__init__.py").write_text("")
    (tmp_path / "pkg" / "_ufuncs.pyi").write_text("k1: object\n")
    (tmp_path / "README.md").write_text(
        _english_readme("Use `pkg._ufuncs.k1` for the Bessel function.\n")
    )
    result = analyze_repository(tmp_path)
    refs = {r.object: r for r in result.referents if r.predicate_type == "SYMBOL_EXISTS"}
    assert refs["pkg._ufuncs.k1"].assertions[0].code_verdict == "SUPPORTED"


def test_cython_cdef_class_symbol_is_supported(tmp_path: Path) -> None:
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "__init__.py").write_text("")
    (tmp_path / "pkg" / "_wrapper.pyx").write_text("cdef class DiscreteAliasUrn:\n    pass\n")
    (tmp_path / "README.md").write_text(
        _english_readme("Use `pkg._wrapper.discretealiasurn` to sample.\n")
    )
    result = analyze_repository(tmp_path)
    refs = {r.object: r for r in result.referents if r.predicate_type == "SYMBOL_EXISTS"}
    assert refs["pkg._wrapper.discretealiasurn"].assertions[0].code_verdict == "SUPPORTED"


def test_opaque_cython_module_missing_symbol_is_nei(tmp_path: Path) -> None:
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "__init__.py").write_text("")
    (tmp_path / "pkg" / "_wrapper.pyx").write_text("cdef class Known:\n    pass\n")
    (tmp_path / "README.md").write_text(
        _english_readme("Use `pkg._wrapper.unknown_symbol` in the API.\n")
    )
    result = analyze_repository(tmp_path)
    refs = {r.object: r for r in result.referents if r.predicate_type == "SYMBOL_EXISTS"}
    assert refs["pkg._wrapper.unknown_symbol"].assertions[0].code_verdict == "NEI"


def test_tld_ending_symbol_that_exists_is_supported() -> None:
    # A real symbol whose last segment is an IANA TLD (`typer.run`,
    # `pytest.fail`, `numpy.save`) must resolve; the gate no longer drops it
    # before the inventory.
    assert _match("typer.run", evidence=_evidence(["typer.run"], kind="function"))[0] == "SUPPORTED"


def test_unresolved_tld_ending_symbol_abstains() -> None:
    # A website mention (`docs.sqlfluff.com`) that does NOT resolve against the
    # inventory stays NEI, not REFUTED (match-layer host-TLD guard).
    assert _match("docs.sqlfluff.com", evidence=_evidence(["pkg.mod"]))[0] == "NEI"


# --- dynamic surfaces ------------------------------------------


def test_module_getattr_is_dynamic_surface() -> None:
    # A module with a module-level ``__getattr__`` (PEP 562) serves missing
    # attributes at runtime (`click.get_text_stream`): absence is not conclusive.
    ev = _evidence(["pkg.mod", "pkg.mod.__getattr__"], kind="function")
    assert _match("pkg.mod.get_text_stream", evidence=ev)[0] == "NEI"


def test_module_without_getattr_refutes() -> None:
    # Without a dynamic surface, a missing attribute stays a CLOSED finding.
    ev = _evidence(["pkg.mod"], kind="module")
    assert _match("pkg.mod.get_text_stream", evidence=ev)[0] == "REFUTED"


def test_pytest_mark_namespace_is_dynamic_surface() -> None:
    # ``pytest.mark.*`` members are constructed at runtime by MarkGenerator —
    # a claim about one abstains instead of refuting.
    ev = _evidence(["pytest", "pytest.mark"], kind="field")
    assert _match("pytest.mark.parametrize", evidence=ev)[0] == "NEI"


# --- git-tracked AST walk --------------------------------------


def _git_init(root: Path) -> None:
    import subprocess

    subprocess.run(["git", "init", "-q", str(root)], check=True)
    subprocess.run(["git", "-C", str(root), "config", "user.email", "t@t"], check=True)
    subprocess.run(["git", "-C", str(root), "config", "user.name", "t"], check=True)
    subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(root), "commit", "-q", "-m", "init"], check=True)


def test_git_tracked_env_dir_is_walked(tmp_path: Path) -> None:
    # ``env/`` is a gitignore-union member, but a *tracked* source dir under it
    # is real code (poetry ``src/poetry/utils/env/``): the git-tree AST walk
    # keeps it instead of pruning it via SKIPPED_DIRS.
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "__init__.py").write_text("")
    (tmp_path / "pkg" / "env").mkdir()
    (tmp_path / "pkg" / "env" / "__init__.py").write_text("")
    (tmp_path / "pkg" / "env" / "helper.py").write_text("def ping():\n    pass\n")
    _git_init(tmp_path)
    objects = {e.object for e in build_symbol_inventory(tmp_path)}
    assert "pkg.env.helper" in objects
    assert "pkg.env.helper.ping" in objects


def test_class_vs_module_refutation_carries_hint_without_layer(tmp_path: Path) -> None:
    # A resolved verdict has no layer; the "did you mean" hint travels in the
    # assertion's reason so the report and the UI can show it.
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "demo"\n', encoding="utf-8")
    (tmp_path / "demo").mkdir()
    (tmp_path / "demo" / "__init__.py").write_text("", encoding="utf-8")
    (tmp_path / "demo" / "client.py").write_text("def connect():\n    pass\n", encoding="utf-8")
    (tmp_path / "README.md").write_text(
        _english_readme("The class `demo.Client` opens the connection.\n"), encoding="utf-8"
    )
    result = analyze_repository(tmp_path)
    refs = {r.object: r for r in result.referents if r.predicate_type == "SYMBOL_EXISTS"}
    assertion = refs["demo.client"].assertions[0]
    assert assertion.code_verdict == "REFUTED"
    assert assertion.code_verdict_layer == ""
    assert "did you mean: demo.client" in assertion.code_verdict_reason


def test_case_hint_helper() -> None:
    from docassay.predicates.base import case_hint

    assert case_hint("demo.widgets", ["demo.Widgets"], ".") == "case differs: demo.Widgets"
    assert case_hint("demo.Widgets", ["demo.Widgets"], ".") == ""
    assert case_hint("`demo.run()`", ["demo.Run"], ".") == "case differs: demo.Run"
    assert case_hint("guide.md", ["docs/Guide.md"]) == "case differs: docs/Guide.md"
    assert case_hint("ide.md", ["docs/Guide.md"]) == ""


def test_case_hint_ignores_lowercased_alias_keys() -> None:
    from docassay.predicates.base import case_hint

    assert case_hint("aiohttp.ClientSession", ["aiohttp.clientsession"], ".") == ""
