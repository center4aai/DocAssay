"""Tests for the LICENSE predicate (project-meta group, §3.6)."""

from __future__ import annotations

from pathlib import Path

from docassay.core.models import Context
from docassay.core.pipeline import analyze_repository
from docassay.evidence.project import (
    LicenseEvidence,
    build_license_inventory,
    canonical_license,
)
from docassay.predicates.crossdoc import (
    LICENSE_WORLD,
    license_scan,
    match_license,
)


def _english_readme(body: str) -> str:
    return "# Demo project\nThis is the demo project that many teams use every day.\n" + body


# --- canonicalization --------------------------------------------------------


def test_canonical_license_folds() -> None:
    assert canonical_license("MIT") == "mit"
    assert canonical_license("apache-2.0") == "apache-2.0"
    assert canonical_license("apache", "==2.0") == "apache-2.0"
    assert canonical_license("apache") == "apache"
    assert canonical_license("BSD-3-Clause") == "bsd"
    assert canonical_license("BSD 3-Clause") == "bsd"
    assert canonical_license("gpl", ">=3") == "gpl-3.0"
    assert canonical_license("gpl-2.0") == "gpl-2.0"
    assert canonical_license("CC-BY-4.0") == "cc-by"
    assert canonical_license("MulanPSL-2.0") == "mulanpsl-2.0"


def test_canonical_license_worlds() -> None:
    assert LICENSE_WORLD == "closed-over-field-and-file"


# --- LICENSE extraction ------------------------------------------------------


def _license_objects(text: str) -> list[tuple[str, str | None]]:
    return [(c.object, c.context.version) for c in license_scan(text, "README.md")]


def test_license_name_in_context_is_anchor() -> None:
    assert _license_objects("released under the MIT license.\n") == [("mit", None)]
    assert _license_objects("Licensed under Apache 2.0.\n") == [("apache-2.0", "==2.0")]
    assert _license_objects("Apache License, Version 2.0\n") == [("apache-2.0", None)]
    assert _license_objects("GPL-3.0 license\n") == [("gpl-3.0", None)]
    assert _license_objects("GPL v3 license\n") == [("gpl-3.0", ">=3")]


def test_apache_as_project_name_is_not_anchor() -> None:
    assert _license_objects("Apache Airflow is a workflow platform.\n") == []
    assert _license_objects("Apache Superset is a BI tool.\n") == []


def test_apache_airflow_licensed_only_apache_version_claims() -> None:
    objects = _license_objects("Apache Airflow is licensed under Apache 2.0\n")
    assert objects == [("apache-2.0", "==2.0")]


def test_bsd_clause_folds_to_bsd() -> None:
    assert _license_objects("released under the BSD 3-Clause license\n") == [("bsd", ">=3")]


def test_license_word_required() -> None:
    assert _license_objects("The MIT student union uses this.\n") == []
    assert _license_objects("GPL bikes are popular.\n") == []


# --- matching (LICENSE) ------------------------------------------------------


def _license_evidence(*names: str) -> dict[str, list[LicenseEvidence]]:
    return {
        name: [
            LicenseEvidence(
                evidence_id=f"license:pyproject.toml:{name}",
                license_name=name,
                source_file="pyproject.toml",
            )
        ]
        for name in names
    }


def _match_l(claimed: str, evidence: dict, **flags) -> tuple[str, ...]:
    context = Context()
    verdict, support, refute, *_ = match_license(claimed, context, evidence, **flags)
    return (verdict, *support, *refute)


def test_license_match_declared_supported() -> None:
    assert _match_l("mit", _license_evidence("mit"))[0] == "SUPPORTED"


def test_license_match_mismatch_refuted() -> None:
    assert _match_l("apache-2.0", _license_evidence("mit"))[0] == "REFUTED"


def test_license_match_undeclared_nei() -> None:
    assert _match_l("mit", {})[0] == "NEI"


def test_license_match_negation_refutes() -> None:
    ev = _license_evidence("mit")
    context = Context(polarity=frozenset({"not"}))
    assert match_license("mit", context, ev)[0] == "REFUTED"
    assert match_license("mit", context, {})[0] == "NEI"


def test_license_match_historical_downgrades() -> None:
    assert _match_l("apache-2.0", _license_evidence("mit"), historical=True)[0] == "NEI"


# --- inventory ---------------------------------------------------------------


