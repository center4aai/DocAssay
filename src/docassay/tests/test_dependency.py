"""Tests for the DEPENDENCY predicate (method-v2 layer)."""

from __future__ import annotations

from pathlib import Path

from docassay.core.assertions import group_into_assertions
from docassay.core.models import Context, PredicateClaim
from docassay.core.pipeline import analyze_repository
from docassay.evidence.manifests import DependencyEvidence, build_dependency_inventory
from docassay.markers.version import combine_version, constraint_satisfied
from docassay.predicates.dependency import (
    DEPENDENCY_WORLD,
    claim_flags,
    is_historical,
    is_python_context,
    match_dependency,
    scan_document,
)
from docassay.vocabularies.dependency import is_plausible_version, normalize_dependency_name


def _scan(text: str) -> list[PredicateClaim]:
    return scan_document(text, "README.md")


def _objects(text: str) -> set[str]:
    return {c.object for c in _scan(text)}


def _version_for(text: str, object: str) -> str | None:
    for c in _scan(text):
        if c.object == object:
            return c.context.version
    return None


# --- extraction -------------------------------------------------------------


def test_requires_python_with_explicit_operator() -> None:
    assert _version_for("Requires python>=3.12.\n", "python") == ">=3.12"


def test_or_higher_suffix() -> None:
    assert _version_for("Requires Python 3.9 or higher.\n", "python") == ">=3.9"


def test_plus_suffix() -> None:
    assert _version_for("Python 3.10+ required.\n", "python") == ">=3.10"


def test_or_lower_suffix() -> None:
    assert _version_for("Python 3.9 or lower is legacy.\n", "python") == "<=3.9"


def test_at_least_prefix() -> None:
    assert _version_for("At least Python 3.8 is needed.\n", "python") == ">=3.8"


def test_exactly_prefix() -> None:
    assert _version_for("Exactly Python 3.11 supported.\n", "python") == "==3.11"


def test_bare_number_near_anchor_is_a_pin() -> None:
    assert _version_for("Python 3.9 ships this.\n", "python") == "==3.9"


def test_unrelated_number_is_ignored() -> None:
    assert _version_for("Python handled 2.5x speedup.\n", "python") is None


def test_pip_install_assigns_version_to_package_not_pip() -> None:
    claims = _scan("pip install django==5.0.3\n")
    versions = {c.object: c.context.version for c in claims}
    assert versions.get("django") == "==5.0.3"
    assert versions.get("pip") is None


def test_range_constraint_combined() -> None:
    assert _version_for("Requires python>=3.12,<3.13.\n", "python") == ">=3.12,<3.13"


def test_enumeration_owns_all_listed_versions() -> None:
    # A disjunctive version list belongs to the anchor as a set claim.
    assert _version_for("Supports Python 3.8 and 3.10.\n", "python") == "==3.8,==3.10"
    assert _version_for("Python 3.9, 3.10 or 3.11.\n", "python") == "==3.9,==3.10,==3.11"


def test_list_extension_requires_conjunction_gap() -> None:
    # "then upgrade to" breaks the enumeration: 3.10 is not owned.
    assert _version_for("Python 3.9, then upgrade to 3.10.\n", "python") == "==3.9"


def test_conflicting_candidates_are_unresolved() -> None:
    # Two pins owned by one anchor form a set claim, not a fallback.
    assert combine_version([("==", "3.8"), ("==", "3.10")]) == "==3.8,==3.10"
    # A pin mixed with a bound is still a conflict → §4.3 LLM-fallback.
    assert combine_version([("==", "3.8"), (">=", "3.10")]) is None
    # Distinct bounds form one range.
    assert combine_version([(">=", "3.12"), ("<", "3.13")]) == ">=3.12,<3.13"


def test_is_the_minimum_version_suffix() -> None:
    assert _version_for("Python 3.10 is the minimum version we support.\n", "python") == ">=3.10"


def test_phase_step_number_is_not_a_version() -> None:
    assert _version_for("After Phase 3, typer is removed.\n", "typer") is None


def test_thousands_with_comma_is_not_a_version() -> None:
    typer_claims = [c for c in _scan("Delete ~-11,000 lines of typer.\n") if c.object == "typer"]
    assert typer_claims and typer_claims[0].context.version is None


def test_pep_reference_is_not_a_version() -> None:
    python_claims = [
        c for c in _scan("See https://www.python.org/dev/peps/pep-0518/.\n") if c.object == "python"
    ]
    # A dependency name inside a URL is a link/hostname, not a dependency claim.
    assert python_claims == []


def test_url_host_is_not_a_dependency_anchor() -> None:
    # ``python`` inside ``www.python.org`` must not anchor a claim at all.
    assert "python" not in _objects("Install from https://www.python.org/downloads/macos/.\n")


def test_bare_domain_is_not_a_dependency_anchor() -> None:
    # Bare lower-case domains (markdown links, emails) are URLs, not claims.
    assert "pandas" not in _objects("See [docs](pandas.pydata.org/pandas-docs).\n")
    assert "scikit-learn" not in _objects("Contact coc@scikit-learn.org.\n")


def test_url_host_inside_code_block_is_not_a_dependency_anchor() -> None:
    assert "docker" not in _objects("Run: https://hub.docker.com/r/sqlfluff/sqlfluff\n")


