"""Tests for the domain layer.

Claims and evidence are stamped with the manifest-bearing directory that
contains their file, so monorepo sub-projects never mix in one referent and a
sub-project's DEPENDENCY claim adjudicates against its own manifest only.
"""

from __future__ import annotations

from pathlib import Path

from docassay.core.domains import DomainIndex
from docassay.core.pipeline import analyze_repository


def _english_readme(body: str) -> str:
    return "# Demo project\nThis is the demo project that many teams use every day.\n" + body


def _dependency_verdicts(result) -> dict[tuple[str, str], str]:
    """(object, domain) → code_verdict over DEPENDENCY referents."""
    out: dict[tuple[str, str], str] = {}
    for ref in result.referents:
        if ref.predicate_type != "DEPENDENCY":
            continue
        verdicts = {a.code_verdict for a in ref.assertions}
        out[(ref.object, ref.domain)] = verdicts.pop() if len(verdicts) == 1 else "MIXED"
    return out


# --- DomainIndex --------------------------------------------------------------


def test_single_manifest_maps_everything_to_root(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'demo'\n")
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "x.md").write_text("x\n")
    index = DomainIndex.build(tmp_path)
    assert index.is_single_domain
    assert index.domain_for("README.md") == ""
    assert index.domain_for("docs/x.md") == ""
    assert index.domain_for("src/pkg/__init__.py") == ""


def test_monorepo_maps_files_to_deepest_manifest_dir(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'root'\n")
    for d in ("libs/core", "providers/amazon"):
        (tmp_path / d).mkdir(parents=True)
        (tmp_path / d / "pyproject.toml").write_text("[project]\nname = 'pkg'\n")
    index = DomainIndex.build(tmp_path)
    assert not index.is_single_domain
    assert index.domain_for("README.md") == ""
    assert index.domain_for("libs/core/README.md") == "libs/core"
    assert index.domain_for("providers/amazon/docs/x.md") == "providers/amazon"
    assert index.domain_for("libs/core/pyproject.toml") == "libs/core"


def test_deepest_manifest_dir_wins(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'root'\n")
    (tmp_path / "a").mkdir()
    (tmp_path / "a" / "pyproject.toml").write_text("[project]\nname = 'a'\n")
    (tmp_path / "a" / "b").mkdir()
    (tmp_path / "a" / "b" / "pyproject.toml").write_text("[project]\nname = 'b'\n")
    index = DomainIndex.build(tmp_path)
    assert index.domain_for("a/README.md") == "a"
    assert index.domain_for("a/b/README.md") == "a/b"


def test_domain_boundary_requires_segment_boundary(tmp_path: Path) -> None:
    (tmp_path / "providers").mkdir()
    (tmp_path / "providers" / "amazon").mkdir()
    (tmp_path / "providers" / "amazon" / "pyproject.toml").write_text("[project]\nname = 'x'\n")
    index = DomainIndex.build(tmp_path)
    assert index.domain_for("providers/amazon/x.md") == "providers/amazon"
    assert index.domain_for("providers/amazonaws/x.md") == ""


def test_domain_for_normalizes_input(tmp_path: Path) -> None:
    (tmp_path / "Libs").mkdir()
    (tmp_path / "Libs" / "Core").mkdir()
    (tmp_path / "Libs" / "Core" / "pyproject.toml").write_text("[project]\nname = 'x'\n")
    index = DomainIndex.build(tmp_path)
    assert index.domain_for("Libs/Core/README.md") == "libs/core"


# --- pipeline integration -----------------------------------------------------


def _build_monorepo(tmp_path: Path) -> Path:
    (tmp_path / "pyproject.toml").write_text(
        "[project]\nname = 'root'\ndependencies = ['numpy>=1.20']\n"
    )
    libs = tmp_path / "libs" / "core"
    libs.mkdir(parents=True)
    (libs / "pyproject.toml").write_text(
        "[project]\nname = 'core'\ndependencies = ['requests>=2.0']\n"
    )
    (tmp_path / "README.md").write_text(_english_readme("This project uses numpy and requests.\n"))
    (libs / "README.md").write_text(_english_readme("The core library uses requests.\n"))
    (libs / "docs").mkdir()
    (libs / "docs" / "usage.md").write_text(_english_readme("The core does not use numpy.\n"))
    return tmp_path


def test_sub_projects_split_into_separate_referents(tmp_path: Path) -> None:
    root = _build_monorepo(tmp_path)
    result = analyze_repository(root)
    verdicts = _dependency_verdicts(result)

    # The same object claimed from the root README and a sub-project README
    # lands in two different referents, each adjudicated against its own
    # manifest.
    assert ("requests", "") in verdicts
    assert ("requests", "libs/core") in verdicts


def test_root_claim_sees_union_of_manifests(tmp_path: Path) -> None:
    root = _build_monorepo(tmp_path)
    result = analyze_repository(root)
    verdicts = _dependency_verdicts(result)
    # The root README describes the whole repo: numpy is declared in the root
    # manifest, requests in a sub-manifest — both support the root claim.
    assert verdicts[("numpy", "")] == "SUPPORTED"
    assert verdicts[("requests", "")] == "SUPPORTED"


def test_sub_project_claim_adjudicates_against_own_manifest(tmp_path: Path) -> None:
    root = _build_monorepo(tmp_path)
    result = analyze_repository(root)
    verdicts = _dependency_verdicts(result)
    # "uses requests" from libs/core → declared in libs/core manifest.
    assert verdicts[("requests", "libs/core")] == "SUPPORTED"
    # "does not use numpy" from libs/core → numpy is NOT declared in the
    # libs/core manifest, so the negation abstains (NEI) instead of refuting
    # against the root manifest's declaration.
    assert verdicts[("numpy", "libs/core")] == "NEI"


def test_evidence_is_domain_stamped(tmp_path: Path) -> None:
    root = _build_monorepo(tmp_path)
    result = analyze_repository(root)
    by_object = {e.object: e for e in result.evidence}
    assert by_object["numpy"].domain == ""
    assert by_object["requests"].domain == "libs/core"
