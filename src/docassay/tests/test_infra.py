"""Tests for the HAS_DOCKERFILE and HAS_CI_WORKFLOW predicates (infra, §3.5)."""

from __future__ import annotations

from pathlib import Path

from docassay.core.models import Context
from docassay.core.pipeline import analyze_repository
from docassay.evidence.infra import InfraEvidence, build_infra_inventory
from docassay.predicates.infra import (
    INFRA_WORLD,
    ci_workflow_scan,
    dockerfile_scan,
    match_ci_workflow,
    match_dockerfile,
)


def _english_readme(body: str) -> str:
    return "# Demo project\nThis is the demo project that many teams use every day.\n" + body


def test_world_is_closed_over_listing() -> None:
    assert INFRA_WORLD == "closed-over-listing"


# --- extraction -------------------------------------------------------------


def _dockerfile_objects(text: str) -> list[str]:
    return [c.object for c in dockerfile_scan(text, "README.md")]


def test_dockerfile_mention_is_anchor() -> None:
    assert _dockerfile_objects("The project ships a Dockerfile.\n") == ["dockerfile"]
    assert _dockerfile_objects("See the `Dockerfile` at the root.\n") == ["dockerfile"]


def test_dockerfile_instruction_is_not_anchored() -> None:
    # "Create a Dockerfile" instructs the *user* to write one; it is not a
    # claim that the documented project ships a Dockerfile.
    assert dockerfile_scan("Create a Dockerfile for your service.\n", "README.md") == []


def test_dockerfile_example_is_not_anchored() -> None:
    # A how-to mention of the *user's* Dockerfile is not a capability claim.
    assert dockerfile_scan("An example Dockerfile is shown below.\n", "README.md") == []
    assert dockerfile_scan("The Dockerfile below uses pip.\n", "README.md") == []


def test_dockerfile_assertive_mention_anchors() -> None:
    assert dockerfile_scan("The project ships a Dockerfile.\n", "README.md")
    assert dockerfile_scan("A Dockerfile is included at the root.\n", "README.md")


def _ci_objects(text: str) -> list[str]:
    return [c.object for c in ci_workflow_scan(text, "README.md")]


def test_ci_product_mention_is_anchor() -> None:
    assert _ci_objects("The project uses GitHub Actions.\n") == ["ci_workflow"]
    assert _ci_objects("GitLab CI is used for releases.\n") == ["ci_workflow"]
    assert _ci_objects("The continuous integration pipeline deploys.\n") == ["ci_workflow"]


def test_bare_ci_needs_context() -> None:
    assert _ci_objects("Our CI workflow runs tests.\n") == ["ci_workflow"]
    assert _ci_objects("CI/CD pipeline is green.\n") == ["ci_workflow"]
    assert _ci_objects("We run CI on every commit.\n") == []
    assert _ci_objects("The team uses CircleCI.\n") == []


# --- inventory --------------------------------------------------------------


def test_dockerfile_inventory(tmp_path: Path) -> None:
    (tmp_path / "Dockerfile").write_text("FROM python:3.12\n")
    (tmp_path / "docker").mkdir()
    (tmp_path / "docker" / "Dockerfile.dev").write_text("")
    (tmp_path / "notdocker").write_text("")
    inventory = build_infra_inventory(tmp_path)
    dockerfiles = [e for e in inventory if e.kind == "dockerfile"]
    assert {e.path for e in dockerfiles} == {"Dockerfile", "docker/Dockerfile.dev"}


def test_ci_inventory(tmp_path: Path) -> None:
    (tmp_path / ".github").mkdir()
    (tmp_path / ".github" / "workflows").mkdir()
    (tmp_path / ".github" / "workflows" / "ci.yml").write_text("")
    (tmp_path / ".github" / "workflows" / "lint.yaml").write_text("")
    (tmp_path / ".gitlab-ci.yml").write_text("")
    (tmp_path / "Jenkinsfile").write_text("")
    inventory = build_infra_inventory(tmp_path)
    ci = [e for e in inventory if e.kind == "ci"]
    assert {e.path for e in ci} == {
        ".github/workflows/ci.yml",
        ".github/workflows/lint.yaml",
        ".gitlab-ci.yml",
        "Jenkinsfile",
    }


def test_ci_inventory_non_ci_yaml_ignored(tmp_path: Path) -> None:
    (tmp_path / "ci.yml").write_text("")  # root-level yml is not a known CI path
    assert build_infra_inventory(tmp_path) == []


# --- matching ---------------------------------------------------------------


