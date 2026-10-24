"""HAS_DOCKERFILE and HAS_CI_WORKFLOW predicates.

The infrastructure group's evidence is the project's own file listing — the
same CLOSED world as PATH_EXISTS. Extraction is anchor-first over capability
mentions: the ``Dockerfile`` name for the dockerfile referent, and CI product
names plus ``ci``/``ci/cd``/``continuous integration`` for the ``ci_workflow``
referent. A claim that a capability exists is refuted by its absence in the
tree (the CLOSED world turns a stale doc claim into a finding); generative
instructions ("add a Dockerfile"), examples and historical mentions downgrade
to NEI.
"""

from __future__ import annotations

import re

from docassay.core.models import Context, PredicateClaim
from docassay.core.windows import anchor_line_text, iter_windows, line_at
from docassay.data import load_list, regex_alternation
from docassay.evidence.infra import InfraEvidence, build_infra_inventory
from docassay.markers.context import extract_contexts
from docassay.predicates.base import GateResult, Predicate, Verdict, mention_gate_reason
from docassay.vocabularies.markers import NEGATION_WORDS, is_historical_mention

HAS_DOCKERFILE_PREDICATE = "HAS_DOCKERFILE"
HAS_CI_WORKFLOW_PREDICATE = "HAS_CI_WORKFLOW"
INFRA_WORLD = "closed-over-listing"

# The Dockerfile name is the precise capability claim ("we ship a Dockerfile",
# "the `Dockerfile` at the root"). A generic "docker image" mention is not an
# anchor — building a docker image does not imply a committed Dockerfile.
# A bare "Dockerfile" mention is NOT a claim either: how-to Docker tutorials
# discuss the *user's* Dockerfile ("your Dockerfile", "the Dockerfile below",
# "create a Dockerfile") without asserting that the documented project ships
# one. Only an assertive mention — an existence/possession verb or a repo
# location ("at the root", "in the repository") — anchors the capability claim.
_DOCKERFILE_RE = re.compile(r"\bDockerfiles?\b", re.IGNORECASE)
_DOCKERFILE_ASSERT_RE = re.compile(
    r"\b(?:at\s+the\s+(?:root|top)|comes?\s+with|in\s+the\s+(?:repo(?:sitory)?|tree)|"
    r"includ\w*|located\s+(?:in|at)|lives?\s+in|offers?|offered|present\s+in|"
    r"provid\w*|releas\w*|ships?|shipped|suppl\w*)\b",
    re.IGNORECASE,
)

# CI product names and bare "ci"/"ci/cd"/"continuous integration". (data/project.json)
_CI_NAMES: frozenset[str] = load_list("project.json", "ci_names")
_CI_CONTEXT_WORDS: frozenset[str] = load_list("project.json", "ci_context_words")
_CI_ANCHOR_RE = re.compile(r"\b(?:ci|ci/cd|" + regex_alternation(_CI_NAMES) + r")\b", re.IGNORECASE)
_CI_CONTEXT_RE = re.compile(r"\b(?:" + regex_alternation(_CI_CONTEXT_WORDS) + r")\b", re.IGNORECASE)

# Multi-word product names are unambiguous on their own; bare "ci" and the
# single-word tools need a CI context word in the window to be a claim.
_UNAMBIGUOUS_CI: frozenset[str] = frozenset(
    {
        "azure pipelines",
        "bitbucket pipelines",
        "continuous integration",
        "github actions",
        "gitlab ci",
        "travis ci",
    }
)

# Creation verbs make a mention an instruction ("add a Dockerfile", "set up a
# CI pipeline"). The generic generative pool is NOT reused wholesale: "runs" is
# the verb that *describes* a CI workflow ("our CI workflow runs tests"), and a
# descriptive mention is exactly the claim the predicate must adjudicate.
# (data/markers.json)
_INSTRUCTION_RE = re.compile(
    r"\b(?:add(?:ed|ing|s)?|configur\w*|creat\w*|defin\w*|enabl\w*|generat\w*|"
    r"install\w*|scaffold\w*|set\s+up|setup|writ\w*)\b",
    re.IGNORECASE,
)
_EXEMPLARY_RE = re.compile(
    r"\b(?:"
    + regex_alternation(load_list("markers.json", "exemplary_phrases"), escape=False)
    + r")\b|like\s*[`]",
    re.IGNORECASE,
)


