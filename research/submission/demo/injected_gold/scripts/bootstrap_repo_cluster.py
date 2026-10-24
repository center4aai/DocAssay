"""Repository-cluster percentile bootstrap for Stage C (no Wilson).

Stage C's 72 bundles are not independent Bernoulli trials: seeds repeat targets
within a repository. The primary interval therefore resamples the **six
repositories** with replacement (10,000 replicates, fixed seed), and the
leave-one-repo-out range is reported as a robustness check
(``validation/stage-c-plan.md`` §8.8, ``protocol.md`` §5 as amended).

Standard library only. Importable and runnable.
"""

from __future__ import annotations

import argparse
import json
import random
from collections import defaultdict


def _rate(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def percentile(values: list[float], p: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    index = (len(ordered) - 1) * p
    low = int(index)
    high = min(low + 1, len(ordered) - 1)
    weight = index - low
    return ordered[low] * (1 - weight) + ordered[high] * weight


def bootstrap_rate(
    entries: list[dict],
    field: str,
    value: str,
    *,
    replicates: int = 10000,
    seed: int = 20261020,
) -> dict | None:
    """Percentile CI over repository clusters for ``field == value``.

    ``entries`` need ``repo`` and ``field``. Returns the point estimate, the
    cluster count, the CI, and the leave-one-repo-out range.
    """
    by_repo: dict[str, list[float]] = defaultdict(list)
    for entry in entries:
        by_repo[entry["repo"]].append(1.0 if entry.get(field) == value else 0.0)
    repos = sorted(by_repo)
    if not repos:
        return None
    point = _rate([v for rows in by_repo.values() for v in rows])
    if point is None:
        return None
    rng = random.Random(seed)
    draws: list[float] = []
    for _ in range(replicates):
        sample = [rng.choice(repos) for _ in repos]
        draws.append(_rate([v for repo in sample for v in by_repo[repo]]) or 0.0)
    loo = []
    for repo in repos:
        rest = [v for other in repos if other != repo for v in by_repo[other]]
        loo.append(_rate(rest))
    return {
        "point": round(point, 4),
        "n_entries": sum(len(rows) for rows in by_repo.values()),
        "n_clusters": len(repos),
        "ci95": [round(percentile(draws, 0.025) or 0.0, 4),
                 round(percentile(draws, 0.975) or 0.0, 4)],
        "loo_min": round(min(v for v in loo if v is not None), 4) if any(loo) else None,
        "loo_max": round(max(v for v in loo if v is not None), 4) if any(loo) else None,
        "replicates": replicates,
        "seed": seed,
        "method": "repo-cluster percentile bootstrap; no Wilson",
        "degenerate": len(repos) < 2 or (point in (0.0, 1.0)),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--entries", required=True, help="JSON list with repo/outcome fields")
    ap.add_argument("--field", default="outcome")
    ap.add_argument("--value", default="refuted")
    ap.add_argument("--replicates", type=int, default=10000)
    ap.add_argument("--seed", type=int, default=20261020)
    args = ap.parse_args(argv)
    entries = json.load(open(args.entries, encoding="utf-8"))
    print(json.dumps(
        bootstrap_rate(entries, args.field, args.value,
                       replicates=args.replicates, seed=args.seed),
        indent=2,
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
