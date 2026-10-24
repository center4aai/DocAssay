"""E6: migration/compatibility/historical version prose is not a requirement.

E1 correctly attaches a version to a duplicate dependency mention, but on real
repositories that turned migration guides, compatibility notes and release
history into ``REFUTED`` claims:

- fastapi's Pydantic v1→v2 migration guide (18 lines of "migrate from v1");
- fastapi ``deployment/versions.md`` ("always compatible with FastAPI");
- prefect "API differences between whenever 0.7.x–0.9.x and ≥ 0.10.0";
- scikit-learn "Starting from joblib >= 0.14", "prior to version scipy 0.16"
  and "Scikit-learn 0.23 required Python 3.6—3.8".

E6 gates the genre at the document level (migration/upgrade guide paths) and
the framing at the claim level (``compatibility`` / ``historical_version``
flags). A would-be version refutation in those contexts is ``NEI`` with a
``CLAIM_GATE`` reason. Current requirements ("requires X>=Y", "depends on X
(>=Y)", "the only runtime dependency is X>=Y") stay refutable.
"""

from __future__ import annotations

from pathlib import Path

from docassay.core.pipeline import _is_excluded_doc, analyze_repository
from docassay.evidence.manifests import DependencyEvidence
from docassay.predicates.dependency import (
    claim_flags,
    is_compatibility_context,
    is_historical_version,
    match_dependency,
    scan_document,
)


def _claim(text: str, object_name: str):
    return next(c for c in scan_document(text, "README.md") if c.object == object_name)


def _inventory(name: str, spec: str) -> dict[str, list[DependencyEvidence]]:
    return {
        name: [
            DependencyEvidence(
                evidence_id=f"{name}:pyproject.toml:{spec}",
                package_name=name,
                version_spec=spec,
                source_file="pyproject.toml",
                source_type="project",
            )
        ]
    }


def _verdict(text: str, object_name: str, spec: str):
    claim = _claim(text, object_name)
    return match_dependency(
        object_name,
        claim.context,
        _inventory(object_name, spec),
        **claim_flags(claim),
    )


def _write_repo(
    tmp_path: Path,
    readme: str,
    dependencies: list[str],
    *,
    requires_python: str = ">=3.11",
    doc_path: str = "README.md",
) -> Path:
    repo = tmp_path / "repo"
    (repo / doc_path).parent.mkdir(parents=True, exist_ok=True)
    deps = ",\n".join(f'    "{dep}"' for dep in dependencies)
    (repo / "pyproject.toml").write_text(
        "[project]\n"
        'name = "demo"\n'
        f'requires-python = "{requires_python}"\n'
        "dependencies = [\n"
        f"{deps}\n"
        "]\n"
    )
    (repo / doc_path).write_text(readme)
    return repo


def _refuted(repo: Path) -> list[tuple[str, str]]:
    result = analyze_repository(repo)
    return [
        (referent.predicate_type, referent.object)
        for referent in result.referents
        for assertion in referent.assertions
        if assertion.code_verdict == "REFUTED"
    ]


def _dependency_verdict(repo: Path, object_name: str) -> str:
    result = analyze_repository(repo)
    assertions = [
        assertion
        for referent in result.referents
        if referent.predicate_type == "DEPENDENCY" and referent.object == object_name
        for assertion in referent.assertions
    ]
    assert assertions, f"no DEPENDENCY {object_name} assertion"
    return assertions[0].code_verdict


# --- document level: migration/upgrade guides are historical genre ----------


def test_migration_guide_path_is_excluded() -> None:
    assert _is_excluded_doc(
        "docs/en/docs/how-to/migrate-from-pydantic-v1-to-pydantic-v2.md"
    )
    assert _is_excluded_doc("docs/upgrade-guide.md")
    # Ordinary current-reference docs stay scanned.
    assert not _is_excluded_doc("docs/deployment/versions.md")
    assert not _is_excluded_doc("docs/how-to/using-the-api.rst")