def _scan_claims(
    text: str,
    source: str,
    predicate_type: str,
    object_name: str,
    anchors: list[tuple[int, int, str, str]],
    line_idx: int,
    line_start: int,
    line_map,
) -> list[PredicateClaim]:
    contexts = extract_contexts(
        text,
        [(s, e, t) for s, e, t, _a in anchors],
        is_plausible=lambda _n, _v: False,
        line_map=line_map,
    )
    claims: list[PredicateClaim] = []
    seen: set[tuple[str, str]] = set()
    for start, end, token, anchor_type in anchors:
        dedupe_key = (anchor_line_text(text, line_map, start), token)
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        claims.append(
            PredicateClaim(
                claim_id=f"{source}:{line_idx}:{start}",
                source=source,
                predicate_type=predicate_type,
                object=object_name,
                raw_context=anchor_line_text(text, line_map, start),
                context=contexts[start],
                anchor_type=anchor_type,
                line_start=line_at(line_map, start, line_start),
                line_end=line_at(line_map, end - 1, line_start),
            )
        )
    return claims


def dockerfile_scan(text: str, source: str) -> list[PredicateClaim]:
    """Anchor-first scan of one document → HAS_DOCKERFILE claims.

    Only assertive mentions anchor ("we ship a Dockerfile", "a Dockerfile is
    included at the root"). How-to tutorial mentions of the *user's* Dockerfile
    are not claims about the documented project and never anchor.
    """
    claims: list[PredicateClaim] = []
    for line_idx, (window, line_start, _line_end, line_map) in enumerate(iter_windows(text)):
        if not _DOCKERFILE_ASSERT_RE.search(window):
            continue
        anchors = [
            (m.start(), m.end(), m.group(0), "dockerfile") for m in _DOCKERFILE_RE.finditer(window)
        ]
        if not anchors:
            continue
        claims.extend(
            _scan_claims(
                window,
                source,
                HAS_DOCKERFILE_PREDICATE,
                "dockerfile",
                anchors,
                line_idx,
                line_start,
                line_map,
            )
        )
    return claims


def ci_workflow_scan(text: str, source: str) -> list[PredicateClaim]:
    """Anchor-first scan of one document → HAS_CI_WORKFLOW claims.

    A bare ``ci``/``ci/cd``/``continuous integration`` mention (or a single-word
    tool name) must sit in a CI context ("CI workflow", "runs GitHub Actions").
    Multi-word product names ("GitHub Actions", "GitLab CI") anchor on their own.
    """
    claims: list[PredicateClaim] = []
    for line_idx, (window, line_start, _line_end, line_map) in enumerate(iter_windows(text)):
        has_context = bool(_CI_CONTEXT_RE.search(window))
        anchors: list[tuple[int, int, str, str]] = []
        for m in _CI_ANCHOR_RE.finditer(window):
            token = m.group(0).lower()
            if token not in _UNAMBIGUOUS_CI and not has_context:
                continue
            anchor_type = "ci" if token in {"ci", "ci/cd"} else "product"
            anchors.append((m.start(), m.end(), token, anchor_type))
        if not anchors:
            continue
        claims.extend(
            _scan_claims(
                window,
                source,
                HAS_CI_WORKFLOW_PREDICATE,
                "ci_workflow",
                anchors,
                line_idx,
                line_start,
                line_map,
            )
        )
    return claims


def dockerfile_harvest(project_root) -> list[InfraEvidence]:
    return [e for e in build_infra_inventory(project_root) if e.kind == "dockerfile"]


def ci_harvest(project_root) -> list[InfraEvidence]:
    return [e for e in build_infra_inventory(project_root) if e.kind == "ci"]


