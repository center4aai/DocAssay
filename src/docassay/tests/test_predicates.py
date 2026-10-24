"""Tests for the predicate plugin architecture (extensibility of §3/§4/§6)."""

from __future__ import annotations

import dataclasses
import re
from dataclasses import dataclass
from pathlib import Path

from docassay.core.models import Context, PredicateClaim
from docassay.core.pipeline import analyze_repository
from docassay.markers.context import extract_contexts
from docassay.predicates import ALL_PREDICATES
from docassay.predicates.base import Predicate, Verdict
from docassay.predicates.dependency import dependency_predicate
from docassay.vocabularies.markers import NEGATION_WORDS

# --- a minimal second predicate: TOOL_EXISTS ----------------------------------
#
# Proves the plugin contract: own vocabulary, own evidence source (tools.txt),
# own presence/negation matching. No versions, no downgrade flags.


_TOOL_NAMES = frozenset({"alpha", "beta", "gamma"})
_TOOL_ANCHOR = re.compile(
    r"(?<![a-z0-9_-])(?:"
    + "|".join(re.escape(n) for n in sorted(_TOOL_NAMES, key=len, reverse=True))
    + r")(?![a-z0-9_-])",
    re.IGNORECASE,
)


@dataclass(frozen=True, slots=True)
class ToolEvidence:
    evidence_id: str
    object: str
    source_file: str


def tool_scan(text: str, source: str) -> list[PredicateClaim]:
    low = text.lower()
    matches = list(_TOOL_ANCHOR.finditer(low))
    anchors = [(m.start(), m.end(), m.group(0)) for m in matches]
    contexts = extract_contexts(text, anchors, is_plausible=lambda n, v: False)
    claims: list[PredicateClaim] = []
    for m in matches:
        claims.append(
            PredicateClaim(
                claim_id=f"{source}:{m.start()}",
                source=source,
                predicate_type="TOOL_EXISTS",
                object=m.group(0).lower(),
                raw_context=text,
                context=contexts[m.start()],
            )
        )
    return claims


def tool_harvest(project_root: Path) -> list[ToolEvidence]:
    path = project_root / "tools.txt"
    if not path.exists():
        return []
    return [
        ToolEvidence(evidence_id=f"{name}:tools.txt", object=name, source_file="tools.txt")
        for name in path.read_text(encoding="utf-8").splitlines()
        if name.strip()
    ]


def tool_match(object: str, context: Context, evidence_by_name: dict, **flags) -> Verdict:
    evidence = evidence_by_name.get(object, [])
    negative = bool(context.polarity & NEGATION_WORDS)
    if negative:
        if evidence:
            return Verdict("REFUTED", (), tuple(e.evidence_id for e in evidence))
        return Verdict("NEI", layer="WORLD", reason="negation with no evidence")
    if evidence:
        return Verdict("SUPPORTED", tuple(e.evidence_id for e in evidence))
    return Verdict("NEI", layer="WORLD", reason="not in config inventory")


tool_predicate = Predicate(
    name="TOOL_EXISTS",
    world="closed-over-config",
    scan=tool_scan,
    harvest=tool_harvest,
    match=tool_match,
)


def _english_readme(body: str) -> str:
    return "# Demo project\nThis is the demo project that many teams use every day.\n" + body


# --- registry -----------------------------------------------------------------


def test_registry_contains_dependency() -> None:
    assert any(p.name == "DEPENDENCY" for p in ALL_PREDICATES)


# --- a second predicate end-to-end --------------------------------------------


def test_stub_predicate_end_to_end(tmp_path: Path) -> None:
    (tmp_path / "tools.txt").write_text("alpha\n")
    (tmp_path / "README.md").write_text(
        _english_readme("The project builds on the alpha framework.\n")
    )
    result = analyze_repository(tmp_path, plugins=(tool_predicate,))
    assert result.scanned_documents == 1
    assert len(result.evidence) == 1
    by_object = {ref.object: ref for ref in result.referents}
    assert set(by_object) == {"alpha"}
    alpha = by_object["alpha"]
    assert alpha.predicate_type == "TOOL_EXISTS"
    assert alpha.assertions[0].code_verdict == "SUPPORTED"
    assert alpha.assertions[0].evidence_sources == ("tools.txt",)


def test_stub_predicate_absent_evidence_is_nei(tmp_path: Path) -> None:
    (tmp_path / "tools.txt").write_text("alpha\n")
    (tmp_path / "README.md").write_text(_english_readme("No tool is used here.\n"))
    result = analyze_repository(tmp_path, plugins=(tool_predicate,))
    assert {ref.object for ref in result.referents} == set()


def test_stub_predicate_negation_with_evidence(tmp_path: Path) -> None:
    (tmp_path / "tools.txt").write_text("alpha\nbeta\n")
    (tmp_path / "README.md").write_text(
        _english_readme("The project does not use beta in production.\n")
    )
    result = analyze_repository(tmp_path, plugins=(tool_predicate,))
    beta = next(ref for ref in result.referents if ref.object == "beta")
    assert beta.assertions[0].code_verdict == "REFUTED"


def test_world_holds_evaluated_once_per_predicate(tmp_path: Path) -> None:
    # ``world_holds`` walks the tree, so it must be evaluated once per predicate,
    # not once per referent (which made adjudication O(referents × tree size)).
    (tmp_path / "tools.txt").write_text("alpha\nbeta\ngamma\n")
    (tmp_path / "README.md").write_text(
        _english_readme("The project uses alpha, beta and gamma.\n")
    )
    calls: list[Path] = []

    def world_holds(root: Path) -> bool:
        calls.append(root)
        return True

    counting = dataclasses.replace(tool_predicate, world_holds=world_holds)
    result = analyze_repository(tmp_path, plugins=(counting,))
    assert len(result.referents) == 3
    assert len(calls) == 1


# --- coexistence with the dependency predicate --------------------------------


def test_predicates_coexist(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "demo"\nrequires-python = ">=3.10"\ndependencies = ["sqlalchemy>=2.0"]\n'
    )
    (tmp_path / "tools.txt").write_text("alpha\n")
    (tmp_path / "README.md").write_text(
        _english_readme(
            "The project uses SQLAlchemy and the alpha framework. It requires "
            "Python 3.10 or higher and is tested on Linux.\n"
        )
    )
    result = analyze_repository(tmp_path, plugins=(dependency_predicate, tool_predicate))
    predicate_types = {ref.predicate_type for ref in result.referents}
    assert predicate_types == {"DEPENDENCY", "TOOL_EXISTS"}
    assert any(
        ref.object == "sqlalchemy" and ref.predicate_type == "DEPENDENCY"
        for ref in result.referents
    )
    assert any(
        ref.object == "alpha" and ref.predicate_type == "TOOL_EXISTS" for ref in result.referents
    )


# --- extract_contexts vocabulary parametrization ------------------------------


def test_extract_contexts_custom_plausibility() -> None:
    anchors = [(0, 3, "foo")]
    default = extract_contexts("foo 3.10", anchors)
    assert default[0].version == "==3.10"
    no_versions = extract_contexts("foo 3.10", anchors, is_plausible=lambda n, v: False)
    assert no_versions[0].version is None
