"""Document-local module context for SYMBOL_EXISTS (trial rule).

Natural API-reference docs name a module once (a section heading, a table row,
a prose lead-in) and then use bare member names (``### `Reading` ``,
``- `scale_quantity` returns …``). The scan qualifies such a bare name with the
module the document itself supplies (``gaugekit.models.reading``); without a
document module the name stays bare, and a bare name can never REFUTE.
"""

from __future__ import annotations

from pathlib import Path

from docassay.core.models import Context
from docassay.core.pipeline import analyze_repository
from docassay.evidence.symbols import SymbolEvidence
from docassay.predicates.structure import symbol_exists_match, symbol_exists_scan

PROJECT_MODULES = frozenset(
    {
        "gaugekit.loader",
        "gaugekit.models",
        "palette.harmony",
        "plotline.canvas",
        "plotline.scales",
        "sheetmusic.parser",
    }
)
TOP_PACKAGES = frozenset({"gaugekit", "palette", "plotline", "sheetmusic"})


def _scan(text: str) -> list:
    return symbol_exists_scan(
        text,
        "api.md",
        project_modules=PROJECT_MODULES,
        top_packages=TOP_PACKAGES,
    )


def _objects(text: str) -> set[str]:
    return {claim.object for claim in _scan(text)}


# --- module-heading context ----------------------------------------------------


def test_module_heading_qualifies_bare_heading_name() -> None:
    objects = _objects("## `gaugekit.models`\n\n### `Reading`\n\nA single observation.\n")
    assert "gaugekit.models.reading" in objects
    assert "reading" not in objects


def test_module_heading_qualifies_signature_heading() -> None:
    objects = _objects(
        "## `gaugekit.loader`\n\n### `read_station_id() -> str`\n\nReturns the identifier.\n"
    )
    assert "gaugekit.loader.read_station_id" in objects


def test_nested_heading_inherits_section_module() -> None:
    objects = _objects(
        "## `plotline.scales`\n\n### `nice_ticks() -> list[float]`\n\nRound tick values.\n"
    )
    assert "plotline.scales.nice_ticks" in objects


def test_kind_prefix_is_stripped_before_anchoring() -> None:
    objects = _objects("## `plotline.canvas`\n\n### `class Canvas`\n\nA drawing surface.\n")
    assert "plotline.canvas.canvas" in objects
    assert "plotline.canvas.class canvas" not in objects


def test_prose_call_under_module_heading_is_qualified() -> None:
    objects = _objects(
        "## `plotline.canvas`\n\n"
        "### `class Canvas`\n\n"
        "A drawing surface. `Canvas()` takes no arguments.\n"
    )
    assert "plotline.canvas.canvas" in objects


def test_new_top_level_heading_closes_module_context() -> None:
    objects = _objects(
        "## `gaugekit.models`\n\n### `Reading`\n\n## Notes\n\n### `Ghost`\n\nA stray heading.\n"
    )
    assert "gaugekit.models.reading" in objects
    assert "ghost" in objects
    assert "gaugekit.models.ghost" not in objects


def test_prose_bare_identifier_under_heading_stays_bare() -> None:
    # A return-type mention must not be qualified into the module namespace:
    # ``Chord`` is defined in ``sheetmusic.models``, not ``sheetmusic.parser``.
    objects = _objects(
        "## `sheetmusic.parser`\n\nDeclared to parse a chord into a `Chord`. Takes no parameters.\n"
    )
    assert "chord" in objects
    assert "sheetmusic.parser.chord" not in objects


def test_builtin_literal_is_not_anchored() -> None:
    objects = _objects("## `sheetmusic.parser`\n\nThe body returns `None`.\n")
    assert "none" not in objects
    assert "sheetmusic.parser.none" not in objects


# --- same-line module / path context ------------------------------------------


def test_table_row_module_qualifies_bare_name() -> None:
    text = (
        "| Piece | Module | Role |\n"
        "|---|---|---|\n"
        "| `Canvas` | `plotline.canvas` | Drawing size and background. |\n"
    )
    assert "plotline.canvas.canvas" in _objects(text)


def test_same_line_module_qualifies_prose_bare_name() -> None:
    objects = _objects("The `sheetmusic.parser` module declares `parse_chord` (returns `Chord`).\n")
    assert "sheetmusic.parser.parse_chord" in objects
    # The return-type mention later on the line is not the documented subject.
    assert "sheetmusic.parser.chord" not in objects


def test_same_line_module_path_qualifies_prose_bare_name() -> None:
    objects = _objects(
        "`palette/harmony.py` provides `generate_palette`, which is annotated to return a list.\n"
    )
    assert "palette.harmony.generate_palette" in objects


def test_same_line_foreign_module_does_not_qualify() -> None:
    objects = _objects("The `requests.sessions` module provides `Session`.\n")
    assert "session" in objects
    assert "requests.sessions.session" not in objects


