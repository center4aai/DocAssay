# Harness fix before scoring — dependency requirement normalization

**Date:** 2026-10-20
**Status:** applied **before** any scoring run; no tool output influenced it.

## What happened

The first finalize pass produced:

| status | count |
|---|---:|
| verified | 55 |
| verify_failed | 17 |

All 17 failures were `external-dependency-drift` constraint-form proposals
(1/18 verified for that class). The reason was identical:

```
rejected: constraint is None, expected 'click>=999'
```

The natural injector proposed the **full requirement string** (`click>=999`,
`numpy>=999`, `PyYAML>=999`, `click<8.1`) in the `new` field, while the
applier expects only the constraint (`>=999`, `<8.1`) and prefixes the
dependency name itself. The applier therefore wrote a malformed requirement
(`clickclick>=999`) and the engine-free oracle correctly rejected it.

This is a **harness parsing mismatch**, not a generator defect: the proposals
are semantically valid and name a real manifest dependency. The prompt was not
changed, the spec was not changed, and the tool was not changed. No tool result
existed at this point.

## Fix

`llm_inject._constraint(raw, symbol)` strips a leading dependency name when the
model writes the full requirement, leaving the constraint the applier expects.
The raw model value is preserved in the manifest as `new_raw` for provenance.
The rule is in `llm_injection/scripts/llm_inject.py`.

## Second fix: mixed-case dependency names in the oracle

After the requirement normalization, 70/72 verified. The two remaining failures
were both `PyYAML` proposals:

```
rejected: doc line no longer names the dependency: README.md:20
```

The inventory normalizes dependency names to lower case (`pyyaml`), while the
document spells the published name (`PyYAML`). The oracle's doc-line check was
case-sensitive. `engine/oracle.py:_check_dependency_version_break` now compares
the dependency name case-insensitively. This is an oracle correctness fix, not
a tool change; `oracle.py --selftest` passes.

## Effect

The frozen injector outputs are re-applied unchanged; only harness/oracle
parsing changes. Pre-fix and post-fix counts are reported side by side in the
Stage B report so the dependency arm is not silently inflated.

| pass | verified | verify_failed | dependency verified |
|---|---:|---:|---:|
| pre-fix | 55 | 17 | 1/18 |
| after requirement normalization | 70 | 2 | 16/18 |
| after case-insensitive oracle check | **72** | **0** | **18/18** |

No injector output was regenerated and no prompt, spec, or tool code was
changed. The model's raw value is preserved as `new_raw` in the manifest.

## Third, summary-only fix after the engine run

The first scoring attempt generated all claim dumps, then crashed in
`seed_stats` because control entries do not carry the injection-only `op_id`
field. `seed_stats` now skips controls. The engine was **not** re-run (the
cached claims were reused), and no per-entry outcome or metric changed. This is
an analysis-summary fix, not a scoring or tool change.