def _infra_evidence(kind: str, *paths: str) -> dict[str, list[InfraEvidence]]:
    object_name = "dockerfile" if kind == "dockerfile" else "ci_workflow"
    return {
        object_name: [InfraEvidence(evidence_id=f"{kind}:{p}", kind=kind, path=p) for p in paths]
    }


def _match_dockerfile(evidence: dict, **flags) -> tuple[str, ...]:
    verdict, support, refute, *_ = match_dockerfile("dockerfile", Context(), evidence, **flags)
    return (verdict, *support, *refute)


def test_match_dockerfile_present_supported() -> None:
    assert _match_dockerfile(_infra_evidence("dockerfile", "Dockerfile"))[0] == "SUPPORTED"


def test_match_dockerfile_absent_refuted() -> None:
    assert _match_dockerfile({})[0] == "REFUTED"


def test_match_dockerfile_absent_instructional_nei() -> None:
    assert _match_dockerfile({}, instructional=True)[0] == "NEI"
    assert _match_dockerfile({}, historical=True)[0] == "NEI"
    assert _match_dockerfile({}, exemplary=True)[0] == "NEI"


def test_match_dockerfile_negation() -> None:
    ev = _infra_evidence("dockerfile", "Dockerfile")
    context = Context(polarity=frozenset({"not"}))
    assert match_dockerfile("dockerfile", context, ev)[0] == "REFUTED"
    assert match_dockerfile("dockerfile", context, {})[0] == "NEI"


def test_match_ci_present_supported() -> None:
    ev = _infra_evidence("ci", ".github/workflows/ci.yml")
    verdict, support, _, *_ = match_ci_workflow("ci_workflow", Context(), ev)
    assert verdict == "SUPPORTED"
    assert support == ("ci:.github/workflows/ci.yml",)


def test_match_ci_absent_refuted() -> None:
    assert match_ci_workflow("ci_workflow", Context(), {})[0] == "REFUTED"


# --- pipeline over a real filesystem ----------------------------------------


def test_analyze_repository_dockerfile_supported(tmp_path: Path) -> None:
    (tmp_path / "Dockerfile").write_text("FROM python:3.12\n")
    (tmp_path / "README.md").write_text(_english_readme("The project ships a Dockerfile.\n"))
    result = analyze_repository(tmp_path)
    refs = {r.object: r for r in result.referents if r.predicate_type == "HAS_DOCKERFILE"}
    assert "dockerfile" in refs
    assert refs["dockerfile"].assertions[0].code_verdict == "SUPPORTED"


def test_analyze_repository_dockerfile_absent_is_finding(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text(_english_readme("The project ships a Dockerfile.\n"))
    result = analyze_repository(tmp_path)
    refs = {r.object: r for r in result.referents if r.predicate_type == "HAS_DOCKERFILE"}
    assert refs["dockerfile"].assertions[0].code_verdict == "REFUTED"


def test_analyze_repository_ci_supported(tmp_path: Path) -> None:
    (tmp_path / ".github").mkdir()
    (tmp_path / ".github" / "workflows").mkdir()
    (tmp_path / ".github" / "workflows" / "ci.yml").write_text("")
    (tmp_path / "README.md").write_text(
        _english_readme("The project uses GitHub Actions for its workflow.\n")
    )
    result = analyze_repository(tmp_path)
    refs = {r.object: r for r in result.referents if r.predicate_type == "HAS_CI_WORKFLOW"}
    assert "ci_workflow" in refs
    assert refs["ci_workflow"].assertions[0].code_verdict == "SUPPORTED"


def test_analyze_repository_ci_absent_is_finding(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text(_english_readme("Our CI workflow runs tests.\n"))
    result = analyze_repository(tmp_path)
    refs = {r.object: r for r in result.referents if r.predicate_type == "HAS_CI_WORKFLOW"}
    assert "ci_workflow" in refs
    assert refs["ci_workflow"].assertions[0].code_verdict == "REFUTED"


def test_analyze_repository_ci_instruction_is_gated(tmp_path: Path) -> None:
    """A directive ("Add a CI workflow") is a non-claim by construction (Phase 2
    claim-gate): it never forms a referent, instead of a would-be NEI."""
    (tmp_path / "README.md").write_text(
        _english_readme("Add a CI workflow before merging changes.\n")
    )
    result = analyze_repository(tmp_path)
    refs = {r.object for r in result.referents if r.predicate_type == "HAS_CI_WORKFLOW"}
    assert "ci_workflow" not in refs
    assert ("HAS_CI_WORKFLOW", "instructional mention", "ci_workflow") in result.gated_claims