def infra_flags(claim: PredicateClaim) -> dict[str, bool]:
    """Downgrade signals: historical, generative-instruction, example."""
    return {
        "historical": is_historical_mention(claim.context, claim.raw_context),
        "instructional": _sentence_initial_instruction(claim.raw_context, _INSTRUCTION_RE),
        "exemplary": bool(_EXEMPLARY_RE.search(claim.raw_context)),
    }


def infra_gate(claim: PredicateClaim) -> GateResult:
    """Whether a scan-produced capability mention is a current-state claim.

    The instructional signal is *sentence-initial* imperative ("Add a CI
    workflow"); a descriptive "our CI workflow runs tests" stays a claim.
    """
    if is_historical_mention(claim.context, claim.raw_context):
        return GateResult(False, "historical mention")
    if _sentence_initial_instruction(claim.raw_context, _INSTRUCTION_RE):
        return GateResult(False, "instructional mention")
    if _EXEMPLARY_RE.search(claim.raw_context):
        return GateResult(False, "exemplary mention")
    return GateResult()


def _sentence_initial_instruction(raw_context: str, regex: re.Pattern) -> bool:
    """Whether an imperative verb opens the window ("Add a CI workflow")."""
    low = raw_context.lstrip(" \t\n\r\"'`([{")
    return regex.match(low) is not None


def _presence_match(
    object: str,
    context: Context,
    evidence_by_name: dict[str, list[InfraEvidence]],
    flags: dict[str, bool],
) -> Verdict:
    """Presence verdict against the capability evidence (§6.1, CLOSED world).

    positive+evidence → SUPPORTED · negative+evidence → REFUTED ·
    negative∅ → NEI · positive∅ → REFUTED. An instruction, an example or a
    historical mention downgrades the would-be REFUTED to NEI.
    """
    evidence = evidence_by_name.get(object, [])
    negative = bool(context.polarity & NEGATION_WORDS)
    if negative:
        if evidence:
            return Verdict("REFUTED", (), _evidence_ids(evidence))
        return Verdict("NEI", layer="WORLD", reason="negation with no evidence")
    if evidence:
        return Verdict("SUPPORTED", _evidence_ids(evidence))
    if any(flags.values()):
        return Verdict("NEI", layer="CLAIM_GATE", reason=mention_gate_reason(**flags))
    return Verdict("REFUTED")


def match_dockerfile(
    object: str,
    context: Context,
    evidence_by_name: dict[str, list[InfraEvidence]],
    *,
    historical: bool = False,
    instructional: bool = False,
    exemplary: bool = False,
) -> Verdict:
    """Presence verdict against the Dockerfile evidence."""
    return _presence_match(
        "dockerfile",
        context,
        evidence_by_name,
        {"historical": historical, "instructional": instructional, "exemplary": exemplary},
    )


def match_ci_workflow(
    object: str,
    context: Context,
    evidence_by_name: dict[str, list[InfraEvidence]],
    *,
    historical: bool = False,
    instructional: bool = False,
    exemplary: bool = False,
) -> Verdict:
    """Presence verdict against the CI-config evidence."""
    return _presence_match(
        "ci_workflow",
        context,
        evidence_by_name,
        {"historical": historical, "instructional": instructional, "exemplary": exemplary},
    )


def _evidence_ids(items: list[InfraEvidence]) -> tuple[str, ...]:
    return tuple(e.evidence_id for e in items)


has_dockerfile_predicate = Predicate(
    name=HAS_DOCKERFILE_PREDICATE,
    world=INFRA_WORLD,
    scan=dockerfile_scan,
    harvest=dockerfile_harvest,
    match=match_dockerfile,
    flags=infra_flags,
    gate=infra_gate,
)

has_ci_workflow_predicate = Predicate(
    name=HAS_CI_WORKFLOW_PREDICATE,
    world=INFRA_WORLD,
    scan=ci_workflow_scan,
    harvest=ci_harvest,
    match=match_ci_workflow,
    flags=infra_flags,
    gate=infra_gate,
)
