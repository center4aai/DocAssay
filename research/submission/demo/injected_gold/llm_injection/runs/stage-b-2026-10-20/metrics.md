# Stage B — metrics

Three outcomes over **verified** injections: `refuted` / `nei` / `none`.
`nei` is a deliberate abstention, not a miss. The end-to-end table puts
declines and generator failures in the denominator.

## Injections (verified)

| outcome | count | rate |
|---|---:|---:|
| refuted | 35/72 | 0.486 |
| nei | 7/72 | 0.097 |
| none | 30/72 | 0.417 |

## Per class

| class | n | refuted | NEI | none | refutation | abstention | extraction miss |
|---|---:|---:|---:|---:|---:|---:|---:|
| external-dependency-drift | 18 | 14 | 0 | 4 | 0.778 | 0.000 | 0.222 |
| identifier-drift | 18 | 1 | 1 | 16 | 0.056 | 0.056 | 0.889 |
| path-location-drift | 18 | 18 | 0 | 0 | 1.000 | 0.000 | 0.000 |
| removed-referent-drift | 18 | 2 | 6 | 10 | 0.111 | 0.333 | 0.556 |

### `none` subtypes by class

| class | no_claim | other_referent | supported |
|---|---:|---:|---:|
| external-dependency-drift | 0 | 0 | 4 |
| identifier-drift | 9 | 6 | 1 |
| path-location-drift | 0 | 0 | 0 |
| removed-referent-drift | 7 | 2 | 1 |

## Per claim form

| claim form | n | refuted | NEI | none | refutation |
|---|---:|---:|---:|---:|---:|
| bare | 32 | 2 | 7 | 23 | 0.062 |
| bare_call | 3 | 0 | 0 | 3 | 0.000 |
| dependency | 18 | 14 | 0 | 4 | 0.778 |
| path | 18 | 18 | 0 | 0 | 1.000 |
| qualified | 1 | 1 | 0 | 0 | 1.000 |

## `none` subtypes

| subtype | count |
|---|---:|
| no_claim | 16 |
| other_referent | 8 |
| supported | 6 |

## Injector outcomes (all planned bundles)

| status | count |
|---|---:|
| verified | 72 |

These are the **final** statuses: 72/72 verified, 0 declines, 0 generator
failures. The pre-scoring harness/oracle fixes (55 → 70 → 72) are recorded
in `HARNESS_FIX.md`; no injector output was regenerated.

## End-to-end (all planned bundles)

| class | planned | refuted | NEI | none | end-to-end refutation |
|---|---:|---:|---:|---:|---:|
| external-dependency-drift | 18 | 14 | 0 | 4 | 0.778 |
| identifier-drift | 18 | 1 | 1 | 16 | 0.056 |
| path-location-drift | 18 | 18 | 0 | 0 | 1.000 |
| removed-referent-drift | 18 | 2 | 6 | 10 | 0.111 |
| **all** | 72 | 35 | 7 | 30 | 0.486 |

## Controls

| class | n | clean | refuted (FP) | NEI | none | precision |
|---|---:|---:|---:|---:|---:|---:|
| external-dependency-drift | 6 | 6 | 0 | 0 | 6 | 1.000 |
| identifier-drift | 6 | 6 | 0 | 0 | 6 | 1.000 |
| path-location-drift | 6 | 6 | 0 | 1 | 5 | 1.000 |
| **all** | 18 | 18 | 0 | 1 | 17 | 1.000 |

Control subtypes (non-refuted):

| subtype | count |
|---|---:|
| nei | 1 |
| no_claim | 2 |
| other_referent | 2 |
| supported | 13 |

## Cluster bootstrap (headline inference)

Repositories are resampled with replacement (10,000 replicates, fixed seed);
Wilson intervals are **not** used for the headline because injections cluster
within repositories.

| scope | outcome | point | 95% CI | clusters |
|---|---|---:|---|---:|
| all | refuted | 0.486 | [0.375, 0.611] | 6 |
| all | nei | 0.097 | [0.042, 0.167] | 6 |
| all | none | 0.417 | [0.278, 0.569] | 6 |
| external-dependency-drift | refuted | 0.778 | [0.444, 1.000] | 6 |
| external-dependency-drift | nei | 0.000 | [0.000, 0.000] | 6 |
| external-dependency-drift | none | 0.222 | [0.000, 0.556] | 6 |
| identifier-drift | refuted | 0.056 | [0.000, 0.167] | 6 |
| identifier-drift | nei | 0.056 | [0.000, 0.167] | 6 |
| identifier-drift | none | 0.889 | [0.778, 1.000] | 6 |
| path-location-drift | refuted | 1.000 | [1.000, 1.000] | 6 |
| path-location-drift | nei | 0.000 | [0.000, 0.000] | 6 |
| path-location-drift | none | 0.000 | [0.000, 0.000] | 6 |
| removed-referent-drift | refuted | 0.111 | [0.000, 0.333] | 6 |
| removed-referent-drift | nei | 0.333 | [0.111, 0.611] | 6 |
| removed-referent-drift | none | 0.556 | [0.222, 0.889] | 6 |

## Baseline findings

0 baseline `REFUTED` claim(s) recorded; see
`baseline_findings.json`. They are adjudicated separately as true documentation
bugs or tool false positives, never used to edit the corpus.
