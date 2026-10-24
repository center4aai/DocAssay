# Injected-gold metrics

- date: 2026-10-24
- seed: 0
- repos: ci_workflow_control_present, ci_workflow_false_claim, ci_workflow_mention, dockerfile_control_present, dockerfile_false_claim, dockerfile_mention, license_control_present, license_false_claim, license_mention
- engine: `./.venv/bin/python3 -m docassay.core.dump_claims`
- smoke/contamination: conformance: constructed cases on a clean synthetic base (predicate-defined artifact classes; separate provenance arm)

## Overall

NEI is a deliberate abstention, not a failure; only `none` is an
extraction miss. `refutation + abstention + extraction miss = 1`.

| verified/injected | refuted | NEI | none | refutation [ci95] | abstention | extraction miss | gap inj/refuted | controls | clean | precision [ci95] |
|---|---|---|---|---|---|---|---|---|---|---|
| 3/3 | 3 | 0 | 0 | 1.0 [0.439, 1.0] | 0.0 | 0.0 | 0/0 | 6 | 5 | 0.833 [0.436, 0.97] |

## Per canonical class

| canonical_class | verified/injected | refuted | NEI | none | refutation | abstention | extraction miss | gap inj/refuted | controls | precision |
|---|---|---|---|---|---|---|---|---|---|---|
| ci-workflow-drift | 1/1 | 1 | 0 | 0 | 1.0 | 0.0 | 0.0 | 0/0 | 2 | 1.0 |
| dockerfile-drift | 1/1 | 1 | 0 | 0 | 1.0 | 0.0 | 0.0 | 0/0 | 2 | 1.0 |
| license-drift | 1/1 | 1 | 0 | 0 | 1.0 | 0.0 | 0.0 | 0/0 | 2 | 0.5 |

## Outcome by claim form

Aggregated over the `refuted` bucket (controls shown separately).

| claim form | verified/injected | refuted | NEI | none | refutation | abstention | extraction miss | controls | precision |
|---|---|---|---|---|---|---|---|---|---|
| bare | 3/3 | 3 | 0 | 0 | 1.0 | 0.0 | 0.0 | 6 | 0.833 |

## Reaction distribution (MPChecker: how the tool reacted)

| canonical_class | bucket | refuted | nei | none |
|---|---|---|---|---|
| ci-workflow-drift | refuted | 1 | 0 | 0 |
| dockerfile-drift | refuted | 1 | 0 | 0 |
| license-drift | refuted | 1 | 0 | 0 |

## Unattributed findings (injected tree, precision proxy)

New refutations on the injected tree not matching any injected artifact —
pre-existing findings (genuine or false) that survive injection.

| repo | baseline refuted | new refuted | unattributed |
|---|---|---|---|
| ci_workflow_control_present | 0 | 0 | 0 |
| ci_workflow_false_claim | 0 | 2 | 0 |
| ci_workflow_mention | 0 | 0 | 0 |
| dockerfile_control_present | 0 | 0 | 0 |
| dockerfile_false_claim | 0 | 1 | 0 |
| dockerfile_mention | 0 | 0 | 0 |
| license_control_present | 0 | 0 | 0 |
| license_false_claim | 0 | 1 | 0 |
| license_mention | 1 | 0 | 0 |

## Control false refutes (baseline)

- `license_mention` license.mention `MIT` @ README.md:57
  - LICENSE 'mit' — 

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
