# Injected-gold metrics

- date: 2026-10-23
- seed: 0
- repos: bibscan__control, bibscan__external-dependency-drift__s1_0, bibscan__external-dependency-drift__s2_0, bibscan__external-dependency-drift__s3_0, bibscan__identifier-drift__s1_0, bibscan__identifier-drift__s2_0, bibscan__identifier-drift__s3_0, bibscan__path-location-drift__s1_0, bibscan__path-location-drift__s2_0, bibscan__path-location-drift__s3_0, bibscan__removed-referent-drift__s1_0, bibscan__removed-referent-drift__s2_0, bibscan__removed-referent-drift__s3_0, contourkit__control, contourkit__external-dependency-drift__s1_0, contourkit__external-dependency-drift__s2_0, contourkit__external-dependency-drift__s3_0, contourkit__identifier-drift__s1_0, contourkit__identifier-drift__s2_0, contourkit__identifier-drift__s3_0, contourkit__path-location-drift__s1_0, contourkit__path-location-drift__s2_0, contourkit__path-location-drift__s3_0, contourkit__removed-referent-drift__s1_0, contourkit__removed-referent-drift__s2_0, contourkit__removed-referent-drift__s3_0, morpheme__control, morpheme__external-dependency-drift__s1_0, morpheme__external-dependency-drift__s2_0, morpheme__external-dependency-drift__s3_0, morpheme__identifier-drift__s1_0, morpheme__identifier-drift__s2_0, morpheme__identifier-drift__s3_0, morpheme__path-location-drift__s1_0, morpheme__path-location-drift__s2_0, morpheme__path-location-drift__s3_0, morpheme__removed-referent-drift__s1_0, morpheme__removed-referent-drift__s2_0, morpheme__removed-referent-drift__s3_0, sensorbus__control, sensorbus__external-dependency-drift__s1_0, sensorbus__external-dependency-drift__s2_0, sensorbus__external-dependency-drift__s3_0, sensorbus__identifier-drift__s1_0, sensorbus__identifier-drift__s2_0, sensorbus__identifier-drift__s3_0, sensorbus__path-location-drift__s1_0, sensorbus__path-location-drift__s2_0, sensorbus__path-location-drift__s3_0, sensorbus__removed-referent-drift__s1_0, sensorbus__removed-referent-drift__s2_0, sensorbus__removed-referent-drift__s3_0, serialscope__control, serialscope__external-dependency-drift__s1_0, serialscope__external-dependency-drift__s2_0, serialscope__external-dependency-drift__s3_0, serialscope__identifier-drift__s1_0, serialscope__identifier-drift__s2_0, serialscope__identifier-drift__s3_0, serialscope__path-location-drift__s1_0, serialscope__path-location-drift__s2_0, serialscope__path-location-drift__s3_0, serialscope__removed-referent-drift__s1_0, serialscope__removed-referent-drift__s2_0, serialscope__removed-referent-drift__s3_0, tileplan__control, tileplan__identifier-drift__s1_0, tileplan__identifier-drift__s2_0, tileplan__identifier-drift__s3_0, tileplan__path-location-drift__s1_0, tileplan__path-location-drift__s2_0, tileplan__path-location-drift__s3_0, tileplan__removed-referent-drift__s1_0, tileplan__removed-referent-drift__s2_0, tileplan__removed-referent-drift__s3_0
- engine: `./.venv/bin/python3 -m docassay.core.dump_claims`
- smoke/contamination: smoke: repos are from test_repos/validation_repos (held-out); not an evaluation corpus

## Overall

NEI is a deliberate abstention, not a failure; only `none` is an
extraction miss. `refutation + abstention + extraction miss = 1`.

| verified/injected | refuted | NEI | none | refutation [ci95] | abstention | extraction miss | gap inj/refuted | controls | clean | precision [ci95] |
|---|---|---|---|---|---|---|---|---|---|---|
| 69/69 | 50 | 15 | 4 | 0.725 [0.61, 0.816] | 0.217 | 0.058 | 0/0 | 24 | 24 | 1.0 [0.862, 1.0] |

## Per canonical class

