# Injected-gold metrics

- date: 2026-10-14
- seed: 1
- repos: ledgerly, parcelroute, quillpad, tidecast
- engine: `./.venv/bin/python3 -m docassay.core.dump_claims`
- smoke/contamination: synthetic: generated repos, docs and code consistent by construction (uncontaminated evaluation corpus)

## Overall

| refuted injected | detected | recall [ci95] | doc_drift inj/det | completeness_gap inj/det | controls | clean | precision [ci95] |
|---|---|---|---|---|---|---|---|
| 20 | 14 | 0.7 [0.481, 0.855] | 0/0 | 0/0 | 0 | 0 | None None |

## Per canonical class

| canonical_class | refuted inj | det | recall | doc_drift inj/det | gap inj/det | controls | precision | reactions (refuted/nei/none) |
|---|---|---|---|---|---|---|---|---|
| external-dependency-drift | 4 | 3 | 0.75 [0.301, 0.954] | 0/0 | 0/0 | 0 | - - | 3/0/1 |
| identifier-drift | 4 | 4 | 1.0 [0.51, 1.0] | 0/0 | 0/0 | 0 | - - | 4/0/0 |
| path-location-drift | 4 | 4 | 1.0 [0.51, 1.0] | 0/0 | 0/0 | 0 | - - | 4/0/0 |
| removed-referent-drift | 4 | 3 | 0.75 [0.301, 0.954] | 0/0 | 0/0 | 0 | - - | 3/0/1 |
| value-drift | 4 | 0 | 0.0 [0.0, 0.49] | 0/0 | 0/0 | 0 | - - | 0/0/4 |

## Reaction distribution (MPChecker: how the tool reacted)

| canonical_class | bucket | refuted | nei | doc_conflict | none |
|---|---|---|---|---|---|
| external-dependency-drift | refuted | 3 | 0 | 0 | 1 |
| identifier-drift | refuted | 4 | 0 | 0 | 0 |
| path-location-drift | refuted | 4 | 0 | 0 | 0 |
| removed-referent-drift | refuted | 3 | 0 | 0 | 1 |
| value-drift | refuted | 0 | 0 | 0 | 4 |

## Unattributed findings (injected tree, precision proxy)

New refutations on the injected tree not matching any injected artifact —
pre-existing findings (genuine or false) that survive injection.

| repo | baseline refuted | new refuted | unattributed |
|---|---|---|---|
| ledgerly | 0 | 11 | 0 |
| parcelroute | 0 | 15 | 0 |
| quillpad | 0 | 8 | 0 |
| tidecast | 0 | 13 | 0 |

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
