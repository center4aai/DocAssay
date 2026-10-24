# Conformance templates — the three predicate-defined artifact classes

These templates close the predicate-coverage gap: `LICENSE`, `HAS_DOCKERFILE`
and `HAS_CI_WORKFLOW` are declared by the tool (`SCOPE.md` §3.5–3.7) but have no
external-catalog rows. For these three the object is **defined by the predicate
itself** (a declared license, a `Dockerfile`, a CI config), so a constructed
case is a legitimate conformance test rather than a circular target choice.

This is a **separate provenance layer**, not the real-incident bank:

- `origin: "conformance"` — constructed from the predicate definition;
- never mixed into `catalog_ours.json` (which forbids hand-made cases without a
  real incident);
- reported as its own arm next to the real-incident LLM injections.

Each predicate gets three cases:

| case | what it checks |
|---|---|
| `false-claim` | a recorded claim that the artifact exists, while it does not → expected `REFUTED` |
| `control-present` | the claim is true (artifact present / declared license matches) → must not be refuted |
| `mention` | an instruction / negative mention ("Add a Dockerfile", "not MIT") → must not be refuted |

Run:

```bash
B=research/submission/demo/injected_gold
PYTHONPATH=src uv run python $B/conformance/run.py --out $B/conformance/runs/demo
PYTHONPATH=src uv run python $B/scripts/score_injections.py \
    --manifest $B/conformance/runs/demo/manifest.jsonl \
    --snapshots $B/conformance/runs/demo/snapshots \
    --out $B/conformance/runs/demo --seed 0
```