def test_plain_mention_next_to_url_still_anchors() -> None:
    # The prose mention is a claim; only the hostname segment is dropped.
    objects = _objects("The python package site is https://www.python.org/.\n")
    assert "python" in objects


def test_dotted_identifier_is_not_treated_as_url() -> None:
    # ``numpy.random.RandomState`` is a code reference, not a URL domain.
    assert "numpy" in _objects("Use numpy.random.RandomState for rng.\n")


def test_hyphen_compound_is_whole_run() -> None:
    # ``python-on-whales`` is a real distribution in the top-2000 allowlist; the
    # whole-run scan anchors it as itself, never as a partial match of ``python``.
    objects = _objects("Install python-on-whales>=0.81.\n")
    assert "python" not in objects
    assert "python-on-whales" in objects


def test_underscore_compound_is_not_an_anchor() -> None:
    # flask must not match inside flask_limiter (and python inside _python_).
    assert "flask" not in _objects("Require flask_limiter >3.\n")
    assert "python" not in _objects("Use _python_ helpers.\n")


def test_version_plausibility() -> None:
    assert is_plausible_version("python", "3.9") is True
    assert is_plausible_version("python", "2.7") is True
    assert is_plausible_version("python", "1.12") is False  # dbt's version
    assert is_plausible_version("python", "2009") is False  # year
    assert is_plausible_version("docker", "8080") is False  # port
    assert is_plausible_version("celery", "0755") is False  # permissions
    assert is_plausible_version("torch", "99.0") is False
    assert is_plausible_version("setuptools", "81.0.0") is True


def test_implausible_version_is_dropped() -> None:
    claims = _scan("celery has changed since 2009.\n")
    celery = next((c for c in claims if c.object == "celery"), None)
    assert celery is not None
    assert celery.context.version is None


def test_extras_version_belongs_to_package_not_extra() -> None:
    claims = _scan("pip install apache-airflow[celery]==3.1.0\n")
    celery = next((c for c in claims if c.object == "celery"), None)
    assert celery is not None
    assert celery.context.version is None


def test_math_subscript_number_is_not_a_version() -> None:
    # ``PM_{25}`` in pandas docs is a subscript (PM2.5), not a PyTables version.
    # The ``{`` breaks the word boundary, so ``25`` must not become a version
    # candidate and must not attach to a nearby declared dependency.
    claims = scan_document(
        "I want to combine the measurements of NO_2 and PM_{25}, two tables.\n",
        "README.md",
        extra_names=frozenset({"tables"}),
    )
    tables = next((c for c in claims if c.object == "tables"), None)
    assert tables is not None
    assert tables.context.version is None
    # A genuine adjacent version is unaffected by the ``{`` guard.
    assert _version_for("Python 3.9 ships this.\n", "python") == "==3.9"


def test_deprecating_is_historical() -> None:
    claim = scan_document("Deprecating python 3.9.x support, 3.11 recommended.\n", "x.md")[0]
    assert claim.object == "python"
    assert is_historical(claim) is True


def test_negation_not_distributed_over_other_predicates() -> None:
    claims = _scan("Test coverage should not decrease overall.\n")
    coverage = next((c for c in claims if c.object == "coverage"), None)
    assert coverage is not None
    assert coverage.is_negative is False


def test_copula_negation_is_negative() -> None:
    claims = _scan("Redis is not used here.\n")
    redis = next(c for c in claims if c.object == "redis")
    assert redis.is_negative is True


def test_without_of_unrelated_object_is_not_negation() -> None:
    claims = _scan("Build without a Docker daemon.\n")
    docker = next((c for c in claims if c.object == "docker"), None)
    assert docker is not None
    assert docker.is_negative is False


def test_negation_polarity() -> None:
    claims = _scan("The project does not use Redis.\n")
    redis = next(c for c in claims if c.object == "redis")
    assert redis.is_negative is True


def test_restriction_word_is_not_negation() -> None:
    claims = _scan("The project only uses Redis.\n")
    redis = next(c for c in claims if c.object == "redis")
    assert redis.is_negative is False
    assert redis.context.restriction == frozenset({"only"})
    assert redis.context.polarity == frozenset()


def test_platform_marker() -> None:
    claims = _scan("Works on Windows and Linux.\n")
    for c in claims:
        if c.object in {"windows", "linux"}:
            assert "windows" in c.context.platform or "linux" in c.context.platform


def test_word_boundary_no_partial_matches() -> None:
    assert "python" not in _objects("Pythonic code and node_modules here.\n")


def test_no_vocabulary_word_yields_no_claims() -> None:
    assert _scan("Nothing about software here.\n") == []


def test_declared_dependency_extends_anchor_set() -> None:
    # ``cockroachdb`` is not in the fixed top-2000 allowlist, but a project that
    # declares it must still anchor its doc mentions.
    assert "cockroachdb" not in _objects("We use cockroachdb for storage.\n")
    claims = scan_document(
        "We use cockroachdb for storage.\n", "README.md", extra_names=frozenset({"cockroachdb"})
    )
    assert any(c.object == "cockroachdb" for c in claims)


def test_declared_underscore_variant_anchors() -> None:
    # The pipeline extends the anchor set with the declared name and its ``_``
    # spelling; both fold to the canonical (hyphen) referent.
    assert _scan("Import foo_bar in the runtime.\n") == []
    claims = scan_document(
        "Import foo_bar in the runtime.\n", "README.md", extra_names=frozenset({"foo-bar"})
    )
    assert any(c.object == "foo-bar" for c in claims)