def test_fastapi_migration_guide_produces_no_refutation(tmp_path: Path) -> None:
    readme = (
        "# Migrate from Pydantic v1 to Pydantic v2\n"
        "\n"
        "If you have an old FastAPI app, you might be using Pydantic version 1.\n"
        "\n"
        "FastAPI 0.100.0 had support for either Pydantic v1 or v2.\n"
        "\n"
        "Pydantic version 1 is still supported by older FastAPI releases.\n"
    )
    repo = _write_repo(
        tmp_path,
        readme,
        ["pydantic>=2.7"],
        doc_path="docs/en/docs/how-to/migrate-from-pydantic-v1-to-pydantic-v2.md",
    )
    result = analyze_repository(repo)
    assert result.claims == []  # excluded before claim formation
    assert _refuted(repo) == []


# --- claim level: compatibility / migration framing -------------------------


def test_prefect_whenever_compatibility_ranges_are_nei() -> None:
    text = (
        "Use `whenever` compat helpers to abstract over API differences between "
        "whenever 0.7.x–0.9.x and ≥ 0.10.0.\n"
    )
    claim = _claim(text, "whenever")
    flags = claim_flags(claim)
    assert flags["compatibility"] is True
    verdict = match_dependency(
        "whenever", claim.context, _inventory("whenever", ">=0.7.3,<0.11.0"), **flags
    )
    assert verdict.outcome == "NEI"
    assert verdict.layer == "CLAIM_GATE"
    assert verdict.reason == "compatibility mention"


def test_sklearn_starting_from_joblib_is_nei() -> None:
    text = (
        "Starting from ``joblib >= 0.14``, when the ``loky`` backend is used "
        "(which is the default), joblib will limit child threads.\n"
    )
    assert _claim(text, "joblib").context.version == ">=0.14"
    verdict = _verdict(text, "joblib", ">=1.4.0")
    assert verdict.outcome == "NEI"
    assert verdict.reason == "compatibility mention"


def test_sklearn_prior_to_scipy_version_is_nei() -> None:
    text = (
        "The distributions in ``scipy.stats`` prior to version scipy 0.16 do not "
        "allow specifying a random state.\n"
    )
    verdict = _verdict(text, "scipy", ">=1.10.0")
    assert verdict.outcome == "NEI"
    assert verdict.reason == "compatibility mention"


def test_sklearn_release_history_python_is_nei() -> None:
    text = "Scikit-learn 0.23 required Python 3.6—3.8.\n"
    claim = _claim(text, "python")
    assert is_historical_version(claim) is True
    verdict = _verdict(text, "python", ">=3.11")
    assert verdict.outcome == "NEI"
    assert verdict.reason == "historical version mention"


def test_fastapi_stale_compatibility_advice_is_nei() -> None:
    text = (
        "Pydantic includes the tests for FastAPI with its own tests, so new "
        "versions of Pydantic (above `1.0.0`) are always compatible with FastAPI.\n"
    )
    verdict = _verdict(text, "pydantic", ">=2.7.0,<3.0.0")
    assert verdict.outcome == "NEI"
    assert verdict.reason == "compatibility mention"


def test_historical_pydantic_v1_prose_does_not_refute() -> None:
    text = "This is a migration guide from Pydantic v1 to Pydantic v2.\n"
    claim = _claim(text, "pydantic")
    assert is_compatibility_context(claim) is True
    verdict = _verdict(text, "pydantic", ">=2.7")
    assert verdict.outcome == "NEI"
    assert verdict.reason == "compatibility mention"


def test_compatibility_phrase_family_is_flagged() -> None:
    cases = [
        ("You can migrate from Django 1.4 to 2.0.", "django"),
        ("You can upgrade from Celery 4.0 to 5.0.", "celery"),
        ("This is compatible with Flask 2.0.", "flask"),
        ("The API differences between numpy 1.24 and 2.0 are documented.", "numpy"),
        ("Before version scipy 0.16 the API differed.", "scipy"),
    ]
    for text, object_name in cases:
        assert is_compatibility_context(_claim(text, object_name)) is True, text


