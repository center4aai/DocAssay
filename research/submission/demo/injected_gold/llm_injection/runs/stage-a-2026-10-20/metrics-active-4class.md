# Stage A — active four-class metrics

Source: combined `stage-a-s1-active` + `stage-a-s23-active` manifests
(`value-drift` historical entries excluded). Four repos × four active classes ×
three seeds. These are the numbers used in `report.md` §5.

## Overall

| outcome | count | rate | 95% CI |
|---|---:|---:|---|
| refuted | 18/32 | **0.5625** | [0.393, 0.718] |
| NEI (claim formed, abstained) | 10/32 | **0.3125** | [0.180, 0.486] |
| none (no claim formed) | 4/32 | **0.125** | [0.050, 0.281] |
| all attempts (end-to-end refutation) | 18/48 | 0.375 | [0.252, 0.516] |

`NEI` is a deliberate abstention, not a failure. `refuted + NEI + none = 32`.

## Per class

| class | verified | refuted | NEI | none | refutation | abstention | extraction miss |
|---|---:|---:|---:|---:|---:|---:|---:|
| path-location-drift | 10 | 10 | 0 | 0 | 1.000 | 0.000 | 0.000 |
| external-dependency-drift | 9 | 7 | 0 | 2 | 0.778 | 0.000 | 0.222 |
| identifier-drift | 8 | 1 | 6 | 1 | 0.125 | 0.750 | 0.125 |
| removed-referent-drift | 5 | 0 | 4 | 1 | 0.000 | 0.800 | 0.200 |
| **total** | **32** | **18** | **10** | **4** | **0.5625** | **0.3125** | **0.125** |

## Per claim form

| claim form | verified | refuted | NEI | none |
|---|---:|---:|---:|---:|
| path | 10 | 10 | 0 | 0 |
| dependency | 9 | 7 | 0 | 2 |
| qualified symbol | 1 | 1 | 0 | 0 |
| bare call (`name()`) | 9 | 0 | 9 | 0 |
| bare symbol | 3 | 0 | 1 | 2 |
| **total** | **32** | **18** | **10** | **4** |

## Per seed

| seed | verified | refuted | NEI | none |
|---|---:|---:|---:|---:|
| 1 | 11 | 6 | 3 | 2 |
| 2–3 | 21 | 12 | 7 | 2 |

## Historical value-drift

`value-drift` was removed from the active scope after Stage A. Its historical
12 verified entries were 3 refuted / 9 no-claim under the old VERSION predicate;
they are excluded from the active totals above.

## Baseline note

The Stage A baseline had 0 REFUTED on all four synthetic repos. This is not a
precision result; see `baseline_evidence.md` for real-repo baseline counts
(bitsandbytes 34, fastapi 62, pydantic 29) and examples of baseline false
positives. A 0-REFUTED acceptance gate is circular and has been replaced by a
diagnostic `baseline-report`.