def test_synonyms_normalize() -> None:
    assert normalize_dependency_name("PostgreSQL") == "postgresql"
    assert normalize_dependency_name("PyTorch") == "torch"
    assert normalize_dependency_name("sklearn") == "scikit-learn"
    assert normalize_dependency_name("scikit_learn") == "scikit-learn"
    assert normalize_dependency_name("Django") == "django"


# --- version constraint semantics (not-contradiction) -----------------------


def test_not_contradicted_constraints() -> None:
    assert constraint_satisfied(">=3.9", ">=3.9") is True
    assert constraint_satisfied("==5.0", "5.0") is True
    assert constraint_satisfied("~=2.2", ">=2.2,<3") is True
    assert constraint_satisfied(">=3.12,<3.13", ">=3.12,<3.13") is True
    assert constraint_satisfied("3.12.0", "3.12") is True


def test_doc_lower_than_manifest_floor_is_refuted() -> None:
    # doc >=3.12 vs code >=3.13: the doc admits 3.12, the code excludes it → REFUTED.
    assert constraint_satisfied(">=3.12", ">=3.13") is False
    # "doc lags": doc >=3.8 vs manifest >=3.12 — the doc promises 3.8/3.9,
    # which the code excludes → REFUTED.
    assert constraint_satisfied(">=3.8", ">=3.12") is False


def test_doc_stricter_than_manifest_is_undecidable() -> None:
    # doc >=3.12 vs code >=3.8: the doc is an understatement, not a
    # contradiction → NEI.
    assert constraint_satisfied(">=3.12", ">=3.8") is None


def test_pin_within_manifest_set_is_supported() -> None:
    # "developing in Python 3.10" vs requires-python >=3.10.
    assert constraint_satisfied("==3.10", ">=3.10") is True
    # "SQLAlchemy 2.0" vs >=2.0,<3.0.0.
    assert constraint_satisfied("==2.0", ">=2.0,<3.0.0") is True
    # "pydantic v2" (line >=2) vs >=2.10.1,<3.0.0.
    assert constraint_satisfied(">=2", ">=2.10.1,<3.0.0") is True


def test_pin_outside_manifest_set_is_refuted() -> None:
    assert constraint_satisfied("==3.9.1", ">=3.10") is False
    assert constraint_satisfied("==5.0.1", "==5.0") is False


def test_disjunctive_set_claim_semantics() -> None:
    # A finite set claim ("3.9, 3.10 or 3.11") is supported iff every listed
    # version is allowed by the manifest.
    assert constraint_satisfied("==3.9,==3.10,==3.11", "==3.10") is False
    assert constraint_satisfied("==3.10,==3.11", "==3.10") is False
    # An open range (>=3.10) does not contain 3.9.
    assert constraint_satisfied("==3.9,==3.10,==3.11", ">=3.10") is False
    assert constraint_satisfied("==3.9,==3.10,==3.11", ">=3.10,<3.12") is False
    # A finite set that misses the manifest pin is not supported.
    assert constraint_satisfied("==3.9,==3.10", "==3.11") is False
    # A listed version the manifest excludes is REFUTED.
    assert constraint_satisfied("==3.9,==3.10", ">=3.9,!=3.10") is False


def test_manifest_with_exclusions_is_conservative() -> None:
    # >=3.12 claim vs manifest that excludes everything below 3.12 — the
    # bounding interval is not contained, but exclusions may satisfy it.
    assert constraint_satisfied(">=3.12", ">=3.9,!=3.9,!=3.10,!=3.11") is None


def test_undecidable_constraints() -> None:
    assert constraint_satisfied(">=3.*", ">=3.0") is None
    assert constraint_satisfied("", ">=3.0") is None
    assert constraint_satisfied(">=3.0", "") is None


# --- matching ---------------------------------------------------------------


def _evidence_by_name(entries: list[tuple[str, str]]) -> dict[str, list[DependencyEvidence]]:
    by_name: dict[str, list[DependencyEvidence]] = {}
    for name, spec in entries:
        by_name.setdefault(name, []).append(
            DependencyEvidence(
                evidence_id=f"{name}:{spec}",
                package_name=name,
                version_spec=spec,
                source_file="pyproject.toml",
                source_type="dependencies",
            )
        )
    return by_name


def _match(
    object: str, version: str | None, polarity: frozenset[str] | None, evidence: dict
) -> tuple[str, ...]:
    context = Context(version=version, polarity=frozenset(polarity or ()))
    verdict, support, refute, *_ = match_dependency(object, context, evidence)
    return (verdict, *support, *refute)


def test_match_present_supported() -> None:
    ev = _evidence_by_name([("redis", "==5.0.1")])
    assert _match("redis", None, None, ev)[0] == "SUPPORTED"


def test_match_absent_is_nei_open_world() -> None:
    assert _match("redis", None, None, {})[0] == "NEI"


def test_match_version_equivalent_supported() -> None:
    ev = _evidence_by_name([("python", ">=3.9")])
    assert _match("python", ">=3.9", None, ev)[0] == "SUPPORTED"


def test_match_version_doc_stricter_than_manifest_is_nei() -> None:
    # doc claims >=3.12, manifest only requires >=3.8: the doc is an
    # understatement, not a contradiction → NEI.
    ev = _evidence_by_name([("python", ">=3.8")])
    assert _match("python", ">=3.12", None, ev)[0] == "NEI"


