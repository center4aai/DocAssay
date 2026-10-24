# Seed diversity and per-seed detection

`coverage` = distinct injected targets / candidate-pool size. A pool of 1
is seed-invariant by construction (e.g. a single resolvable path).

## Per operator × repo

| repo::operator | pool | entries | distinct targets | coverage | seeds |
|---|---|---|---|---|---|
| ledgerly__s1::llm.external-dependency-drift | None | 1 | 1 | None | 1 |
| ledgerly__s1::llm.identifier-drift | None | 1 | 1 | None | 1 |
| ledgerly__s1::llm.path-location-drift | None | 1 | 1 | None | 1 |
| ledgerly__s1::llm.removed-referent-drift | None | 1 | 1 | None | 1 |
| ledgerly__s1::llm.value-drift | None | 1 | 1 | None | 1 |
| ledgerly__s2::llm.identifier-drift | None | 1 | 1 | None | 1 |
| ledgerly__s2::llm.path-location-drift | None | 1 | 1 | None | 1 |
| ledgerly__s2::llm.removed-referent-drift | None | 1 | 1 | None | 1 |
| ledgerly__s2::llm.value-drift | None | 1 | 1 | None | 1 |
| ledgerly__s3::llm.identifier-drift | None | 1 | 1 | None | 1 |
| ledgerly__s3::llm.path-location-drift | None | 1 | 1 | None | 1 |
| ledgerly__s3::llm.value-drift | None | 1 | 1 | None | 1 |
| parcelroute__s1::llm.external-dependency-drift | None | 1 | 1 | None | 1 |
| parcelroute__s1::llm.identifier-drift | None | 1 | 1 | None | 1 |
| parcelroute__s1::llm.path-location-drift | None | 1 | 1 | None | 1 |
| parcelroute__s1::llm.removed-referent-drift | None | 1 | 1 | None | 1 |
| parcelroute__s1::llm.value-drift | None | 1 | 1 | None | 1 |
| parcelroute__s2::llm.external-dependency-drift | None | 1 | 1 | None | 1 |
| parcelroute__s2::llm.path-location-drift | None | 1 | 1 | None | 1 |
| parcelroute__s2::llm.removed-referent-drift | None | 1 | 1 | None | 1 |
| parcelroute__s2::llm.value-drift | None | 1 | 1 | None | 1 |
| parcelroute__s3::llm.external-dependency-drift | None | 1 | 1 | None | 1 |
| parcelroute__s3::llm.identifier-drift | None | 1 | 1 | None | 1 |
| parcelroute__s3::llm.path-location-drift | None | 1 | 1 | None | 1 |
| parcelroute__s3::llm.value-drift | None | 1 | 1 | None | 1 |
| quillpad__s1::llm.identifier-drift | None | 1 | 1 | None | 1 |
| quillpad__s1::llm.path-location-drift | None | 1 | 1 | None | 1 |
| quillpad__s1::llm.value-drift | None | 1 | 1 | None | 1 |
| quillpad__s2::llm.external-dependency-drift | None | 1 | 1 | None | 1 |
| quillpad__s2::llm.identifier-drift | None | 1 | 1 | None | 1 |
| quillpad__s2::llm.path-location-drift | None | 1 | 1 | None | 1 |
| quillpad__s2::llm.removed-referent-drift | None | 1 | 1 | None | 1 |
| quillpad__s2::llm.value-drift | None | 1 | 1 | None | 1 |
| quillpad__s3::llm.external-dependency-drift | None | 1 | 1 | None | 1 |
| quillpad__s3::llm.identifier-drift | None | 1 | 1 | None | 1 |
| quillpad__s3::llm.path-location-drift | None | 1 | 1 | None | 1 |
| quillpad__s3::llm.removed-referent-drift | None | 1 | 1 | None | 1 |
| quillpad__s3::llm.value-drift | None | 1 | 1 | None | 1 |
| tidecast__s1::llm.external-dependency-drift | None | 1 | 1 | None | 1 |
| tidecast__s1::llm.identifier-drift | None | 1 | 1 | None | 1 |
| tidecast__s1::llm.path-location-drift | None | 1 | 1 | None | 1 |
| tidecast__s1::llm.removed-referent-drift | None | 1 | 1 | None | 1 |
| tidecast__s1::llm.value-drift | None | 1 | 1 | None | 1 |
| tidecast__s2::llm.external-dependency-drift | None | 1 | 1 | None | 1 |
| tidecast__s2::llm.identifier-drift | None | 1 | 1 | None | 1 |
| tidecast__s2::llm.path-location-drift | None | 1 | 1 | None | 1 |
| tidecast__s2::llm.removed-referent-drift | None | 1 | 1 | None | 1 |
| tidecast__s2::llm.value-drift | None | 1 | 1 | None | 1 |
| tidecast__s3::llm.external-dependency-drift | None | 1 | 1 | None | 1 |
| tidecast__s3::llm.identifier-drift | None | 1 | 1 | None | 1 |
| tidecast__s3::llm.path-location-drift | None | 1 | 1 | None | 1 |
| tidecast__s3::llm.removed-referent-drift | None | 1 | 1 | None | 1 |
| tidecast__s3::llm.value-drift | None | 1 | 1 | None | 1 |

## Per seed

| seed | refuted inj/det | doc_drift inj/det | controls | clean |
|---|---|---|---|---|
| 1 | 18/16 | 0/0 | 0 | 0 |
| 2 | 18/17 | 0/0 | 0 | 0 |
| 3 | 17/16 | 0/0 | 0 | 0 |
