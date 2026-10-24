"""Stratified precision estimation (measurement without a full census).

Reviewing every resolved assertion is infeasible on large repositories (hundreds
of REFUTED per repo). Instead the review effort concentrates on two disjoint
surfaces:

- the top-K findings by score (finding quality — see ``report``), and
- a stratified random sample per (predicate, verdict-bucket, negation) stratum
  (measurement).

The sample is small (a few items per stratum), seeded and deterministic; each
reviewed item is labelled correct/incorrect by a human, and a stratified ratio
estimate of ``precision@resolved`` with a normal-approximation interval is
pooled over the stratum sizes. This is the honest estimator for the paper's
precision numbers without a line-by-line census.
"""

from __future__ import annotations

import math
import random
from collections.abc import Iterable

from docassay.triage import taxonomy
from docassay.triage.findings import Finding


def verdict_bucket(finding: Finding) -> str:
    """Coarse verdict bucket used as a stratum dimension.

    SUPPORTED items form one bucket; REFUTED items split into the predicted
    systematic-noise classes and the true-candidate residual, because those have
    very different base precision.
    """
    if finding.verdict == "SUPPORTED":
        return "SUPPORTED"
    if finding.predicted_class in taxonomy.SYSTEMATIC_NOISE:
        return "SYSTEMATIC"
    return "TRUE_CANDIDATE"


def stratum_key(finding: Finding) -> tuple[str, str, bool]:
    """Stratum of a resolved finding: (predicate, bucket, is_negative)."""
    return (
        finding.predicate,
        verdict_bucket(finding),
        bool(finding.signals.get("is_negative", False)),
    )


def build_strata(items: Iterable[Finding]) -> dict[tuple[str, str, bool], list[Finding]]:
    """Group resolved items into strata (deterministic order)."""
    strata: dict[tuple[str, str, bool], list[Finding]] = {}
    for item in items:
        if not item.is_resolved:
            continue
        key = stratum_key(item)
        strata.setdefault(key, []).append(item)
    for group in strata.values():
        group.sort(key=lambda f: f.finding_id)
    return strata


def sample_from_strata(
    strata: dict[tuple[str, str, bool], list[Finding]],
    per_stratum: int,
    seed: int = 0,
) -> dict[tuple[str, str, bool], list[Finding]]:
    """Deterministic random sample of ``per_stratum`` items per stratum."""
    rng = random.Random(seed)
    return {
        key: rng.sample(group, min(per_stratum, len(group)))
        for key, group in sorted(strata.items())
    }


def wilson_interval(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson score interval for a proportion ``k/n``."""
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    z2 = z * z
    denom = 1 + z2 / n
    centre = (p + z2 / (2 * n)) / denom
    margin = z * math.sqrt((p * (1 - p) + z2 / (4 * n)) / n) / denom
    return (max(0.0, centre - margin), min(1.0, centre + margin))


def stratified_estimate(
    stratum_sizes: dict[tuple[str, str, bool], int],
    stratum_reviewed: dict[tuple[str, str, bool], int],
    stratum_correct: dict[tuple[str, str, bool], int],
    z: float = 1.96,
) -> tuple[float, tuple[float, float], int, int]:
    """Stratified ratio estimate of precision with a normal-approx interval.

    Only strata with at least one reviewed item contribute their sampled
    proportion; unreviewed strata fall back to their population share times an
    uninformative interval (conservative).
    """
    keys = [k for k in stratum_sizes if stratum_sizes[k] > 0]
    total = sum(stratum_sizes[k] for k in keys)
    if total == 0:
        return (0.0, (0.0, 1.0), 0, 0)

    estimate = 0.0
    variance = 0.0
    reviewed_total = 0
    for k in keys:
        n = stratum_sizes[k]
        share = n / total
        r = stratum_reviewed.get(k, 0)
        c = stratum_correct.get(k, 0)
        reviewed_total += r
        if r == 0:
            estimate += share * 0.5
            variance += share * share * (0.25 / 4)
            continue
        p = c / r
        estimate += share * p
        variance += share * share * (p * (1 - p) / max(r - 1, 1))

    std = math.sqrt(variance)
    ci = (max(0.0, estimate - z * std), min(1.0, estimate + z * std))
    return estimate, ci, reviewed_total, total