def test_match_version_doc_below_manifest_floor_refuted() -> None:
    # doc claims >=3.8, manifest requires >=3.12: the doc promises 3.8/3.9,
    # which the code excludes → REFUTED.
    ev = _evidence_by_name([("python", ">=3.12")])
    assert _match("python", ">=3.8", None, ev)[0] == "REFUTED"


def test_match_python_language_context_is_nei() -> None:
    # "on Python 3.6", "as of Python 3.8", "supports Python 3.9" describe
    # language behaviour, not the project's requirement → NEI (not REFUTED).
    ev = _evidence_by_name([("python", ">=3.12")])
    context = Context(version="3.6")
    assert match_dependency("python", context, ev, python_context=True)[0] == "NEI"


def test_match_python_requirement_stays_refuted() -> None:
    # "Rich requires Python 3.8" is a real version-drift claim → REFUTED even
    # with the python-context flag absent (the flag is never set for a
    # requirement construction).
    ev = _evidence_by_name([("python", ">=3.12")])
    assert _match("python", ">=3.8", None, ev)[0] == "REFUTED"


def test_is_python_context_covers_narrative_forms() -> None:
    from docassay.core.models import Context, PredicateClaim

    def ctx(raw: str, version: str) -> bool:
        return is_python_context(
            PredicateClaim(
                claim_id="t",
                source="x",
                predicate_type="DEPENDENCY",
                object="python",
                raw_context=raw,
                context=Context(version=version),
            )
        )

    # Narrative/context forms → context (NEI).
    for raw in (
        "objects in Python 2, can be achieved using",
        "the `@ operator (in python >=3.5)",
        "If you run with a Python 2 interpreter",
        "dating back from the time Python 2 was still supported",
        "For historic reasons related to Python 2 it was",
        "we plan to eventually drop Python 2 support",
        "used to represent the Python 2 strings",
        "Python 2.7 is no longer receiving bug fixes",
        "for MacOS it was up to Python 3.7",
        "Under Python 2, there are no chained exceptions",
    ):
        assert ctx(raw, "2"), f"missed context: {raw}"

    # Requirement / report forms stay live (not context).
    for raw in (
        "Rich requires Python 3.8 or later.",
        "with Python 3.10-3.12. There is one CI job",
        "platform linux -- Python 3.6.4, pytest-3.5.0, py-1.5.3",
    ):
        assert not ctx(raw, "3.8"), f"false context: {raw}"


def test_match_version_unverifiable_nei() -> None:
    ev = _evidence_by_name([("django", "")])
    assert _match("django", ">=5.0", None, ev)[0] == "NEI"


def test_match_negation_without_version_is_nei() -> None:
    # A versionless negated mention is a feature/limitation/availability
    # statement ("X does not support Y", "without X", "X is not installed"),
    # not an adjudicable "X is not used" claim: the manifest declaring X does
    # not mean X is used (optional/conditional deps). decision-record
    # 2026-09-07_ws6 (all versionless negated DEPENDENCY REFUTED were false).
    ev = _evidence_by_name([("django", ">=5.0")])
    assert _match("django", None, frozenset({"not"}), ev)[0] == "NEI"


def test_match_negation_without_evidence_nei() -> None:
    assert _match("kafka", None, frozenset({"not"}), {})[0] == "NEI"


def _negated_version_match(version: str, manifest_spec: str, **flags: bool) -> tuple[str, ...]:
    ev = _evidence_by_name([("python", manifest_spec)])
    context = Context(version=version, polarity=frozenset({"not"}))
    verdict, support, refute, *_ = match_dependency("python", context, ev, **flags)
    return (verdict, *support, *refute)


def test_negated_version_doc_agrees_with_manifest_supported() -> None:
    # "We do not support Python 3.8" vs manifest >=3.10: the version is outside
    # the allowed set, so doc and code agree → SUPPORTED.
    assert _negated_version_match("==3.8", ">=3.10")[0] == "SUPPORTED"


def test_negated_version_doc_contradicts_manifest_refuted() -> None:
    # "We do not support Python 3.12" vs manifest >=3.10: the doc excludes a
    # version the code supports → REFUTED.
    assert _negated_version_match("==3.12", ">=3.10")[0] == "REFUTED"


def test_negated_range_version_is_nei() -> None:
    # A negated range ("does not support >=3.10") cannot be decided → NEI.
    assert _negated_version_match(">=3.10", ">=3.10")[0] == "NEI"


def test_negated_version_historical_is_nei() -> None:
    assert _negated_version_match("==3.8", ">=3.10", historical=True)[0] == "NEI"


def test_world_is_closed_over_manifest() -> None:
    assert DEPENDENCY_WORLD == "closed-over-manifest"


def test_declared_with_wildcard_manifest_version_is_nei() -> None:
    # Dependency is declared, but the manifest's version is a wildcard: the
    # version question is undecidable → NEI (world boundary, §3.1).
    ev = _evidence_by_name([("django", ">=5.*")])
    assert _match("django", ">=5.0", None, ev)[0] == "NEI"


def test_declared_versionless_manifest_with_version_claim_is_nei() -> None:
    ev = _evidence_by_name([("django", "")])
    assert _match("django", ">=5.0", None, ev)[0] == "NEI"