| canonical_class | verified/injected | refuted | NEI | none | refutation | abstention | extraction miss | gap inj/refuted | controls | precision |
|---|---|---|---|---|---|---|---|---|---|---|
| external-dependency-drift | 15/15 | 15 | 0 | 0 | 1.0 | 0.0 | 0.0 | 0/0 | 5 | 1.0 |
| identifier-drift | 18/18 | 9 | 9 | 0 | 0.5 | 0.5 | 0.0 | 0/0 | 13 | 1.0 |
| path-location-drift | 18/18 | 14 | 0 | 4 | 0.778 | 0.0 | 0.222 | 0/0 | 6 | 1.0 |
| removed-referent-drift | 18/18 | 12 | 6 | 0 | 0.667 | 0.333 | 0.0 | 0/0 | 0 | - |

## Outcome by claim form

Aggregated over the `refuted` bucket (controls shown separately).

| claim form | verified/injected | refuted | NEI | none | refutation | abstention | extraction miss | controls | precision |
|---|---|---|---|---|---|---|---|---|---|
| bare | 28/28 | 14 | 14 | 0 | 0.5 | 0.5 | 0.0 | 10 | 1.0 |
| bare_call | 7/7 | 6 | 1 | 0 | 0.857 | 0.143 | 0.0 | 0 | - |
| dependency | 15/15 | 15 | 0 | 0 | 1.0 | 0.0 | 0.0 | 5 | 1.0 |
| path | 18/18 | 14 | 0 | 4 | 0.778 | 0.0 | 0.222 | 6 | 1.0 |
| qualified | 1/1 | 1 | 0 | 0 | 1.0 | 0.0 | 0.0 | 3 | 1.0 |

## Reaction distribution (MPChecker: how the tool reacted)

| canonical_class | bucket | refuted | nei | none |
|---|---|---|---|---|
| external-dependency-drift | refuted | 15 | 0 | 0 |
| identifier-drift | refuted | 9 | 9 | 0 |
| path-location-drift | refuted | 14 | 0 | 4 |
| removed-referent-drift | refuted | 12 | 6 | 0 |

## Unattributed findings (injected tree, precision proxy)

New refutations on the injected tree not matching any injected artifact —
pre-existing findings (genuine or false) that survive injection.