def test_license_inventory_from_field(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "demo"\nlicense = "Apache-2.0"\n')
    evidence = build_license_inventory(tmp_path)
    assert [e.license_name for e in evidence] == ["apache-2.0"]


def test_license_inventory_from_file(tmp_path: Path) -> None:
    (tmp_path / "LICENSE").write_text("Apache License\nVersion 2.0, January 2004\nCopyright 2024\n")
    evidence = build_license_inventory(tmp_path)
    assert [e.license_name for e in evidence] == ["apache-2.0"]
    assert evidence[0].source_file == "LICENSE"


# --- pipeline over a real filesystem ----------------------------------------


def test_analyze_repository_license_supported(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "demo"\nlicense = "MIT"\n')
    (tmp_path / "README.md").write_text(
        _english_readme("This project is released under the MIT license.\n")
    )
    result = analyze_repository(tmp_path)
    refs = {r.object: r for r in result.referents if r.predicate_type == "LICENSE"}
    assert "mit" in refs
    assert refs["mit"].assertions[0].code_verdict == "SUPPORTED"


def test_analyze_repository_license_drift_is_finding(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "demo"\nlicense = "MIT"\n')
    (tmp_path / "README.md").write_text(
        _english_readme("The project is licensed under Apache 2.0.\n")
    )
    result = analyze_repository(tmp_path)
    refs = {r.object: r for r in result.referents if r.predicate_type == "LICENSE"}
    assert "apache-2.0" in refs
    assert refs["apache-2.0"].assertions[0].code_verdict == "REFUTED"


def test_analyze_repository_no_manifest_abstains(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text(
        _english_readme("The project is licensed under the MIT license.\n")
    )
    result = analyze_repository(tmp_path)
    license_refs = [r for r in result.referents if r.predicate_type == "LICENSE"]
    assert all(a.code_verdict == "NEI" for r in license_refs for a in r.assertions)


# --- Phase 5: SPDX and full license texts -----------------------


def test_canonical_licenses_splits_spdx_expression() -> None:
    from docassay.evidence.project import canonical_licenses

    assert canonical_licenses("BSD-3-Clause AND 0BSD AND MIT AND CC0-1.0") == [
        "bsd",
        "0bsd",
        "mit",
        "cc0",
    ]
    assert canonical_licenses("MIT") == ["mit"]
    assert canonical_licenses("") == []


def test_gplv3_license_anchor() -> None:
    # "GPLv3" has no hyphen before the version.
    assert _license_objects("GPLv3 license\n") == [("gpl-3.0", None)]
    assert canonical_license("LGPLv2.1") == "lgpl-2.1"


def test_full_license_text_headers_are_detected() -> None:
    from docassay.evidence.project import detect_licenses_in_text

    assert detect_licenses_in_text("GNU GENERAL PUBLIC LICENSE\nVersion 3, 29 June 2007\n") == [
        "gpl-3.0"
    ]
    assert detect_licenses_in_text(
        "GNU LESSER GENERAL PUBLIC LICENSE\nVersion 2.1, February 1999\n"
    ) == ["lgpl-2.1"]
    assert detect_licenses_in_text("Mozilla Public License Version 2.0\n") == ["mpl-2.0"]
    # Body-only texts (no name header).
    assert detect_licenses_in_text(
        "Copyright (c) 2025 X\n\nPermission is hereby granted, free of charge, to "
        "any person obtaining a copy\n"
    ) == ["mit"]


def test_vendor_license_is_not_the_project_license(tmp_path: Path) -> None:
    # An Apache LICENSE vendored under crates/ must not make Apache the
    # declared license of an MIT project.
    (tmp_path / "crates" / "dep").mkdir(parents=True)
    (tmp_path / "crates" / "dep" / "LICENSE").write_text(
        "Apache License\nVersion 2.0, January 2004\n"
    )
    (tmp_path / "LICENSE").write_text("MIT License\nCopyright 2025\n")
    names = {e.license_name for e in build_license_inventory(tmp_path)}
    assert names == {"mit"}


def test_license_family_claim_matches_versioned_declaration() -> None:
    # "licensed under the GPL" is under-specified but true when the manifest
    # declares GPL-3.0-or-later.
    assert _match_l("gpl", _license_evidence("gpl-3.0"))[0] == "SUPPORTED"
    assert canonical_license("GPL-3.0-or-later") == "gpl-3.0"
    # A different family still refutes.
    assert _match_l("apache-2.0", _license_evidence("gpl-3.0"))[0] == "REFUTED"


def test_third_party_attribution_is_not_a_project_claim() -> None:
    # "parts adapted from projectx, which is licensed under Apache 2.0" does
    # not claim the project is Apache.
    ev = _license_evidence("mit")
    assert match_license("apache-2.0", Context(), ev, third_party=True)[0] == "NEI"