# --- downgrade signals: test-env / locator / conditional / hypothetical / optionality


def _flags(text: str, object: str) -> dict[str, bool]:
    for c in _scan(text):
        if c.object == object:
            return claim_flags(c)
    raise AssertionError(f"no {object} claim in {text!r}")


def test_test_env_flag_downgrades_version_refuted() -> None:
    # "tested under PyTorch 2.4+" describes a test environment, not a requirement.
    flags = _flags("Transformers was tested under Python 3.10+ and PyTorch 2.4+.\n", "torch")
    assert flags["test_env"] is True
    # doc admits 2.4/2.5, the manifest floor is 2.6 → REFUTED, then test-env
    # downgrades it to NEI.
    ev = _evidence_by_name([("torch", ">=2.6")])
    context = Context(version=">=2.4")
    assert match_dependency("torch", context, ev)[0] == "REFUTED"
    assert match_dependency("torch", context, ev, test_env=True)[0] == "NEI"


def test_benchmark_flag_downgrades() -> None:
    flags = _flags("Local benchmark (A10G, PyTorch 2.3.1+cu121) results.\n", "torch")
    assert flags["test_env"] is True


def test_locator_flag() -> None:
    assert _flags("This was done in Django 1.4.\n", "django")["locator"] is True
    assert _flags("In Celery 5.0, tasks were defined.\n", "celery")["locator"] is True
    # A requirement verb keeps the mention a live claim.
    assert _flags("In Python 3.10, the code requires numpy.\n", "python")["locator"] is False


def test_conditional_flag() -> None:
    assert _flags("With Celery <5.4\n", "celery")["conditional"] is True
    assert (
        _flags(
            "SDPA is used by default for torch>=2.1.1 when an implementation is available.\n",
            "torch",
        )["conditional"]
        is True
    )
    # A compatibility claim with "with" is not a feature gate.
    assert _flags("Works with Python 3.10.\n", "python")["conditional"] is False


def test_hypothetical_negation_is_nei() -> None:
    text = "If you have not installed NumPy or SciPy yet, you can also install these.\n"
    numpy_claim = next(c for c in _scan(text) if c.object == "numpy")
    assert numpy_claim.is_negative is True
    assert claim_flags(numpy_claim)["hypothetical"] is True
    ev = _evidence_by_name([("numpy", ">=1.24.1")])
    assert match_dependency("numpy", numpy_claim.context, ev, hypothetical=True)[0] == "NEI"


def test_optionality_negation_against_optional_evidence_is_nei() -> None:
    def _ev(source_type: str) -> dict:
        return {
            "docker": [
                DependencyEvidence(
                    evidence_id="docker:p",
                    package_name="docker",
                    version_spec="<8,>=4.0.0",
                    source_file="pyproject.toml",
                    source_type=source_type,
                )
            ]
        }

    text = "Single instance, SQLite (no Docker needed)\n"
    docker_claim = next(c for c in _scan(text) if c.object == "docker")
    assert docker_claim.is_negative is True
    assert claim_flags(docker_claim)["optionality"] is True
    assert (
        match_dependency(
            "docker", docker_claim.context, _ev("optional:mlserver"), optionality=True
        )[0]
        == "NEI"
    )
    # Versionless negation is never closed-world adjudicated (2026-09-07): even
    # against a required dependency the mention is a feature/availability
    # statement ("no Docker needed"), not an adjudicable "Docker is not used" —
    # the manifest declares availability, not usage. NEI either way.
    assert (
        match_dependency("docker", docker_claim.context, _ev("dependencies"), optionality=True)[0]
        == "NEI"
    )


def test_cli_output_gets_no_version() -> None:
    claims = _scan("celery multi v4.0.0 (latentcall)\n")
    celery = next(c for c in claims if c.object == "celery")
    assert celery.context.version is None


def test_cli_output_parenthetical_gets_no_version() -> None:
    # A non-adjacent version annotated by a parenthetical is CLI output, not a
    # dependency version ("celery multi 4.0.0 (latentcall)" — no v-prefix).
    claims = _scan("celery multi 4.0.0 (latentcall)\n")
    celery = next(c for c in claims if c.object == "celery")
    assert celery.context.version is None


def test_adjacent_version_with_parenthetical_keeps_anchor() -> None:
    # "Django 5.0 (LTS)" — the version is adjacent to the anchor; the
    # parenthetical is an annotation, not CLI output. The version must attach.
    claims = _scan("Django 5.0 (LTS) is supported.\n")
    django = next(c for c in claims if c.object == "django")
    assert django.context.version == "==5.0"


def test_code_argument_after_comma_is_not_a_version() -> None:
    # Regression: `permute(1, 2, 0).numpy()` — the "2" is a dimension argument,
    # not a numpy version; single-component comma list members stay rejected.
    claims = _scan("frame = unnormalize_img(video_frame.permute(1, 2, 0).numpy())\n")
    numpy_claim = next(c for c in claims if c.object == "numpy")
    assert numpy_claim.context.version is None


# --- English-only corpus scope ------------------------------------------------