| repo | baseline refuted | new refuted | unattributed |
|---|---|---|---|
| bibscan__control | 0 | 0 | 0 |
| bibscan__external-dependency-drift__s1_0 | 0 | 1 | 0 |
| bibscan__external-dependency-drift__s2_0 | 0 | 1 | 0 |
| bibscan__external-dependency-drift__s3_0 | 0 | 1 | 0 |
| bibscan__identifier-drift__s1_0 | 0 | 0 | 0 |
| bibscan__identifier-drift__s2_0 | 0 | 2 | 0 |
| bibscan__identifier-drift__s3_0 | 0 | 0 | 0 |
| bibscan__path-location-drift__s1_0 | 0 | 1 | 0 |
| bibscan__path-location-drift__s2_0 | 0 | 1 | 0 |
| bibscan__path-location-drift__s3_0 | 0 | 0 | 0 |
| bibscan__removed-referent-drift__s1_0 | 0 | 2 | 0 |
| bibscan__removed-referent-drift__s2_0 | 0 | 1 | 0 |
| bibscan__removed-referent-drift__s3_0 | 0 | 0 | 0 |
| contourkit__control | 0 | 0 | 0 |
| contourkit__external-dependency-drift__s1_0 | 0 | 3 | 0 |
| contourkit__external-dependency-drift__s2_0 | 0 | 3 | 0 |
| contourkit__external-dependency-drift__s3_0 | 0 | 3 | 0 |
| contourkit__identifier-drift__s1_0 | 0 | 0 | 0 |
| contourkit__identifier-drift__s2_0 | 0 | 0 | 0 |
| contourkit__identifier-drift__s3_0 | 0 | 0 | 0 |
| contourkit__path-location-drift__s1_0 | 0 | 1 | 0 |
| contourkit__path-location-drift__s2_0 | 0 | 0 | 0 |
| contourkit__path-location-drift__s3_0 | 0 | 1 | 0 |
| contourkit__removed-referent-drift__s1_0 | 0 | 0 | 0 |
| contourkit__removed-referent-drift__s2_0 | 0 | 1 | 0 |
| contourkit__removed-referent-drift__s3_0 | 0 | 0 | 0 |
| morpheme__control | 0 | 0 | 0 |
| morpheme__external-dependency-drift__s1_0 | 0 | 1 | 0 |
| morpheme__external-dependency-drift__s2_0 | 0 | 1 | 0 |
| morpheme__external-dependency-drift__s3_0 | 0 | 1 | 0 |
| morpheme__identifier-drift__s1_0 | 0 | 1 | 0 |
| morpheme__identifier-drift__s2_0 | 0 | 1 | 0 |
| morpheme__identifier-drift__s3_0 | 0 | 1 | 0 |
| morpheme__path-location-drift__s1_0 | 0 | 4 | 0 |
| morpheme__path-location-drift__s2_0 | 0 | 1 | 0 |
| morpheme__path-location-drift__s3_0 | 0 | 1 | 0 |
| morpheme__removed-referent-drift__s1_0 | 0 | 1 | 0 |
| morpheme__removed-referent-drift__s2_0 | 0 | 1 | 0 |
| morpheme__removed-referent-drift__s3_0 | 0 | 1 | 0 |
| sensorbus__control | 0 | 0 | 0 |
| sensorbus__external-dependency-drift__s1_0 | 0 | 1 | 0 |
| sensorbus__external-dependency-drift__s2_0 | 0 | 1 | 0 |
| sensorbus__external-dependency-drift__s3_0 | 0 | 1 | 0 |
| sensorbus__identifier-drift__s1_0 | 0 | 0 | 0 |
| sensorbus__identifier-drift__s2_0 | 0 | 0 | 0 |
| sensorbus__identifier-drift__s3_0 | 0 | 0 | 0 |
| sensorbus__path-location-drift__s1_0 | 0 | 3 | 0 |
| sensorbus__path-location-drift__s2_0 | 0 | 3 | 0 |
| sensorbus__path-location-drift__s3_0 | 0 | 3 | 0 |
| sensorbus__removed-referent-drift__s1_0 | 0 | 0 | 0 |
| sensorbus__removed-referent-drift__s2_0 | 0 | 0 | 0 |
| sensorbus__removed-referent-drift__s3_0 | 0 | 0 | 0 |
| serialscope__control | 0 | 0 | 0 |
| serialscope__external-dependency-drift__s1_0 | 0 | 1 | 0 |
| serialscope__external-dependency-drift__s2_0 | 0 | 1 | 0 |
| serialscope__external-dependency-drift__s3_0 | 0 | 1 | 0 |
| serialscope__identifier-drift__s1_0 | 0 | 1 | 0 |
| serialscope__identifier-drift__s2_0 | 0 | 0 | 0 |
| serialscope__identifier-drift__s3_0 | 0 | 1 | 0 |
| serialscope__path-location-drift__s1_0 | 0 | 5 | 0 |
| serialscope__path-location-drift__s2_0 | 0 | 5 | 0 |
| serialscope__path-location-drift__s3_0 | 0 | 3 | 0 |
| serialscope__removed-referent-drift__s1_0 | 0 | 1 | 0 |
| serialscope__removed-referent-drift__s2_0 | 0 | 1 | 0 |
| serialscope__removed-referent-drift__s3_0 | 0 | 1 | 0 |
| tileplan__control | 0 | 0 | 0 |
| tileplan__identifier-drift__s1_0 | 0 | 1 | 0 |
| tileplan__identifier-drift__s2_0 | 0 | 1 | 0 |
| tileplan__identifier-drift__s3_0 | 0 | 1 | 0 |
| tileplan__path-location-drift__s1_0 | 0 | 0 | 0 |
| tileplan__path-location-drift__s2_0 | 0 | 0 | 0 |
| tileplan__path-location-drift__s3_0 | 0 | 1 | 0 |
| tileplan__removed-referent-drift__s1_0 | 0 | 2 | 0 |
| tileplan__removed-referent-drift__s2_0 | 0 | 1 | 0 |
| tileplan__removed-referent-drift__s3_0 | 0 | 1 | 0 |

## Control false refutes (baseline)

None.

## Boundary (out-of-scope classes, not operators)

```
{
  "out_of_scope_repo_expr": [
    "behavior-drift",
    "signature-drift",
    "constraint-drift",
    "security-drift",
    "exception-contract-drift",
    "null-semantics-drift",
    "format-encoding-drift",
    "polarity-order-drift",
    "lifecycle-contract-drift",
    "return-value-semantics-drift",
    "parameter-mismatch",
    "unused-parameter",
    "copy-edit-drift"
  ],
  "out_of_scope_doc_process_data": [
    "presentation-format",
    "documentation-process",
    "documentation-tooling",
    "data-quality",
    "control-repair-failure"
  ],
  "candidate_unconfirmed": [
    "error-message-drift"
  ]
}
```
