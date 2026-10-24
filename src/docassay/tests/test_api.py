"""Tests for the deterministic fact-inventory API (docassay.api).

The API is the agent-facing surface over the pipeline: it must expose the same
facts and verdicts the CLI reports, so this pins the inventory shape, the
single-claim verdicts (including a refutation and an abstention) and lookup.
"""

from __future__ import annotations

from pathlib import Path

from docassay.api import PREDICATE_NAMES, Oracle, build_inventory, verify_claim


def _english_readme(body: str) -> str:
    return "# Demo project\nThis is the demo project that many teams use every day.\n" + body


def _mini_repo(tmp_path: Path) -> Path:
    (tmp_path / "pyproject.toml").write_text(
        "[project]\n"
        'name = "demo"\n'
        'version = "1.2.3"\n'
        'dependencies = ["requests>=2.0"]\n'
        "\n"
        "[project.scripts]\n"
        'demo = "demo:main"\n'
    )
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "mod.py").write_text("class Klass:\n    pass\n")
    (tmp_path / "README.md").write_text(
        _english_readme("The project ships `src/mod.py` and defines `Klass`.\n")
    )
    return tmp_path


def test_build_inventory_shape(tmp_path: Path) -> None:
    inventory = build_inventory(_mini_repo(tmp_path))

    assert inventory.predicates  # at least dependency + path + symbol
    assert set(inventory.counts()) == set(PREDICATE_NAMES)
    assert inventory.for_predicate("PATH_EXISTS")
    # provenance is carried on every fact
    for fact in inventory.facts:
        assert fact.evidence_id


def test_metadata_reports_license_and_dependencies(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "demo"\nlicense = "MIT"\ndependencies = ["requests>=2.0"]\n'
    )
    inventory = build_inventory(tmp_path)

    metadata = inventory.metadata()
    assert metadata["licenses"] == ["mit"]
    assert "requests" in metadata["dependencies"]
    assert "versions" not in metadata


def test_lookup_is_case_insensitive(tmp_path: Path) -> None:
    inventory = build_inventory(_mini_repo(tmp_path))

    assert inventory.lookup("PATH_EXISTS", "SRC/MOD.PY")
    assert inventory.lookup("SYMBOL_EXISTS", "klass")


def test_verify_declared_dependency_is_supported(tmp_path: Path) -> None:
    result = verify_claim(_mini_repo(tmp_path), "The project depends on requests.")

    assert result.status == "SUPPORTED"
    assert any(v.predicate == "DEPENDENCY" and v.verdict == "SUPPORTED" for v in result.verdicts)


def test_verify_undeclared_dependency_abstains(tmp_path: Path) -> None:
    result = verify_claim(_mini_repo(tmp_path), "The project depends on flask.")

    assert result.status == "NEI"
    abstained = next(v for v in result.verdicts if v.predicate == "DEPENDENCY")
    assert abstained.layer == "WORLD"


def test_predicate_vocabulary_is_six_predicates() -> None:
    assert PREDICATE_NAMES == (
        "DEPENDENCY",
        "PATH_EXISTS",
        "SYMBOL_EXISTS",
        "LICENSE",
        "HAS_DOCKERFILE",
        "HAS_CI_WORKFLOW",
    )
    assert "VERSION" not in PREDICATE_NAMES


def test_verify_path_referent_is_supported(tmp_path: Path) -> None:
    result = verify_claim(_mini_repo(tmp_path), "See `src/mod.py` for details.")

    supported = [v for v in result.verdicts if v.predicate == "PATH_EXISTS"]
    assert supported and supported[0].object == "src/mod.py"
    assert supported[0].verdict == "SUPPORTED"
    assert supported[0].supporting  # evidence ids are exposed


def test_verify_stale_path_is_refuted(tmp_path: Path) -> None:
    result = verify_claim(_mini_repo(tmp_path), "See `src/missing.py` for details.")

    assert result.status == "REFUTED"
    assert any(
        v.predicate == "PATH_EXISTS" and v.object == "src/missing.py" and v.verdict == "REFUTED"
        for v in result.verdicts
    )


def test_verify_unknown_text_has_no_claim(tmp_path: Path) -> None:
    result = verify_claim(_mini_repo(tmp_path), "The weather today is pleasant.")

    assert result.status == "NO_CLAIM"
    assert result.verdicts == ()


def test_oracle_caches_inventory(tmp_path: Path) -> None:
    oracle = Oracle(_mini_repo(tmp_path))

    first = oracle.inventory
    assert oracle.inventory is first  # cached across calls
    assert oracle.refresh() is not first  # refresh rebuilds


def test_oracle_list_facts_filters(tmp_path: Path) -> None:
    oracle = Oracle(_mini_repo(tmp_path))

    facts = oracle.list_facts(predicate="PATH_EXISTS")
    assert facts and all(f["predicate"] == "PATH_EXISTS" for f in facts)
    assert oracle.list_facts(limit=1)