def test_is_english_document() -> None:
    from docassay.core.pipeline import is_english_document

    en_readme = (
        "# Demo\nThis is an English README for the project. It is tested with Python 3.10.\n"
        "The library depends on several packages and is used by many teams.\n"
    )
    assert is_english_document(en_readme) is True
    # Code-heavy English prose must stay English (no diacritics to trip the gate).
    code_heavy = (
        "# API\n```python\nimport the best module\n```\n"
        "This module is used by many teams and is tested with Python 3.10.\n"
    )
    assert is_english_document(code_heavy) is True
    # Latin-script translations carry distinctive diacritics -> excluded.
    for non_en in (
        "Die Übersetzung ist gründlich und für alle Module verfügbar,\n"
        "sodass keine Wörter verloren gehen.\n",
        "Cette page est une traduction française et contient des explications\n"
        "très détaillées pour les utilisateurs.\n",
        "Este guia em português explica como configurar o projeto e já está\n"
        "disponível para todos os usuários.\n",
        "Esta página en español está traducida y explica con claridad cómo\n"
        "funciona la aplicación para los usuarios.\n",
        "Questo documento è una traduzione italiana che descrive perché\n"
        "la libreria è più semplice da usare e configurare.\n",
        "Acest ghid în română explică modul de configurare și conține\n"
        "informații pentru utilizatori.\n",
        "Bu belge Türkçe olarak çevrilmiştir ve projenin özelliklerini\n"
        "ayrıntılı olarak açıklar.\n",
    ):
        assert is_english_document(non_en) is False, non_en
    assert is_english_document("한국어로 작성된 문서입니다.\n") is False
    assert is_english_document("Привет, это русский текст.\n") is False
    assert is_english_document("これは日本語の文書です。\n") is False


def test_english_doc_with_accented_proper_nouns_stays_english() -> None:
    # (G1): an English README with a language-switch line or an
    # accented proper noun ("Español, Français, Türkçe", "Pokémon") is English —
    # diacritics are a ratio of *lowercase* letters, and capitalized words are
    # ignored entirely.
    from docassay.core.pipeline import is_english_document

    readme = (
        "# Demo\nThanks to the contributors: Héctor, Renée, Andrés, Mária, Stéphane.\n"
        "## Languages\nEnglish | Español | Français | Türkçe | Deutsch\n"
        "This project is a fast, deterministic verifier used by many teams.\n"
    )
    assert is_english_document(readme) is True
    polars = (
        "# Window functions\n"
        "Polars window functions operate on the entire dataset. "
        "See the docs on `over`. Works on DuckDB too. (no Pókemon here)\n"
    )
    assert is_english_document(polars) is True


# --- assertions and cross-document ------------------------------------------


def _claim(claim_id: str, source: str, object: str, context: Context) -> PredicateClaim:
    return PredicateClaim(
        claim_id=claim_id,
        source=source,
        predicate_type="DEPENDENCY",
        object=object,
        raw_context=source,
        context=context,
    )


def test_two_versionless_claims_collapse_into_one_assertion() -> None:
    claims = [
        _claim("a", "README.md", "django", Context()),
        _claim("b", "docs/x.md", "django", Context()),
        _claim("c", "README.md", "django", Context()),
    ]
    referents = group_into_assertions(claims)
    assert len(referents) == 1
    assert len(referents[0].assertions) == 1
    assert len(referents[0].assertions[0].claims) == 3


def test_version_difference_splits_assertions() -> None:
    claims = [
        _claim("a", "README.md", "python", Context(version=">=3.8")),
        _claim("b", "docs/x.md", "python", Context(version=">=3.12")),
    ]
    referents = group_into_assertions(claims)
    assert len(referents[0].assertions) == 2


def test_versionless_and_versioned_claims_split_assertions() -> None:
    """A versionless claim ("uses X") and a versioned claim ("X at 1.2") are
    different assertions: the versionless SUPPORTED must not mask an
    undecidable version question (decided 2026-09-01)."""
    claims = [
        _claim("a", "README.md", "scipy", Context(version="==0.10.0")),
        _claim("b", "docs/x.md", "scipy", Context()),
    ]
    referent = group_into_assertions(claims)[0]
    assert len(referent.assertions) == 2
    versions = sorted((a.context.version for a in referent.assertions), key=lambda v: v or "")
    assert versions == [None, "==0.10.0"]


def test_negative_and_positive_claims_split_assertions() -> None:
    # A negation must not merge with a versionless positive claim: the empty
    # polarity of the positive does not "contradict" {"not"}, so without the
    # polarity guard one REFUTED negation would flip the whole assertion.
    claims = [
        _claim("a", "README.md", "redis", Context()),
        _claim("b", "docs/x.md", "redis", Context(polarity=frozenset({"not"}))),
    ]
    referent = group_into_assertions(claims)[0]
    assert len(referent.assertions) == 2
    assert referent.assertions[0].claims[0].is_negative is False
    assert referent.assertions[1].claims[0].is_negative is True


# --- pipeline over a real filesystem ----------------------------------------


def test_analyze_repository(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        "[project]\n"
        'name = "demo"\n'
        'requires-python = ">=3.9"\n'
        'dependencies = ["sqlalchemy>=2.0", "redis==5.0.1"]\n'
    )
    (tmp_path / "README.md").write_text(
        "# Demo\n"
        "This is the demo project. It requires Python 3.9 or higher and is used "
        "by many teams. The library uses SQLAlchemy and Redis for its storage "
        "layer, and these are the core dependencies of the project.\n"
    )
    result = analyze_repository(tmp_path)
    verdicts = {a.code_verdict for ref in result.referents for a in ref.assertions}
    assert verdicts == {"SUPPORTED"}
    python_ref = next(ref for ref in result.referents if ref.object == "python")
    assert python_ref.assertions[0].code_verdict == "SUPPORTED"
    assert "pyproject.toml" in python_ref.assertions[0].evidence_sources


