"""Tests for line-level provenance (line_start/line_end) on claims and evidence.

Covers the review §6.4 requirement: every claim and line-bound evidence fact
carries the 1-based source line it came from, for the demo's clickable
"doc line ↔ code/manifest line" transition (methodology §4).
"""

from __future__ import annotations

from pathlib import Path

from docassay.core.pipeline import analyze_repository
from docassay.core.windows import iter_windows, iter_windows_preserve_code, line_at
from docassay.evidence.listing import build_structure_inventory
from docassay.evidence.manifests import build_dependency_inventory
from docassay.evidence.symbols import build_symbol_inventory
from docassay.predicates.dependency import scan_document
from docassay.predicates.listing import path_exists_scan
from docassay.predicates.structure import symbol_exists_scan


def _english_readme(body: str) -> str:
    return "# Demo project\nThis is the demo project that many teams use every day.\n" + body


# --- windows -------------------------------------------------------------------


def test_windows_carry_1based_line_numbers() -> None:
    text = "line one\n\nline three\n```\ncode\n```\nline six\n"
    # Fence markers (```) are dropped, but the code line inside is a window.
    windows = list(iter_windows(text))
    assert windows == [
        ("line one", 1, 1, None),
        ("line three", 3, 3, None),
        ("code", 5, 5, None),
        ("line six", 7, 7, None),
    ]


def test_windows_skip_table_rows_keep_line_numbers() -> None:
    text = "head\n| a | b |\n\n| c | d |\ntail\n"
    windows = list(iter_windows(text))
    assert windows == [("head", 1, 1, None), ("tail", 5, 5, None)]


def test_long_line_split_shares_span() -> None:
    # A single over-160-char prose line splits into several sentence windows
    # that all keep the original line's number.
    text = "First sentence. " * 30
    windows = list(iter_windows(text))
    assert len(windows) > 1
    assert all(ls == 1 and le == 1 for _w, ls, le, _m in windows)


def test_windows_preserve_code_carries_spans() -> None:
    windows = list(iter_windows_preserve_code("first\n\n`src/a.py` here\n"))
    assert windows == [("first", 1, 1, None), ("`src/a.py` here", 3, 3, None)]


def test_table_header_cell_windows() -> None:
    # A requirements table pairs the column header with each data cell so the
    # version is extracted.
    text = "Requirements:\n| Python  | NumPy |\n|--------|-------|\n| 3.10+  | >=2.0 |\n"
    windows = list(iter_windows(text))
    assert ("Python 3.10+", 4, 4, None) in windows
    assert ("NumPy >=2.0", 4, 4, None) in windows


def test_sentence_fragment_merged_with_line_map() -> None:
    # A negation split across a line break stays one window and
    # the window carries a line map so each anchor keeps its physical line.
    windows = list(iter_windows("We do not\nrequire NumPy for this.\n"))
    assert len(windows) == 1
    window, start, end, line_map = windows[0]
    assert window == "We do not require NumPy for this."
    assert (start, end) == (1, 2)
    assert line_map is not None
    # The first line occupies offsets [0..8); "NumPy" starts on the second line.
    numpy_pos = window.find("NumPy")
    assert line_at(line_map, numpy_pos, 1) == 2
    assert line_at(line_map, 0, 1) == 1
    assert line_at(None, 0, 7) == 7


def test_merged_window_not_over_eager() -> None:
    # A complete line is NOT merged with the next sentence.
    windows = list(iter_windows("Python is supported.\nNew in 3.11.\n"))
    assert windows == [
        ("Python is supported.", 1, 1, None),
        ("New in 3.11.", 2, 2, None),
    ]


def test_negation_across_line_break_sets_anchor_line() -> None:
    # G3 from REPORT §6.1: "does not\nrequire NumPy" is a negation; the anchor
    # reports the physical line it sits on (2), not the window start (1).
    claims = scan_document("We do not\nrequire NumPy for requests.\n", "README.md")
    numpy = next(c for c in claims if c.object == "numpy")
    assert numpy.is_negative is True
    assert (numpy.line_start, numpy.line_end) == (2, 2)


# --- claims --------------------------------------------------------------------


def test_dependency_claim_provenance() -> None:
    text = _english_readme("First requirement line.\n\nThe project needs sqlalchemy>=2.0 here.\n")
    claims = scan_document(text, "README.md")
    sqlalchemy = next(c for c in claims if c.object == "sqlalchemy")
    assert (sqlalchemy.line_start, sqlalchemy.line_end) == (5, 5)


def test_path_claim_provenance_second_line() -> None:
    text = _english_readme("Line A.\n\nLine B: see `src/a.py` for details.\n")
    claims = path_exists_scan(text, "README.md")
    a_py = next(c for c in claims if c.object == "src/a.py")
    assert (a_py.line_start, a_py.line_end) == (5, 5)


