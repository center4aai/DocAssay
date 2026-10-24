"""LICENSE predicate: extraction and matching.

The license comes from the manifest's license field plus the ``LICENSE`` file.
The world is CLOSED over that inventory: a declared license makes a mismatched
claim refutable.

Extraction is anchor-first. LICENSE anchors on a closed allowlist of license
names inside a license-context window ("licensed under", "the ... license"),
with the bare ``Apache`` name deliberately skipped (``Apache Airflow`` /
``Superset`` are project names, not licenses).
"""

from __future__ import annotations

import re

from docassay.core.models import Context, PredicateClaim
from docassay.core.windows import anchor_line_text, iter_windows, line_at
from docassay.data import load_list, regex_alternation
from docassay.evidence.project import (
    LicenseEvidence,
    build_license_inventory,
    canonical_license,
    has_license_inventory,
)
from docassay.markers.context import extract_contexts
from docassay.predicates.base import GateResult, Predicate, Verdict
from docassay.vocabularies.markers import NEGATION_WORDS, is_historical_mention

LICENSE_PREDICATE = "LICENSE"
LICENSE_WORLD = "closed-over-field-and-file"

# License-context words gate the LICENSE anchors. (data/project.json)
_LICENSE_CTX_RE = re.compile(
    r"\b(?:" + regex_alternation(load_list("project.json", "license_context_words")) + r")\b",
    re.IGNORECASE,
)
_LICENSE_NAME_RE = re.compile(
    r"\b(?:"
    + regex_alternation(load_list("project.json", "license_names"))
    + r")(?:-?v?[0-9]+(?:\.[0-9]+)*)?\b",
    re.IGNORECASE,
)

# "Apache License, Version 2.0" — the version sits three tokens past the anchor
# (beyond the shared context-marker radius), so it is folded into the object
# directly.
_LICENSE_VERSION_TAIL_RE = re.compile(r"\bversion\s+(?:v)?\s*([0-9]+(?:\.[0-9]+)*)", re.IGNORECASE)


def _plausible_major(_name: str, num: str) -> bool:
    """Whether ``num`` is a plausible version major (0..99)."""
    try:
        major = int(num.split(".")[0])
    except ValueError:
        return False
    return 0 <= major <= 99


# --- LICENSE -----------------------------------------------------------------


def license_scan(text: str, source: str) -> list[PredicateClaim]:
    """Anchor-first scan of one document → LICENSE claims.

    A license-name anchor is a claim only inside a license-context window. The
    claim object is the canonical license name (§7.1), so a "MIT" claim and an
    "Apache-2.0" claim are separate referents and a mismatched claim refutes
    against the declared license. A bare ``apache`` mention (no version) is
    deliberately skipped: "Apache Airflow"/"Apache Superset" are project names.
    """
    claims: list[PredicateClaim] = []
    for line_idx, (window, line_start, _line_end, line_map) in enumerate(iter_windows(text)):
        if not _LICENSE_CTX_RE.search(window):
            continue
        anchors = [(m.start(), m.end(), m.group(0)) for m in _LICENSE_NAME_RE.finditer(window)]
        if not anchors:
            continue
        contexts = extract_contexts(
            window,
            anchors,
            normalize=lambda name: name.lower(),
            is_plausible=_plausible_major,
            line_map=line_map,
        )
        for start, end, token in anchors:
            version = contexts[start].version
            if version is None:
                tail = window[end : end + 40]
                m = _LICENSE_VERSION_TAIL_RE.search(tail)
                if m:
                    version = f"=={m.group(1)}"
            object_name = canonical_license(token, version)
            if object_name == "apache":
                continue  # bare Apache is a project name, not a license
            claims.append(
                PredicateClaim(
                    claim_id=f"{source}:{line_idx}:{start}",
                    source=source,
                    predicate_type=LICENSE_PREDICATE,
                    object=object_name,
                    raw_context=anchor_line_text(window, line_map, start),
                    context=contexts[start],
                    anchor_type="license-name",
                    line_start=line_at(line_map, start, line_start),
                    line_end=line_at(line_map, end - 1, line_start),
                )
            )
    return claims


# A license claim whose context attributes the license to a *third party*
# ("parts adapted from projectx, which is licensed under the Apache License")
# is not a claim about the project's own license. The cues
# live in ``data/project.json`` (``third_party_license_cues``).
_THIRD_PARTY_LICENSE_RE = re.compile(
    "(?:"
    + regex_alternation(load_list("project.json", "third_party_license_cues"), escape=False)
    + ")",
    re.IGNORECASE,
)


def license_flags(claim: PredicateClaim) -> dict[str, bool]:
    """Downgrade signals: historical or third-party attributed license mention."""
    return {
        "historical": is_historical_mention(claim.context, claim.raw_context),
        "third_party": bool(_THIRD_PARTY_LICENSE_RE.search(claim.raw_context)),
    }


def license_gate(claim: PredicateClaim) -> GateResult:
    """Whether a scan-produced license mention is a current-state claim."""
    if is_historical_mention(claim.context, claim.raw_context):
        return GateResult(False, "historical mention")
    return GateResult()


def _license_family_match(claimed: str, declared: str) -> bool:
    """Whether a declared license satisfies a claimed one.

    A versionless family claim ("GPL", "LGPL") is satisfied by any versioned
    member ("gpl-3.0", "lgpl-2.1") — the doc is under-specified but true
    .
    """
    if claimed == declared:
        return True
    return "-" not in claimed and declared.startswith(claimed + "-")


def match_license(
    object: str,
    context: Context,
    evidence_by_name: dict[str, list[LicenseEvidence]],
    *,
    historical: bool = False,
    third_party: bool = False,
) -> Verdict:
    """Verdict against the declared license (§6.1, CLOSED world).

    The claimed canonical license is present in the inventory → SUPPORTED;
    absent while a *different* license is declared → REFUTED (the README
    contradicts the manifest/LICENSE file). No license declared anywhere →
    NEI. Negation follows the §6.1 table (negative+evidence → REFUTED,
    negative∅ → NEI). A historical mention downgrades a would-be REFUTED; a
    third-party attribution is not a project claim → NEI.
    """
    evidence = list(evidence_by_name.get(object, []))
    if not evidence:
        for declared, items in evidence_by_name.items():
            if _license_family_match(object, declared):
                evidence.extend(items)
    negative = bool(context.polarity & NEGATION_WORDS)
    if negative:
        if evidence:
            return Verdict("REFUTED", (), _evidence_ids(evidence))
        return Verdict("NEI", layer="WORLD", reason="negation with no evidence")
    if evidence:
        return Verdict("SUPPORTED", _evidence_ids(evidence))
    if third_party:
        return Verdict("NEI", layer="CLAIM_GATE", reason="third-party attribution")
    if historical:
        return Verdict("NEI", layer="CLAIM_GATE", reason="historical mention")
    if evidence_by_name:
        return Verdict("REFUTED")
    return Verdict("NEI", layer="WORLD", reason="no license inventory")


def _evidence_ids(items) -> tuple[str, ...]:
    return tuple(e.evidence_id for e in items)


license_predicate = Predicate(
    name=LICENSE_PREDICATE,
    world=LICENSE_WORLD,
    scan=license_scan,
    harvest=build_license_inventory,
    match=match_license,
    flags=license_flags,
    gate=license_gate,
    world_holds=has_license_inventory,
)