def test_same_line_usage_relation_does_not_qualify() -> None:
    # A module that *uses* a helper does not own it: "module uses X" is a
    # relationship, not a membership declaration.
    objects = _objects("`gaugekit.loader` uses `Reading` internally.\n")
    assert "reading" in objects
    assert "gaugekit.loader.reading" not in objects


# --- no module context: bare, never qualified ---------------------------------


def test_bare_name_without_module_context_stays_bare() -> None:
    objects = _objects("- `scale_quantity` returns a single quantity as a `float`.\n")
    assert "scale_quantity" in objects
    assert not any(obj.endswith(".scale_quantity") for obj in objects)


def test_dotted_and_path_tokens_are_not_qualified() -> None:
    objects = _objects(
        "## `gaugekit.loader`\n\nImport `gaugekit.loader.load_csv` or read `palette/harmony.py`.\n"
    )
    assert "gaugekit.loader.load_csv" in objects
    assert "gaugekit.loader.gaugekit.loader.load_csv" not in objects
    assert not any(obj.startswith("gaugekit.loader.palette") for obj in objects)


def test_placeholder_segment_is_not_qualified() -> None:
    objects = _objects("## `gaugekit.loader`\n\n### `foo`\n")
    assert "gaugekit.loader.foo" not in objects


def test_scan_without_module_inventory_keeps_legacy_behaviour() -> None:
    text = "## `gaugekit.models`\n\n### `Reading`\n"
    legacy = {claim.object for claim in symbol_exists_scan(text, "api.md")}
    assert "gaugekit.models" in legacy
    assert "gaugekit.models.reading" not in legacy


def test_negated_bare_name_with_evidence_is_not_refuted() -> None:
    evidence = {
        "demo.types.date": [
            SymbolEvidence(
                evidence_id="field:demo.types.date:demo/types.py:1",
                name="demo.types.date",
                kind="field",
                qualified_name="demo.types.date",
                source_file="demo/types.py",
                line=1,
            )
        ]
    }
    verdict = symbol_exists_match("date", Context(polarity=frozenset({"not"})), evidence)
    assert verdict.outcome == "NEI"


# --- end-to-end pipeline verdicts ---------------------------------------------


def _write_project(root: Path) -> None:
    (root / "demo").mkdir(parents=True)
    (root / "demo" / "__init__.py").write_text("")
    (root / "demo" / "loader.py").write_text("def read_station_id() -> str:\n    return ''\n")
    (root / "demo" / "models.py").write_text("class Reading:\n    pass\n")
    (root / "demo" / "types.py").write_text('date = "date"\n')


def _readme(body: str) -> str:
    return "# Demo project\nThis is the demo project that many teams use every day.\n" + body


def test_pipeline_qualifies_contextual_heading_and_supports(tmp_path: Path) -> None:
    _write_project(tmp_path)
    (tmp_path / "README.md").write_text(
        _readme("## `demo.loader`\n\n### `read_station_id() -> str`\n\nReturns the identifier.\n")
    )
    result = analyze_repository(tmp_path)
    refs = {r.object: r for r in result.referents if r.predicate_type == "SYMBOL_EXISTS"}
    assert refs["demo.loader.read_station_id"].assertions[0].code_verdict == "SUPPORTED"


def test_pipeline_qualified_missing_member_is_refuted(tmp_path: Path) -> None:
    _write_project(tmp_path)
    (tmp_path / "README.md").write_text(
        _readme("## `demo.loader`\n\n### `absent_member() -> str`\n\nReturns a value.\n")
    )
    result = analyze_repository(tmp_path)
    refs = {r.object: r for r in result.referents if r.predicate_type == "SYMBOL_EXISTS"}
    assert refs["demo.loader.absent_member"].assertions[0].code_verdict == "REFUTED"


def test_pipeline_bare_name_without_module_context_is_never_refuted(tmp_path: Path) -> None:
    _write_project(tmp_path)
    (tmp_path / "README.md").write_text(_readme("## Notes\n\n- `ghost_symbol` returns a value.\n"))
    result = analyze_repository(tmp_path)
    refs = {r.object: r for r in result.referents if r.predicate_type == "SYMBOL_EXISTS"}
    assert "ghost_symbol" in refs
    assert refs["ghost_symbol"].assertions[0].code_verdict == "NEI"
    assert not any(
        assertion.code_verdict == "REFUTED"
        for referent in result.referents
        for assertion in referent.assertions
    )


def test_pipeline_negated_bare_name_does_not_refute(tmp_path: Path) -> None:
    # A list item ("JSON has no `date` …") anchors a bare name; even when a
    # project symbol shares the last segment, a bare negation is not a
    # CLOSED-world contradiction.
    _write_project(tmp_path)
    (tmp_path / "README.md").write_text(
        _readme("## Notes\n\n1. JSON has no `date` or tuple types.\n")
    )
    result = analyze_repository(tmp_path)
    refs = {r.object: r for r in result.referents if r.predicate_type == "SYMBOL_EXISTS"}
    assert "date" in refs
    assert refs["date"].assertions[0].code_verdict == "NEI"
