# Stage C metrics

**KPI: `R_detect` — REFUTED or NEI on the same artifact counts as caught.** NEI is an explicit abstention with a mention, not silence; `none` (no claim / wrong SUPPORTED / other referent) is a miss. `R_credit` is REFUTED only; `R_target` is an attribution diagnostic. No Wilson interval is used.

## T2 — overall

| verified | detected (REFUTED+NEI) | R_detect (KPI) [CI] | REFUTED (R_credit) | NEI | none | R_target (attribution) [CI] |
|---|---|---|---|---|---|---|
| 69 | 65 | 0.942 [0.873, 0.9861] | 50 (0.725) | 15 | 4 | 0.565 [0.4762, 0.6389] |

## T3 — class

| value | n | detected | R_detect (KPI) | refuted | NEI | none | R_credit | R_target | cross-mention |
|---|---|---|---|---|---|---|---|---|---|
| external-dependency-drift | 15 | 15 | 1.0 | 15 | 0 | 0 | 1.0 | 1.0 | 0 |
| identifier-drift | 18 | 18 | 1.0 | 9 | 9 | 0 | 0.5 | 0.111 | 7 |
| path-location-drift | 18 | 14 | 0.778 | 14 | 0 | 4 | 0.778 | 0.778 | 0 |
| removed-referent-drift | 18 | 18 | 1.0 | 12 | 6 | 0 | 0.667 | 0.444 | 4 |

Every class is scored on `R_detect` (KPI: REFUTED + NEI). NEI is an explicit abstention with a mention and counts as caught; `none` (no claim / wrong SUPPORTED / other referent) is a miss. `R_target` is attribution only.

## T4 — claim form

| value | n | detected | R_detect (KPI) | refuted | NEI | none | R_credit | R_target | cross-mention |
|---|---|---|---|---|---|---|---|---|---|
| bare | 14 | 14 | 1.0 | 5 | 9 | 0 | 0.357 | 0.143 | 3 |
| bare_call | 4 | 4 | 1.0 | 4 | 0 | 0 | 1.0 | 0.0 | 4 |
| dependency | 15 | 15 | 1.0 | 15 | 0 | 0 | 1.0 | 1.0 | 0 |
| path | 20 | 16 | 0.8 | 15 | 1 | 4 | 0.75 | 0.7 | 1 |
| section_qualified | 16 | 16 | 1.0 | 11 | 5 | 0 | 0.688 | 0.5 | 3 |

## T5 — context source

| value | n | detected | R_detect (KPI) | refuted | NEI | none | R_credit | R_target | cross-mention |
|---|---|---|---|---|---|---|---|---|---|
| heading | 10 | 10 | 1.0 | 6 | 4 | 0 | 0.6 | 0.5 | 1 |
| list | 4 | 4 | 1.0 | 3 | 1 | 0 | 0.75 | 0.5 | 1 |
| none | 53 | 49 | 0.925 | 39 | 10 | 4 | 0.736 | 0.585 | 8 |
| prose | 2 | 2 | 1.0 | 2 | 0 | 0 | 1.0 | 0.5 | 1 |

## T6 — genre

| value | n | detected | R_detect (KPI) | refuted | NEI | none | R_credit | R_target | cross-mention |
|---|---|---|---|---|---|---|---|---|---|
| cookbook | 1 | 0 | 0.0 | 0 | 0 | 1 | 0.0 | 0.0 | 0 |
| explanation | 6 | 6 | 1.0 | 3 | 3 | 0 | 0.5 | 0.0 | 3 |
| how-to | 1 | 1 | 1.0 | 0 | 1 | 0 | 0.0 | 0.0 | 0 |
| module map | 3 | 3 | 1.0 | 2 | 1 | 0 | 0.667 | 0.667 | 0 |
| n/a | 41 | 38 | 0.927 | 33 | 5 | 3 | 0.805 | 0.683 | 5 |
| reference | 16 | 16 | 1.0 | 11 | 5 | 0 | 0.688 | 0.562 | 2 |
| tutorial | 1 | 1 | 1.0 | 1 | 0 | 0 | 1.0 | 0.0 | 1 |

## T7 — target document

