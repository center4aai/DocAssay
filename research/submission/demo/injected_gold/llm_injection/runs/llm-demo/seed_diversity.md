# Seed diversity and per-seed detection

`coverage` = distinct injected targets / candidate-pool size. A pool of 1
is seed-invariant by construction (e.g. a single resolvable path).

## Per operator × repo

| repo::operator | pool | entries | distinct targets | coverage | seeds |
|---|---|---|---|---|---|
| ledgerly::llm.external-dependency-drift | None | 1 | 1 | None | 1 |
| ledgerly::llm.identifier-drift | None | 1 | 1 | None | 1 |
| ledgerly::llm.path-location-drift | None | 1 | 1 | None | 1 |
| ledgerly::llm.removed-referent-drift | None | 1 | 1 | None | 1 |
| ledgerly::llm.value-drift | None | 1 | 1 | None | 1 |
| parcelroute::llm.external-dependency-drift | None | 1 | 1 | None | 1 |
| parcelroute::llm.identifier-drift | None | 1 | 1 | None | 1 |
| parcelroute::llm.path-location-drift | None | 1 | 1 | None | 1 |
| parcelroute::llm.removed-referent-drift | None | 1 | 1 | None | 1 |
| parcelroute::llm.value-drift | None | 1 | 1 | None | 1 |
| quillpad::llm.external-dependency-drift | None | 1 | 1 | None | 1 |
| quillpad::llm.identifier-drift | None | 1 | 1 | None | 1 |
| quillpad::llm.path-location-drift | None | 1 | 1 | None | 1 |
| quillpad::llm.removed-referent-drift | None | 1 | 1 | None | 1 |
| quillpad::llm.value-drift | None | 1 | 1 | None | 1 |
| tidecast::llm.external-dependency-drift | None | 1 | 1 | None | 1 |
| tidecast::llm.identifier-drift | None | 1 | 1 | None | 1 |
| tidecast::llm.path-location-drift | None | 1 | 1 | None | 1 |
| tidecast::llm.removed-referent-drift | None | 1 | 1 | None | 1 |
| tidecast::llm.value-drift | None | 1 | 1 | None | 1 |

## Per seed

| seed | refuted inj/det | doc_drift inj/det | controls | clean |
|---|---|---|---|---|
| 1 | 20/14 | 0/0 | 0 | 0 |