def test_symbol_claim_provenance() -> None:
    text = _english_readme("Intro.\n\n`pkg.mod.Klass` is the main class.\n")
    claims = symbol_exists_scan(text, "README.md")
    klass = next(c for c in claims if c.object == "pkg.mod.klass")
    assert (klass.line_start, klass.line_end) == (5, 5)


def test_claim_id_unchanged_while_lines_added() -> None:
    # The middle claim_id segment stays the window ordinal; the physical line
    # number is carried separately in line_start/line_end.
    text = _english_readme("One.\n\nTwo: uses celery here.\n")
    claims = scan_document(text, "README.md")
    celery = next(c for c in claims if c.object == "celery")
    assert celery.claim_id.startswith("README.md:3:")
    assert (celery.line_start, celery.line_end) == (5, 5)


# --- evidence ------------------------------------------------------------------


def test_requirements_evidence_line_provenance(tmp_path: Path) -> None:
    (tmp_path / "requirements.txt").write_text(
        "# comment\nrequests==2.31.0\n\n--no-index\nnumpy>=1.24\n"
    )
    items = build_dependency_inventory(tmp_path)
    by_name = {e.package_name: e for e in items}
    assert (by_name["requests"].line_start, by_name["requests"].line_end) == (2, 2)
    assert (by_name["numpy"].line_start, by_name["numpy"].line_end) == (5, 5)


def test_pyproject_evidence_line_provenance(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        "[project]\n"
        'name = "demo"\n'
        'requires-python = ">=3.11"\n'
        "dependencies = [\n"
        '  "sqlalchemy>=2.0",\n'
        '  "celery>=5.0",\n'
        "]\n"
        "\n"
        "[project.optional-dependencies]\n"
        "dev = [\n"
        '  "pytest>=7.0",\n'
        '  "ruff>=0.6",\n'
        "]\n"
    )
    items = build_dependency_inventory(tmp_path)
    by_name = {e.package_name: e for e in items}
    assert (by_name["python"].line_start, by_name["python"].line_end) == (3, 3)
    assert (by_name["sqlalchemy"].line_start, by_name["sqlalchemy"].line_end) == (5, 5)
    assert (by_name["celery"].line_start, by_name["celery"].line_end) == (6, 6)
    assert (by_name["pytest"].line_start, by_name["pytest"].line_end) == (11, 11)
    assert (by_name["ruff"].line_start, by_name["ruff"].line_end) == (12, 12)


def test_symbol_evidence_line_span(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "mod.py").write_text("class Klass:\n    def run(self):\n        return 1\n")
    items = build_symbol_inventory(tmp_path)
    klass = next(e for e in items if e.qualified_name == "mod.Klass")
    assert (klass.line_start, klass.line_end) == (1, 3)
    run = next(e for e in items if e.qualified_name == "mod.Klass.run")
    assert (run.line_start, run.line_end) == (2, 3)


def test_path_evidence_file_line_start(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").write_text("x = 1\n")
    (tmp_path / "docs").mkdir()
    files = build_structure_inventory(tmp_path, kind="both")
    by_object = {e.object: e for e in files}
    assert (by_object["src/a.py"].line_start, by_object["src/a.py"].line_end) == (1, 1)
    # a directory is not tied to a text line.
    assert by_object["docs/"].line_start is None
    assert by_object["docs/"].line_end is None


# --- dump export ---------------------------------------------------------------


def test_dump_export_has_provenance(tmp_path: Path) -> None:
    import json

    from docassay.core.dump_claims import dump

    (tmp_path / "requirements.txt").write_text("requests==2.31.0\n")
    (tmp_path / "README.md").write_text(
        _english_readme("The project uses requests for the http client.\n")
    )
    out = tmp_path / "out.jsonl"
    dump(tmp_path, out)
    record = json.loads(out.read_text(encoding="utf-8").splitlines()[0])
    assert record["predicate"] == "DEPENDENCY"
    assert record["object"] == "requests"
    assert record["line_start"] == 3
    assert record["line_end"] == 3
    ev = record["evidence"]["requests:requirements.txt:==2.31.0"]
    assert ev == {
        "source_file": "requirements.txt",
        "line_start": 1,
        "line_end": 1,
        "snippet": "requests==2.31.0",
    }


def test_analyze_repository_claim_lines_pipeline(tmp_path: Path) -> None:
    (tmp_path / "requirements.txt").write_text("requests==2.31.0\n")
    (tmp_path / "README.md").write_text(
        _english_readme("Line one.\n\nThe project uses requests here.\n")
    )
    result = analyze_repository(tmp_path)
    claim = next(
        c
        for ref in result.referents
        for a in ref.assertions
        for c in a.claims
        if c.object == "requests"
    )
    assert (claim.line_start, claim.line_end) == (5, 5)
