# Seed diversity and per-seed detection

`coverage` = distinct injected targets / candidate-pool size. A pool of 1
is seed-invariant by construction (e.g. a single resolvable path).

## Per operator × repo

| repo::operator | pool | entries | distinct targets | coverage | seeds |
|---|---|---|---|---|---|
| ci_workflow_false_claim::ci_workflow.false_claim | None | 1 | 1 | None | 1 |
| dockerfile_false_claim::dockerfile.false_claim | None | 1 | 1 | None | 1 |
| license_false_claim::license.false_claim | None | 1 | 1 | None | 1 |

## Per seed

NEI is a deliberate abstention, not a miss; `none` is an extraction miss.

| seed | refuted inj | refuted | NEI | none | controls | clean |
|---|---|---|---|---|---|---|
| 0 | 3 | 3 | 0 | 0 | 0 | 0 |