def test_release_history_phrase_family_is_historical() -> None:
    cases = [
        ("This feature was introduced in Django 1.4.", "django"),
        ("The API was released in Celery 5.0.", "celery"),
        ("The option was deprecated in Flask 2.0.", "flask"),
    ]
    for text, object_name in cases:
        claim = _claim(text, object_name)
        assert claim_flags(claim)["historical"] is True, text
        verdict = match_dependency(
            object_name,
            claim.context,
            _inventory(object_name, ">=999"),
            **claim_flags(claim),
        )
        assert verdict.outcome == "NEI", text


# --- current requirements stay refutable ------------------------------------


def test_current_requirement_still_refutes() -> None:
    text = "This project requires requests>=2.0 for HTTP.\n"
    claim = _claim(text, "requests")
    assert claim_flags(claim)["compatibility"] is False
    assert claim_flags(claim)["historical_version"] is False
    verdict = _verdict(text, "requests", ">=999")
    assert verdict.outcome == "REFUTED"


def test_gaugekit_numpy_injected_manifest_still_refutes(tmp_path: Path) -> None:
    readme = (
        "# gaugekit\n\n"
        "gaugekit depends on NumPy (`numpy>=1.24`). From a checkout of the repository:\n"
    )
    repo = _write_repo(tmp_path, readme, ["numpy>=999"])
    assert _dependency_verdict(repo, "numpy") == "REFUTED"


def test_sheetmusic_click_injected_manifest_still_refutes(tmp_path: Path) -> None:
    readme = (
        "# sheetmusic\n\n"
        "The only declared runtime dependency is `click>=8.1`.\n"
    )
    repo = _write_repo(tmp_path, readme, ["click<8.1"])
    assert _dependency_verdict(repo, "click") == "REFUTED"


# --- clean baselines: the precision gate adds no refutation -----------------


def test_clean_stage_b_baselines_stay_clean(tmp_path: Path) -> None:
    gaugekit = _write_repo(
        tmp_path / "gaugekit",
        "# gaugekit\n\ngaugekit depends on NumPy (`numpy>=1.24`).\n",
        ["numpy>=1.24"],
    )
    sheetmusic = _write_repo(
        tmp_path / "sheetmusic",
        "# sheetmusic\n\nThe only declared runtime dependency is `click>=8.1`.\n",
        ["click>=8.1"],
    )
    assert _dependency_verdict(gaugekit, "numpy") == "SUPPORTED"
    assert _dependency_verdict(sheetmusic, "click") == "SUPPORTED"
    assert _refuted(gaugekit) == []
    assert _refuted(sheetmusic) == []


def test_real_repo_compatibility_lines_have_no_refutation(tmp_path: Path) -> None:
    readme = (
        "# Notes\n"
        "\n"
        "Use helpers to abstract over API differences between whenever "
        "0.7.x–0.9.x and ≥ 0.10.0.\n"
        "\n"
        "Starting from ``joblib >= 0.14``, the loky backend is used by default "
        "and will limit child threads.\n"
        "\n"
        "The distributions prior to version scipy 0.16 do not allow a random state.\n"
        "\n"
        "Scikit-learn 0.23 required Python 3.6—3.8.\n"
        "\n"
        "New Pydantic versions (above `1.0.0`) are always compatible with FastAPI.\n"
    )
    repo = _write_repo(
        tmp_path,
        readme,
        [
            "whenever>=0.7.3,<0.11.0",
            "joblib>=1.4.0",
            "scipy>=1.10.0",
            "pydantic>=2.7.0,<3.0.0",
        ],
        requires_python=">=3.11",
    )
    assert _refuted(repo) == []
