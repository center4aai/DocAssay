"""Assertion grouping.

Claims group into an assertion when ``predicate_type``, ``object`` and
``domain`` match and their filled context markers do not contradict (§5.3).
"""

from __future__ import annotations

from collections import defaultdict

from docassay.core.models import Assertion, Context, PredicateClaim, ReferentResult


def group_into_assertions(claims: list[PredicateClaim]) -> list[ReferentResult]:
    """Cluster claims into assertions."""
    by_referent: dict[tuple[str, str, str], list[PredicateClaim]] = defaultdict(list)
    for claim in claims:
        by_referent[(claim.predicate_type, claim.object, claim.domain)].append(claim)

    results: list[ReferentResult] = []
    for (predicate_type, object, domain), referent_claims in sorted(by_referent.items()):
        clusters = _cluster_compatible(referent_claims)
        assertions = tuple(
            Assertion(
                predicate_type=predicate_type,
                object=object,
                domain=domain,
                claims=tuple(cluster),
                context=_merge_contexts(cluster),
            )
            for cluster in clusters
        )
        results.append(
            ReferentResult(
                predicate_type=predicate_type,
                object=object,
                domain=domain,
                assertions=assertions,
            )
        )
    return results


def _cluster_compatible(claims: list[PredicateClaim]) -> list[list[PredicateClaim]]:
    """Greedy, order-stable clustering by context compatibility (§5.3).

    Deterministic: claims are visited in ``claim_id`` order and join the first
    cluster whose filled markers do not contradict their own. A claim that
    carries a version never merges with a versionless claim: "X is used" and
    "X is used at version 1.2" are different assertions, and mixing them lets
    a versionless SUPPORTED mask an undecidable version question. A negated
    claim ("X is not used") never merges with a positive one: the empty
    ``polarity`` of a positive claim does not contradict ``{"not"}``, so without
    this guard one negation would flip the whole assertion to REFUTED.
    """
    ordered = sorted(claims, key=lambda c: c.claim_id)
    clusters: list[list[PredicateClaim]] = []
    cluster_contexts: list[Context] = []
    cluster_negative: list[bool] = []
    for claim in ordered:
        for idx, existing in enumerate(cluster_contexts):
            if (existing.version is None) != (claim.context.version is None):
                continue
            if cluster_negative[idx] != claim.is_negative:
                continue
            if not existing.conflicts_with(claim.context):
                clusters[idx].append(claim)
                cluster_contexts[idx] = existing.merged(claim.context)
                break
        else:
            clusters.append([claim])
            cluster_contexts.append(claim.context)
            cluster_negative.append(claim.is_negative)
    return clusters


def _merge_contexts(claims: list[PredicateClaim]) -> Context:
    merged = claims[0].context
    for claim in claims[1:]:
        merged = merged.merged(claim.context)
    return merged
