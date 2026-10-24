"""Tests for the JSON bundle + Markdown export (Mode A, stdlib only).

The bundle is the contract the web viewer consumes, so its schema is pinned
here: meta summary, referent → assertion → claim hierarchy with full claim
provenance, the evidence map, and triage findings.
"""

from __future__ import annotations

import json
from pathlib import Path

from docassay.core.bundle import to_bundle, to_markdown
from docassay.core.dump_claims import dump
from docassay.core.pipeline import analyze_repository


def _english_readme(body: str) -> str:
    return "# Demo project\nThis is the demo project that many teams use every day.\n" + body


def _mini_repo(tmp_path: Path) -> Path:
    (tmp_path / "requirements.txt").write_text("requests==2.31.0\n")
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "mod.py").write_text("class Klass:\n    pass\n")
    (tmp_path / "README.md").write_text(
        _english_readme("The project uses requests for the http client and ships `src/mod.py`.\n")
    )
    return tmp_path


def test_bundle_schema(tmp_path: Path) -> None:
    root = _mini_repo(tmp_path)
    bundle = to_bundle(analyze_repository(root))

    meta = bundle["meta"]
    assert meta["repo"] == tmp_path.name
    assert meta["claims"] >= 2
    assert meta["referents"] >= 2
    assert meta["evidence"] >= 1
    assert meta["scanned_documents"] == 1
    assert "verdicts" in meta and "coverage" in meta
    assert {"SUPPORTED", "REFUTED", "NEI"} & set(meta["verdicts"])
    assert set(bundle) == {"meta", "referents", "evidence", "findings"}

    predicates = {r["predicate_type"] for r in bundle["referents"]}
    assert {"DEPENDENCY", "PATH_EXISTS"} <= predicates


def test_bundle_claim_provenance(tmp_path: Path) -> None:
    bundle = to_bundle(analyze_repository(_mini_repo(tmp_path)))
    ref = next(r for r in bundle["referents"] if r["object"] == "requests")
    claim = ref["assertions"][0]["claims"][0]
    assert claim["source"] == "README.md"
    assert claim["line_start"] == 3
    assert claim["line_end"] == 3
    assert claim["negative"] is False
    assert "raw_context" in claim and "context" in claim
    assert claim["extraction_source"] == "regex"


def test_bundle_context_markers_are_split(tmp_path: Path) -> None:
    # The context contract is polarity/restriction, not the legacy scope.
    bundle = to_bundle(analyze_repository(_mini_repo(tmp_path)))
    ref = next(r for r in bundle["referents"] if r["object"] == "requests")
    context = ref["assertions"][0]["claims"][0]["context"]
    assert set(context) == {"version", "platform", "polarity", "restriction", "time", "arch"}
    assert context["polarity"] == []
    assert context["restriction"] == []


def test_bundle_evidence_provenance(tmp_path: Path) -> None:
    bundle = to_bundle(analyze_repository(_mini_repo(tmp_path)))
    ev = bundle["evidence"]["requests:requirements.txt:==2.31.0"]
    assert ev == {
        "source_file": "requirements.txt",
        "domain": "",
        "line_start": 1,
        "line_end": 1,
        "kind": "requirements",
        "snippet": "requests==2.31.0",
    }
    file_ev = next(
        e
        for e in bundle["evidence"].values()
        if e["source_file"] == "src/mod.py" and e["kind"] == "class"
    )
    assert file_ev["line_start"] == 1
    assert file_ev["snippet"] == "class Klass:"


def test_bundle_deterministic_except_created(tmp_path: Path) -> None:
    root = _mini_repo(tmp_path)
    # The symbol cache lives in the user cache (keyed by root hash), never inside
    # the analyzed tree, so it cannot leak into the PATH_EXISTS listing (REPORT
    # B18).
    first = to_bundle(analyze_repository(root))
    second = to_bundle(analyze_repository(root))
    first["meta"].pop("created")
    second["meta"].pop("created")
    assert first == second


def test_bundle_findings(tmp_path: Path) -> None:
    root = _mini_repo(tmp_path)
    (root / "README.md").write_text(
        _english_readme("The project references the missing `src/ghost.py` file.\n")
    )
    bundle = to_bundle(analyze_repository(root))
    finding = next(f for f in bundle["findings"] if f["object"] == "src/ghost.py")
    assert finding["verdict"] == "REFUTED"
    assert finding["predicate"] == "PATH_EXISTS"
    assert finding["primary_line_start"] == 3


def test_bundle_has_no_doc_consistency_fields(tmp_path: Path) -> None:
    bundle = to_bundle(analyze_repository(_mini_repo(tmp_path)))
    assert "doc_consistency" not in bundle["meta"]
    for referent in bundle["referents"]:
        assert "doc_consistency" not in referent
        assert "doc_conflicts" not in referent


def test_dump_claims_has_no_doc_consistency_fields(tmp_path: Path) -> None:
    output = tmp_path / "claims.jsonl"
    dump(_mini_repo(tmp_path), output)
    records = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]
    assert records
    for record in records:
        assert "doc_consistency" not in record
        assert "doc_conflicts" not in record


def test_markdown_render(tmp_path: Path) -> None:
    bundle = to_bundle(analyze_repository(_mini_repo(tmp_path)))
    md = to_markdown(bundle)
    assert md.startswith(f"# {tmp_path.name}\n")
    assert "code_verdicts:" in md
    assert "## Assertions" in md
    assert "requests" in md
    assert "README.md:3-3" in md
    assert "DOC_DRIFT" not in md
    assert "doc_consistency" not in md
    # a finding-free repo still renders without a findings section
    assert "## Findings" not in md


def test_markdown_findings_section(tmp_path: Path) -> None:
    root = _mini_repo(tmp_path)
    (root / "README.md").write_text(
        _english_readme("The project references the missing `src/ghost.py` file.\n")
    )
    bundle = to_bundle(analyze_repository(root))
    md = to_markdown(bundle)
    assert "## Findings (REFUTED, document order, 1)" in md
    assert "**PATH_EXISTS** src/ghost.py README.md:3-3" in md
    # The triage score does not rank true findings, so it is not shown.
    assert "score" not in bundle["findings"][0]
    assert "predicted_class" not in bundle["findings"][0]


def test_bundle_roundtrip_render_from_disk(tmp_path: Path) -> None:
    root = _mini_repo(tmp_path)
    out = tmp_path / "bundle.json"
    out.write_text(
        json.dumps(to_bundle(analyze_repository(root)), ensure_ascii=False), encoding="utf-8"
    )
    loaded = json.loads(out.read_text(encoding="utf-8"))
    md = to_markdown(loaded)
    assert "## Assertions" in md