| value | n | detected | R_detect (KPI) | refuted | NEI | none | R_credit | R_target | cross-mention |
|---|---|---|---|---|---|---|---|---|---|
| readme | 41 | 38 | 0.927 | 33 | 5 | 3 | 0.805 | 0.683 | 5 |
| reference_document | 22 | 22 | 1.0 | 13 | 9 | 0 | 0.591 | 0.5 | 2 |
| task_document | 6 | 5 | 0.833 | 4 | 1 | 1 | 0.667 | 0.0 | 4 |

## T8 — dependency phrasing

| value | n | detected | R_detect (KPI) | refuted | NEI | none | R_credit | R_target | cross-mention |
|---|---|---|---|---|---|---|---|---|---|
| inline_backticked | 15 | 15 | 1.0 | 15 | 0 | 0 | 1.0 | 1.0 | 0 |
| n/a | 54 | 50 | 0.926 | 35 | 15 | 4 | 0.648 | 0.444 | 11 |

## T8 — dependency form

| value | n | detected | R_detect (KPI) | refuted | NEI | none | R_credit | R_target | cross-mention |
|---|---|---|---|---|---|---|---|---|---|
| constraint_break | 15 | 15 | 1.0 | 15 | 0 | 0 | 1.0 | 1.0 | 0 |
| n/a | 54 | 50 | 0.926 | 35 | 15 | 4 | 0.648 | 0.444 | 11 |

## T7 — repo

| value | n | detected | R_detect (KPI) | refuted | NEI | none | R_credit | R_target | cross-mention |
|---|---|---|---|---|---|---|---|---|---|
| bibscan | 12 | 11 | 0.917 | 8 | 3 | 1 | 0.667 | 0.667 | 0 |
| contourkit | 12 | 11 | 0.917 | 6 | 5 | 1 | 0.5 | 0.417 | 1 |
| morpheme | 12 | 12 | 1.0 | 12 | 0 | 0 | 1.0 | 0.667 | 4 |
| sensorbus | 12 | 12 | 1.0 | 6 | 6 | 0 | 0.5 | 0.5 | 0 |
| serialscope | 12 | 12 | 1.0 | 11 | 1 | 0 | 0.917 | 0.667 | 3 |
| tileplan | 9 | 7 | 0.778 | 7 | 0 | 2 | 0.778 | 0.444 | 3 |

## T9 — end-to-end statuses

| planned | verified | declined | invalid | verify_failed | apply_failed | timeout | no_output | unresolved | conflict | refuted |
|---|---|---|---|---|---|---|---|---|---|---|
| 72 | 69 | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 50 |

## T10 — credited detection × target-line attribution

| class | credited refuted (KPI) | target-line refuted (attribution) | other-mention-only | both |
|---|---|---|---|---|
| external-dependency-drift | 15 | 15 | 0 | 3 |
| identifier-drift | 9 | 2 | 7 | 1 |
| path-location-drift | 14 | 14 | 0 | 7 |
| removed-referent-drift | 12 | 8 | 4 | 1 |

## T11 — controls

| family | required | evaluated | dropped | shortfall | extracted | refuted | specificity | precision (extracted) | extraction |
|---|---|---|---|---|---|---|---|---|---|
| A1 | 6 | 6 | 0 | 0 | 6 | 0 | 1.0 | 1.0 | 1.0 |
| A2 | 6 | 5 | 0 | 1 | 5 | 0 | 1.0 | 1.0 | 1.0 |
| A3 | 6 | 3 | 0 | 3 | 3 | 0 | 1.0 | 1.0 | 1.0 |
| A4 | 6 | 5 | 0 | 1 | 5 | 0 | 1.0 | 1.0 | 1.0 |
| B | 6 | 5 | 0 | 1 | 1 | 0 | 1.0 | 1.0 | 0.2 |
| C | 0 | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |

## T13 — effective sample size

| class | entries | distinct (repo, artifact) | collapsed targets | collapsed entries |
|---|---|---|---|---|
| external-dependency-drift | 15 | 7 | 5 | 13 |
| identifier-drift | 18 | 13 | 5 | 10 |
| path-location-drift | 18 | 11 | 6 | 13 |
| removed-referent-drift | 18 | 15 | 3 | 6 |

## T12 — baseline findings

0 baseline `REFUTED` claim(s); adjudication pending (see baseline_findings.json).

## T14 — annotation

Pending: no non-author annotator at sign-off (OPEN-C9). Engine-only provisional.

## T15 — deviations

- see deviations.md
