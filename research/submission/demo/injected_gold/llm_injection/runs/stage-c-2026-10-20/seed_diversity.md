# Seed diversity and per-seed detection

`coverage` = distinct injected targets / candidate-pool size. A pool of 1
is seed-invariant by construction (e.g. a single resolvable path).

## Per operator × repo

| repo::operator | pool | entries | distinct targets | coverage | seeds |
|---|---|---|---|---|---|
| bibscan__external-dependency-drift__s1_0::llm.external-dependency-drift | None | 1 | 1 | None | 1 |
| bibscan__external-dependency-drift__s2_0::llm.external-dependency-drift | None | 1 | 1 | None | 1 |
| bibscan__external-dependency-drift__s3_0::llm.external-dependency-drift | None | 1 | 1 | None | 1 |
| bibscan__identifier-drift__s1_0::llm.identifier-drift | None | 1 | 1 | None | 1 |
| bibscan__identifier-drift__s2_0::llm.identifier-drift | None | 1 | 1 | None | 1 |
| bibscan__identifier-drift__s3_0::llm.identifier-drift | None | 1 | 1 | None | 1 |
| bibscan__path-location-drift__s1_0::llm.path-location-drift | None | 1 | 1 | None | 1 |
| bibscan__path-location-drift__s2_0::llm.path-location-drift | None | 1 | 1 | None | 1 |
| bibscan__path-location-drift__s3_0::llm.path-location-drift | None | 1 | 1 | None | 1 |
| bibscan__removed-referent-drift__s1_0::llm.removed-referent-drift | None | 1 | 1 | None | 1 |
| bibscan__removed-referent-drift__s2_0::llm.removed-referent-drift | None | 1 | 1 | None | 1 |
| bibscan__removed-referent-drift__s3_0::llm.removed-referent-drift | None | 1 | 1 | None | 1 |
| contourkit__external-dependency-drift__s1_0::llm.external-dependency-drift | None | 1 | 1 | None | 1 |
| contourkit__external-dependency-drift__s2_0::llm.external-dependency-drift | None | 1 | 1 | None | 1 |
| contourkit__external-dependency-drift__s3_0::llm.external-dependency-drift | None | 1 | 1 | None | 1 |
| contourkit__identifier-drift__s1_0::llm.identifier-drift | None | 1 | 1 | None | 1 |
| contourkit__identifier-drift__s2_0::llm.identifier-drift | None | 1 | 1 | None | 1 |
| contourkit__identifier-drift__s3_0::llm.identifier-drift | None | 1 | 1 | None | 1 |
| contourkit__path-location-drift__s1_0::llm.path-location-drift | None | 1 | 1 | None | 1 |
| contourkit__path-location-drift__s2_0::llm.path-location-drift | None | 1 | 1 | None | 1 |
| contourkit__path-location-drift__s3_0::llm.path-location-drift | None | 1 | 1 | None | 1 |
| contourkit__removed-referent-drift__s1_0::llm.removed-referent-drift | None | 1 | 1 | None | 1 |
| contourkit__removed-referent-drift__s2_0::llm.removed-referent-drift | None | 1 | 1 | None | 1 |
| contourkit__removed-referent-drift__s3_0::llm.removed-referent-drift | None | 1 | 1 | None | 1 |
| morpheme__external-dependency-drift__s1_0::llm.external-dependency-drift | None | 1 | 1 | None | 1 |
| morpheme__external-dependency-drift__s2_0::llm.external-dependency-drift | None | 1 | 1 | None | 1 |
| morpheme__external-dependency-drift__s3_0::llm.external-dependency-drift | None | 1 | 1 | None | 1 |
| morpheme__identifier-drift__s1_0::llm.identifier-drift | None | 1 | 1 | None | 1 |
| morpheme__identifier-drift__s2_0::llm.identifier-drift | None | 1 | 1 | None | 1 |
| morpheme__identifier-drift__s3_0::llm.identifier-drift | None | 1 | 1 | None | 1 |
| morpheme__path-location-drift__s1_0::llm.path-location-drift | None | 1 | 1 | None | 1 |
| morpheme__path-location-drift__s2_0::llm.path-location-drift | None | 1 | 1 | None | 1 |
| morpheme__path-location-drift__s3_0::llm.path-location-drift | None | 1 | 1 | None | 1 |
| morpheme__removed-referent-drift__s1_0::llm.removed-referent-drift | None | 1 | 1 | None | 1 |
| morpheme__removed-referent-drift__s2_0::llm.removed-referent-drift | None | 1 | 1 | None | 1 |
| morpheme__removed-referent-drift__s3_0::llm.removed-referent-drift | None | 1 | 1 | None | 1 |
| sensorbus__external-dependency-drift__s1_0::llm.external-dependency-drift | None | 1 | 1 | None | 1 |
| sensorbus__external-dependency-drift__s2_0::llm.external-dependency-drift | None | 1 | 1 | None | 1 |
| sensorbus__external-dependency-drift__s3_0::llm.external-dependency-drift | None | 1 | 1 | None | 1 |
| sensorbus__identifier-drift__s1_0::llm.identifier-drift | None | 1 | 1 | None | 1 |
| sensorbus__identifier-drift__s2_0::llm.identifier-drift | None | 1 | 1 | None | 1 |
| sensorbus__identifier-drift__s3_0::llm.identifier-drift | None | 1 | 1 | None | 1 |
| sensorbus__path-location-drift__s1_0::llm.path-location-drift | None | 1 | 1 | None | 1 |
| sensorbus__path-location-drift__s2_0::llm.path-location-drift | None | 1 | 1 | None | 1 |
| sensorbus__path-location-drift__s3_0::llm.path-location-drift | None | 1 | 1 | None | 1 |
| sensorbus__removed-referent-drift__s1_0::llm.removed-referent-drift | None | 1 | 1 | None | 1 |
| sensorbus__removed-referent-drift__s2_0::llm.removed-referent-drift | None | 1 | 1 | None | 1 |
| sensorbus__removed-referent-drift__s3_0::llm.removed-referent-drift | None | 1 | 1 | None | 1 |
| serialscope__external-dependency-drift__s1_0::llm.external-dependency-drift | None | 1 | 1 | None | 1 |
| serialscope__external-dependency-drift__s2_0::llm.external-dependency-drift | None | 1 | 1 | None | 1 |
| serialscope__external-dependency-drift__s3_0::llm.external-dependency-drift | None | 1 | 1 | None | 1 |
| serialscope__identifier-drift__s1_0::llm.identifier-drift | None | 1 | 1 | None | 1 |
| serialscope__identifier-drift__s2_0::llm.identifier-drift | None | 1 | 1 | None | 1 |
| serialscope__identifier-drift__s3_0::llm.identifier-drift | None | 1 | 1 | None | 1 |
| serialscope__path-location-drift__s1_0::llm.path-location-drift | None | 1 | 1 | None | 1 |
| serialscope__path-location-drift__s2_0::llm.path-location-drift | None | 1 | 1 | None | 1 |
| serialscope__path-location-drift__s3_0::llm.path-location-drift | None | 1 | 1 | None | 1 |
| serialscope__removed-referent-drift__s1_0::llm.removed-referent-drift | None | 1 | 1 | None | 1 |
| serialscope__removed-referent-drift__s2_0::llm.removed-referent-drift | None | 1 | 1 | None | 1 |
| serialscope__removed-referent-drift__s3_0::llm.removed-referent-drift | None | 1 | 1 | None | 1 |
| tileplan__identifier-drift__s1_0::llm.identifier-drift | None | 1 | 1 | None | 1 |
| tileplan__identifier-drift__s2_0::llm.identifier-drift | None | 1 | 1 | None | 1 |
| tileplan__identifier-drift__s3_0::llm.identifier-drift | None | 1 | 1 | None | 1 |
| tileplan__path-location-drift__s1_0::llm.path-location-drift | None | 1 | 1 | None | 1 |
| tileplan__path-location-drift__s2_0::llm.path-location-drift | None | 1 | 1 | None | 1 |
| tileplan__path-location-drift__s3_0::llm.path-location-drift | None | 1 | 1 | None | 1 |
| tileplan__removed-referent-drift__s1_0::llm.removed-referent-drift | None | 1 | 1 | None | 1 |
| tileplan__removed-referent-drift__s2_0::llm.removed-referent-drift | None | 1 | 1 | None | 1 |
| tileplan__removed-referent-drift__s3_0::llm.removed-referent-drift | None | 1 | 1 | None | 1 |

## Per seed

NEI is a deliberate abstention, not a miss; `none` is an extraction miss.

| seed | refuted inj | refuted | NEI | none | controls | clean |
|---|---|---|---|---|---|---|
| 1 | 23 | 17 | 5 | 1 | 0 | 0 |
| 2 | 23 | 17 | 4 | 2 | 0 | 0 |
| 3 | 23 | 16 | 6 | 1 | 0 | 0 |
