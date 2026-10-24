"""E1/E2 regressions: version-bearing duplicate anchors and disjoint intervals.

E1 (Stage B): ``gaugekit depends on NumPy (`numpy>=1.24`)`` produced one
versionless ``DEPENDENCY numpy`` claim, because the first mention won the
same-line dedupe and the versioned second mention was dropped. A versionless
claim is SUPPORTED for any declared manifest spec, so an injected ``>=999``
was invisible.

E2 (Stage B): ``constraint_satisfied(">=8.1", "<8.1")`` returned ``True``
because only lower-to-lower and upper-to-upper bounds were compared; the two
intervals are disjoint, so the doc claim is contradicted by the manifest.
"""

from __future__ import annotations

from pathlib import Path

from docassay.core.pipeline import analyze_repository
from docassay.markers.version import constraint_satisfied
from docassay.predicates.dependency import scan_document


def _claims(text: str):
    return scan_document(text, "README.md")


def _numpy_claim(text: str):
    claims = [c for c in _claims(text) if c.object == "numpy"]
    assert len(claims) == 1, claims
    return claims[0]


def _dependency_verdict(repo: Path, object_name: str) -> str | None:
    result = analyze_repository(repo)
    assertions = [
        assertion
        for referent in result.referents
        if referent.predicate_type == "DEPENDENCY" and referent.object == object_name
        for assertion in referent.assertions
    ]
    assert assertions, f"no DEPENDENCY {object_name} assertion"
    return assertions[0].code_verdict


# --- E1: duplicate mention keeps the versioned occurrence -------------------


def test_duplicate_mention_keeps_versioned_occurrence() -> None:
    claim = _numpy_claim(
        "gaugekit depends on NumPy (`numpy>=1.24`). From a checkout of the repository:\n"
    )
    assert claim.context.version == ">=1.24"


def test_duplicate_mention_requests_pattern() -> None:
    claim = _claims("requests (requests>=2.0) is the HTTP client.\n")
    assert len(claim) == 1
    assert claim[0].object == "requests"
    assert claim[0].context.version == ">=2.0"


def test_duplicate_mention_django_pattern() -> None:
    claims = _claims("Django (django>=4.2) is the web framework.\n")
    assert len(claims) == 1
    assert claims[0].object == "django"
    assert claims[0].context.version == ">=4.2"


def test_versionless_repeat_stays_versionless() -> None:
    claim = _numpy_claim("numpy is used; numpy is fast.\n")
    assert claim.context.version is None


def test_single_versioned_mention_is_unchanged() -> None:
    claim = _numpy_claim("numpy>=1.24 is required.\n")
    assert claim.context.version == ">=1.24"


def test_duplicate_mention_end_to_end_version_is_adjudicated(tmp_path: Path) -> None:
    clean = tmp_path / "clean"
    injected = tmp_path / "injected"
    readme = (
        "# Demo\n\ngaugekit depends on NumPy (`numpy>=1.24`). From a checkout of the repository:\n"
    )
    for repo, spec in ((clean, ">=1.24"), (injected, ">=999")):
        repo.mkdir()
        (repo / "pyproject.toml").write_text(
            "[project]\n"
            'name = "gaugekit"\n'
            'requires-python = ">=3.11"\n'
            f'dependencies = ["numpy{spec}"]\n'
        )
        (repo / "README.md").write_text(readme)

    assert _dependency_verdict(clean, "numpy") == "SUPPORTED"
    assert _dependency_verdict(injected, "numpy") == "REFUTED"


# --- E2: disjoint intervals are contradictions ------------------------------


def test_disjoint_lower_and_upper_bounds_are_refuted() -> None:
    assert constraint_satisfied(">=8.1", "<8.1") is False


def test_disjoint_strict_bounds_are_refuted() -> None:
    assert constraint_satisfied(">8.1", "<=8.1") is False


def test_overlapping_lower_and_upper_bounds_are_supported() -> None:
    assert constraint_satisfied(">=8.1", "<9") is True


def test_doc_below_manifest_floor_is_refuted() -> None:
    assert constraint_satisfied(">=8.1", ">=999") is False


def test_pin_below_upper_bound_is_refuted() -> None:
    assert constraint_satisfied("==8.1", "<8.1") is False


def test_compatible_release_expansion_is_checked_before_comparison() -> None:
    # ~=8.1 expands to >=8.1,<9.0, which does not intersect <8.1.
    assert constraint_satisfied("~=8.1", "<8.1") is False


def test_excluded_only_point_is_refuted() -> None:
    assert constraint_satisfied("!=8.1", "==8.1") is False


def test_baseline_equal_lower_bound_is_supported() -> None:
    assert constraint_satisfied(">=8.1", ">=8.1") is True


def test_upper_bound_only_claim_stays_nei() -> None:
    assert constraint_satisfied("<4", ">=3.10") is None