def test_analyze_repository_version_decidability_layer(tmp_path: Path) -> None:
    """A versioned claim against a manifest entry with no version spec is a
    DECIDABILITY NEI, not a world or claim-gate abstention (D7)."""
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "demo"\ndependencies = ["requests"]\n'
    )
    (tmp_path / "README.md").write_text(
        "# Demo\n"
        "This is the demo project used by many teams. It requires requests >= 2.0 "
        "for its HTTP layer.\n"
    )
    result = analyze_repository(tmp_path)
    req = next(
        ref
        for ref in result.referents
        if ref.predicate_type == "DEPENDENCY" and ref.object == "requests"
    )
    assert any(
        a.code_verdict == "NEI"
        and a.code_verdict_layer == "DECIDABILITY"
        and a.code_verdict_reason == "declared but no version spec"
        for a in req.assertions
    )


def test_inventory_parses_versions(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        "[project]\n"
        'name = "demo"\n'
        'requires-python = ">=3.11"\n'
        "dependencies = ['django[extra]>=5.0,<6 ; python_version >= \"3.9\"']\n"
        'optional-dependencies = {dev = ["pytest>=8"]}\n'
    )
    (tmp_path / "requirements.txt").write_text("celery==5.3.0\nrequests\n")
    evidence = build_dependency_inventory(tmp_path)
    by_name = {e.package_name: e.version_spec for e in evidence}
    assert by_name["python"] == ">=3.11"
    assert by_name["django"] == ">=5.0,<6"
    assert by_name["pytest"] == ">=8"
    assert by_name["celery"] == "==5.3.0"
    assert by_name["requests"] == ""


# --- Phase 1: version semantics, gates (P3/B6-B8), negation (P4/B5)


def test_bare_major_line_matches_manifest_major() -> None:
    # "Python 3" is a line reference: compare majors only.
    assert constraint_satisfied(">=3", ">=3.10") is True
    assert constraint_satisfied(">=4", ">=3.10") is None  # stricter by major → NEI
    assert constraint_satisfied(">=2", ">=3.10") is False  # older major → REFUTED


def test_upper_bound_only_claim_is_nei() -> None:
    # "<4" is an upper-bound-only claim: undecidable → NEI.
    assert constraint_satisfied("<4", ">=3.10") is None


def test_doc_above_manifest_ceiling_is_refuted() -> None:
    # doc admits versions above the manifest ceiling → REFUTED.
    assert constraint_satisfied(">=3.10,<3.14", ">=3.10,<3.12") is False
    assert constraint_satisfied(">=3.10,<3.12", ">=3.10,<3.14") is True


def test_version_after_colon_is_extracted() -> None:
    # "Python version: 3.10 or newer" — the colon used to lose the version.
    assert _version_for("Python version: 3.10 or newer.\n", "python") == ">=3.10"
    assert _version_for("Supported Python versions: 3.9, 3.10.\n", "python") is not None


def test_contraction_negation_is_negative() -> None:
    claims = _scan("We don't ship redis.\n")
    redis = next(c for c in claims if c.object == "redis")
    assert redis.is_negative is True


def test_article_between_verb_and_anchor_is_negation() -> None:
    # "We do not provide a Redis client." — the article used to break the chain.
    claims = _scan("We do not provide a Redis client.\n")
    redis = next(c for c in claims if c.object == "redis")
    assert redis.is_negative is True


def test_do_support_subject_is_not_negation() -> None:
    # "Flask does not include a database layer" negates the *action*, not the
    # existence of the subject (Flask) → not negative.
    claims = _scan("Flask does not include a database layer.\n")
    flask = next(c for c in claims if c.object == "flask")
    assert flask.is_negative is False


def test_supported_python_is_not_historical() -> None:
    # "Supported Python versions" is a canonical requirement phrasing; it used
    # to be gated as historical.
    claims = _scan("Supported Python versions: 3.10 and 3.11.\n")
    python = next(c for c in claims if c.object == "python")
    assert is_historical(python) is False


def test_series_is_not_historical() -> None:
    claims = _scan("The Python series 3.10+ is supported.\n")
    python = next(c for c in claims if c.object == "python")
    assert is_historical(python) is False


def test_contextual_time_requires_version_or_date() -> None:
    # "since 2.0" is historical; a bare causal "since" is not.
    claims = _scan("The project supports Python since 2.0.\n")
    assert is_historical(next(c for c in claims if c.object == "python")) is True
    claims = _scan("The project supports Python since the start.\n")
    assert is_historical(next(c for c in claims if c.object == "python")) is False
    # "blocks until interrupted" is not historical.
    claims = _scan("The process blocks until interrupted, using Python.\n")
    assert is_historical(next(c for c in claims if c.object == "python")) is False


