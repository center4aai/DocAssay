# Seed diversity and per-seed detection

`coverage` = distinct injected targets / candidate-pool size. A pool of 1
is seed-invariant by construction (e.g. a single resolvable path).

## Per operator × repo

| repo::operator | pool | entries | distinct targets | coverage | seeds |
|---|---|---|---|---|---|
| gaugekit__external-dependency-drift__s1_0::llm.external-dependency-drift | None | 1 | 1 | None | 1 |
| gaugekit__external-dependency-drift__s2_0::llm.external-dependency-drift | None | 1 | 1 | None | 1 |
| gaugekit__external-dependency-drift__s3_0::llm.external-dependency-drift | None | 1 | 1 | None | 1 |
| gaugekit__identifier-drift__s1_0::llm.identifier-drift | None | 1 | 1 | None | 1 |
| gaugekit__identifier-drift__s2_0::llm.identifier-drift | None | 1 | 1 | None | 1 |
| gaugekit__identifier-drift__s3_0::llm.identifier-drift | None | 1 | 1 | None | 1 |
| gaugekit__path-location-drift__s1_0::llm.path-location-drift | None | 1 | 1 | None | 1 |
| gaugekit__path-location-drift__s2_0::llm.path-location-drift | None | 1 | 1 | None | 1 |
| gaugekit__path-location-drift__s3_0::llm.path-location-drift | None | 1 | 1 | None | 1 |
| gaugekit__removed-referent-drift__s1_0::llm.removed-referent-drift | None | 1 | 1 | None | 1 |
| gaugekit__removed-referent-drift__s2_0::llm.removed-referent-drift | None | 1 | 1 | None | 1 |
| gaugekit__removed-referent-drift__s3_0::llm.removed-referent-drift | None | 1 | 1 | None | 1 |
| gridwatch__external-dependency-drift__s1_0::llm.external-dependency-drift | None | 1 | 1 | None | 1 |
| gridwatch__external-dependency-drift__s2_0::llm.external-dependency-drift | None | 1 | 1 | None | 1 |
| gridwatch__external-dependency-drift__s3_0::llm.external-dependency-drift | None | 1 | 1 | None | 1 |
| gridwatch__identifier-drift__s1_0::llm.identifier-drift | None | 1 | 1 | None | 1 |
| gridwatch__identifier-drift__s2_0::llm.identifier-drift | None | 1 | 1 | None | 1 |
| gridwatch__identifier-drift__s3_0::llm.identifier-drift | None | 1 | 1 | None | 1 |
| gridwatch__path-location-drift__s1_0::llm.path-location-drift | None | 1 | 1 | None | 1 |
| gridwatch__path-location-drift__s2_0::llm.path-location-drift | None | 1 | 1 | None | 1 |
| gridwatch__path-location-drift__s3_0::llm.path-location-drift | None | 1 | 1 | None | 1 |
| gridwatch__removed-referent-drift__s1_0::llm.removed-referent-drift | None | 1 | 1 | None | 1 |
| gridwatch__removed-referent-drift__s2_0::llm.removed-referent-drift | None | 1 | 1 | None | 1 |
| gridwatch__removed-referent-drift__s3_0::llm.removed-referent-drift | None | 1 | 1 | None | 1 |
| palette__external-dependency-drift__s1_0::llm.external-dependency-drift | None | 1 | 1 | None | 1 |
| palette__external-dependency-drift__s2_0::llm.external-dependency-drift | None | 1 | 1 | None | 1 |
| palette__external-dependency-drift__s3_0::llm.external-dependency-drift | None | 1 | 1 | None | 1 |
| palette__identifier-drift__s1_0::llm.identifier-drift | None | 1 | 1 | None | 1 |
| palette__identifier-drift__s2_0::llm.identifier-drift | None | 1 | 1 | None | 1 |
| palette__identifier-drift__s3_0::llm.identifier-drift | None | 1 | 1 | None | 1 |
| palette__path-location-drift__s1_0::llm.path-location-drift | None | 1 | 1 | None | 1 |
| palette__path-location-drift__s2_0::llm.path-location-drift | None | 1 | 1 | None | 1 |
| palette__path-location-drift__s3_0::llm.path-location-drift | None | 1 | 1 | None | 1 |
| palette__removed-referent-drift__s1_0::llm.removed-referent-drift | None | 1 | 1 | None | 1 |
| palette__removed-referent-drift__s2_0::llm.removed-referent-drift | None | 1 | 1 | None | 1 |
| palette__removed-referent-drift__s3_0::llm.removed-referent-drift | None | 1 | 1 | None | 1 |
| plotline__external-dependency-drift__s1_0::llm.external-dependency-drift | None | 1 | 1 | None | 1 |
| plotline__external-dependency-drift__s2_0::llm.external-dependency-drift | None | 1 | 1 | None | 1 |
| plotline__external-dependency-drift__s3_0::llm.external-dependency-drift | None | 1 | 1 | None | 1 |
| plotline__identifier-drift__s1_0::llm.identifier-drift | None | 1 | 1 | None | 1 |
| plotline__identifier-drift__s2_0::llm.identifier-drift | None | 1 | 1 | None | 1 |
| plotline__identifier-drift__s3_0::llm.identifier-drift | None | 1 | 1 | None | 1 |
| plotline__path-location-drift__s1_0::llm.path-location-drift | None | 1 | 1 | None | 1 |
| plotline__path-location-drift__s2_0::llm.path-location-drift | None | 1 | 1 | None | 1 |
| plotline__path-location-drift__s3_0::llm.path-location-drift | None | 1 | 1 | None | 1 |
| plotline__removed-referent-drift__s1_0::llm.removed-referent-drift | None | 1 | 1 | None | 1 |
| plotline__removed-referent-drift__s2_0::llm.removed-referent-drift | None | 1 | 1 | None | 1 |
| plotline__removed-referent-drift__s3_0::llm.removed-referent-drift | None | 1 | 1 | None | 1 |
| recipecard__external-dependency-drift__s1_0::llm.external-dependency-drift | None | 1 | 1 | None | 1 |
| recipecard__external-dependency-drift__s2_0::llm.external-dependency-drift | None | 1 | 1 | None | 1 |
| recipecard__external-dependency-drift__s3_0::llm.external-dependency-drift | None | 1 | 1 | None | 1 |
| recipecard__identifier-drift__s1_0::llm.identifier-drift | None | 1 | 1 | None | 1 |
| recipecard__identifier-drift__s2_0::llm.identifier-drift | None | 1 | 1 | None | 1 |
| recipecard__identifier-drift__s3_0::llm.identifier-drift | None | 1 | 1 | None | 1 |
| recipecard__path-location-drift__s1_0::llm.path-location-drift | None | 1 | 1 | None | 1 |
| recipecard__path-location-drift__s2_0::llm.path-location-drift | None | 1 | 1 | None | 1 |
| recipecard__path-location-drift__s3_0::llm.path-location-drift | None | 1 | 1 | None | 1 |
| recipecard__removed-referent-drift__s1_0::llm.removed-referent-drift | None | 1 | 1 | None | 1 |
| recipecard__removed-referent-drift__s2_0::llm.removed-referent-drift | None | 1 | 1 | None | 1 |
| recipecard__removed-referent-drift__s3_0::llm.removed-referent-drift | None | 1 | 1 | None | 1 |
| sheetmusic__external-dependency-drift__s1_0::llm.external-dependency-drift | None | 1 | 1 | None | 1 |
| sheetmusic__external-dependency-drift__s2_0::llm.external-dependency-drift | None | 1 | 1 | None | 1 |
| sheetmusic__external-dependency-drift__s3_0::llm.external-dependency-drift | None | 1 | 1 | None | 1 |
| sheetmusic__identifier-drift__s1_0::llm.identifier-drift | None | 1 | 1 | None | 1 |
| sheetmusic__identifier-drift__s2_0::llm.identifier-drift | None | 1 | 1 | None | 1 |
| sheetmusic__identifier-drift__s3_0::llm.identifier-drift | None | 1 | 1 | None | 1 |
| sheetmusic__path-location-drift__s1_0::llm.path-location-drift | None | 1 | 1 | None | 1 |
| sheetmusic__path-location-drift__s2_0::llm.path-location-drift | None | 1 | 1 | None | 1 |
| sheetmusic__path-location-drift__s3_0::llm.path-location-drift | None | 1 | 1 | None | 1 |
| sheetmusic__removed-referent-drift__s1_0::llm.removed-referent-drift | None | 1 | 1 | None | 1 |
| sheetmusic__removed-referent-drift__s2_0::llm.removed-referent-drift | None | 1 | 1 | None | 1 |
| sheetmusic__removed-referent-drift__s3_0::llm.removed-referent-drift | None | 1 | 1 | None | 1 |

## Per seed

NEI is a deliberate abstention, not a miss; `none` is an extraction miss.

| seed | refuted inj | refuted | NEI | none | controls | clean |
|---|---|---|---|---|---|---|
| 1 | 24 | 12 | 4 | 8 | 0 | 0 |
| 2 | 24 | 12 | 1 | 11 | 0 | 0 |
| 3 | 24 | 11 | 2 | 11 | 0 | 0 |
