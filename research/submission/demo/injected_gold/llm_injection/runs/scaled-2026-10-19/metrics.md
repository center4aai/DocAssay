# Injected-gold metrics

- date: 2026-10-19
- seed: 1
- repos: ledgerly__s1, ledgerly__s2, ledgerly__s3, parcelroute__s1, parcelroute__s2, parcelroute__s3, quillpad__s1, quillpad__s2, quillpad__s3, tidecast__s1, tidecast__s2, tidecast__s3
- engine: `./.venv/bin/python3 -m docassay.core.dump_claims`
- smoke/contamination: synthetic: generated repos, docs and code consistent by construction (uncontaminated evaluation corpus)

## Overall

| refuted injected | detected | recall [ci95] | doc_drift inj/det | completeness_gap inj/det | controls | clean | precision [ci95] |
|---|---|---|---|---|---|---|---|
| 53 | 49 | 0.925 [0.821, 0.97] | 0/0 | 0/0 | 0 | 0 | None None |

## Per canonical class

| canonical_class | refuted inj | det | recall | doc_drift inj/det | gap inj/det | controls | precision | reactions (refuted/nei/none) |
|---|---|---|---|---|---|---|---|---|
| external-dependency-drift | 9 | 8 | 0.889 [0.565, 0.98] | 0/0 | 0/0 | 0 | - - | 8/0/1 |
| identifier-drift | 11 | 10 | 0.909 [0.623, 0.984] | 0/0 | 0/0 | 0 | - - | 10/1/0 |
| path-location-drift | 12 | 12 | 1.0 [0.758, 1.0] | 0/0 | 0/0 | 0 | - - | 12/0/0 |
| removed-referent-drift | 9 | 7 | 0.778 [0.453, 0.937] | 0/0 | 0/0 | 0 | - - | 7/0/2 |
| value-drift | 12 | 12 | 1.0 [0.758, 1.0] | 0/0 | 0/0 | 0 | - - | 12/0/0 |

## Reaction distribution (MPChecker: how the tool reacted)

| canonical_class | bucket | refuted | nei | doc_conflict | none |
|---|---|---|---|---|---|
| external-dependency-drift | refuted | 8 | 0 | 0 | 1 |
| identifier-drift | refuted | 10 | 1 | 0 | 0 |
| path-location-drift | refuted | 12 | 0 | 0 | 0 |
| removed-referent-drift | refuted | 7 | 0 | 0 | 2 |
| value-drift | refuted | 12 | 0 | 0 | 0 |

## Unattributed findings (injected tree, precision proxy)

New refutations on the injected tree not matching any injected artifact —
pre-existing findings (genuine or false) that survive injection.

| repo | baseline refuted | new refuted | unattributed |
|---|---|---|---|
| ledgerly__s1 | 0 | 12 | 0 |
| ledgerly__s2 | 0 | 13 | 0 |
| ledgerly__s3 | 0 | 9 | 0 |
| parcelroute__s1 | 0 | 9 | 0 |
| parcelroute__s2 | 0 | 6 | 0 |
| parcelroute__s3 | 0 | 6 | 0 |
| quillpad__s1 | 0 | 5 | 0 |
| quillpad__s2 | 0 | 10 | 0 |
| quillpad__s3 | 0 | 5 | 0 |
| tidecast__s1 | 0 | 11 | 0 |
| tidecast__s2 | 0 | 14 | 0 |
| tidecast__s3 | 0 | 14 | 0 |

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