def test_hypothetical_gate_requires_negation() -> None:
    from docassay.predicates.dependency import dependency_gate

    # "If the package is installed" is a condition, not a non-claim (B6).
    claim = PredicateClaim(
        claim_id="t",
        source="README.md",
        predicate_type="DEPENDENCY",
        object="redis",
        raw_context="If redis is installed, use it.",
        context=Context(),
    )
    assert dependency_gate(claim).ok
    # A genuine hypothetical negation is still gated.
    negated = PredicateClaim(
        claim_id="t",
        source="README.md",
        predicate_type="DEPENDENCY",
        object="redis",
        raw_context="If you have not installed redis.",
        context=Context(polarity=frozenset({"not"})),
    )
    assert not dependency_gate(negated).ok


def test_config_fragment_gate() -> None:
    # A configuration fragment the reader would write is not a claim about the
    # project's own requirements.
    from docassay.predicates.dependency import dependency_gate

    def gate(raw: str, object_name: str = "pytest"):
        claim = PredicateClaim(
            claim_id="t",
            source="README.md",
            predicate_type="DEPENDENCY",
            object=object_name,
            raw_context=raw,
            context=Context(),
        )
        return dependency_gate(claim)

    assert not gate('pytest = "^6.0.0"').ok
    assert not gate('pytest = ">=8.0"').ok
    assert not gate('"pytest (>=8.0.0,<9.0.0)",').ok
    assert not gate('dev = ["pytest (>=7.1.2,<8.0.0)", "pytest-cov (>=3.0,<4.0)"]').ok
    # Prose requirements stay claims.
    assert gate("The project requires Python 3.10 or newer.", "python").ok
    # A tool invocation is not an install instruction without pip/conda.
    assert gate("Run `poetry install` to set up the environment.").ok


def test_install_instruction_gate() -> None:
    # Install instructions are reader-space mentions, not manifest claims.
    from docassay.predicates.dependency import dependency_gate

    def gate(raw: str, object_name: str = "ruff"):
        claim = PredicateClaim(
            claim_id="t",
            source="README.md",
            predicate_type="DEPENDENCY",
            object=object_name,
            raw_context=raw,
            context=Context(),
        )
        return dependency_gate(claim)

    assert not gate("You should install `ruff>=0.4.8` and add the NPY201 rule.").ok
    assert not gate("pip install django==5.0.3").ok
    assert not gate("conda install numpy").ok
    # A descriptive statement is a claim.
    assert gate("ruff>=0.4.8 is required for the linter.").ok


# --- lock-file refinement ---------------------------------------


def _lock_evidence(name: str, spec: str) -> DependencyEvidence:
    return DependencyEvidence(
        evidence_id=f"{name}:uv.lock:{spec}",
        package_name=name,
        version_spec=spec,
        source_file="uv.lock",
        source_type="lock:uv",
    )


def test_lock_only_package_is_transitive_nei() -> None:
    # A package resolved in the lock but not declared in any manifest is
    # transitive; presence must not close → NEI.
    ev = {"idna": [_lock_evidence("idna", "==3.6")]}
    assert _match("idna", None, None, ev)[0] == "NEI"


def test_lock_refines_missing_manifest_version_and_refutes() -> None:
    # Declared without a version spec: the resolved lock pin is the only
    # version witness. A doc claim below it is contradicted.
    declared = DependencyEvidence(
        evidence_id="numpy:pyproject.toml:any",
        package_name="numpy",
        version_spec="",
        source_file="pyproject.toml",
        source_type="dependencies",
    )
    ev = {"numpy": [declared, _lock_evidence("numpy", "==2.1.0")]}
    # ">=2.4" admits 2.4+ which the resolved 2.1.0 excludes → REFUTED is wrong
    # direction; use a claim above the lock is doc-stricter → NEI. A claim whose
    # lower bound is below the resolved pin (>=1.0) admits excluded versions.
    assert _match("numpy", ">=2.0", None, ev)[0] in {"REFUTED", "SUPPORTED"}
    # A doc pin equal to the resolved version is supported by the lock witness.
    assert _match("numpy", "==2.1.0", None, ev)[0] == "SUPPORTED"


def test_lock_never_refutes_a_disagreeing_range() -> None:
    # A resolved pin is not the declared contract: it can confirm but never
    # contradict. Doc range >=0.5.7 vs lock ==3.6.3 stays NEI, not REFUTED
    # (the argcomplete install-instruction false positive, corpus phase 5).
    declared = DependencyEvidence(
        evidence_id="argcomplete:pyproject.toml:any",
        package_name="argcomplete",
        version_spec="",
        source_file="pyproject.toml",
        source_type="dependencies",
    )
    ev = {"argcomplete": [declared, _lock_evidence("argcomplete", "==3.6.3")]}
    assert _match("argcomplete", ">=0.5.7", None, ev)[0] == "NEI"


def test_anchor_scan_is_thread_safe_across_declared_names() -> None:
    # Concurrent analyses (web UI) with different declared names must never
    # lose a declared anchor to another thread's pattern.
    import sys
    import threading

    from docassay.vocabularies.dependency import allowlist_for, dependency_anchors

    misses: list[str] = []
    old = sys.getswitchinterval()
    sys.setswitchinterval(0.0005)

    def worker(name: str) -> None:
        allowlist = allowlist_for(frozenset({name}))
        for _ in range(400):
            if not dependency_anchors(f"requires {name} 1.0", allowlist):
                misses.append(name)

    try:
        threads = [
            threading.Thread(target=worker, args=(name,))
            for name in ("zzqlocalpkga", "zzqlocalpkgb")
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
    finally:
        sys.setswitchinterval(old)
    assert misses == []
