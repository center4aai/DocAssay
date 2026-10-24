# Reproducing the reported experiments

This file is the reproducibility matrix for the demo artifact. The short
version: the **reported experiments reproduce from this repository**; the
LLM generation/annotation steps are not bit-reproducible, and the real-world
rerun needs the network once to fetch the pinned clones.

## What is required

- Python 3.12+ and `uv`.
- This repository (source, scripts, frozen corpora, metrics, run trees).
- Network only for `fetch_corpus.py`. The real-world clones are identified by
  URL and commit in `validation/real_world/corpus.lock.json`; they are not
  redistributed.

## Matrix

| experiment | reproduction | how |
|---|---|---|
| **Stage C scope/engine freeze** | **byte-identical** | `freeze_scope_engine.py --verify` |
| **Stage C corpus freeze** | **byte-identical** | `freeze_corpus.py --verify` |
| **Stage C engine run (150 claim dumps)** | **byte-identical** | `score_injections.py --force` on `scoring_manifest.jsonl` + `snapshots/` |
| **Stage C metrics (Table 1, controls, CIs)** | **byte-identical** | `stage_c_metrics.py --run <run>` |
| **LLM annotation agreement (Table 2)** | **byte-identical** | `annotation_agreement.py --run <run>` on the shipped `annotations/` |
| **Real-world per-repo runs** | **byte-identical** | `run_corpus.py` on the pinned clones (16/16 `claims.jsonl` and `findings.jsonl`) |
| **Real-world staleness attribution** | **byte-identical** | `attribute_staleness.py` on the pinned clones |
| **Real-world adjudication (Table 3)** | **byte-identical** | `merge_triage.py` on `validation/real_world/triage/` |
| **Stage B held-out metrics** | values identical | `stage_b_metrics.py --run <run>`; service path fields in `metrics_stage_b.json` differ, `metrics.json` matches |
| **Conformance templates** | outcomes identical | `conformance/run.py` + `score_injections.py`; 9/9 verified, 3/3 refuted, 5/6 controls clean |
| **Stage A ablation** | **not rerunnable** | only metrics/entries are shipped; the generator run is historical |
| **LLM corpus/injection generation** | **not bit-reproducible** | external models; the frozen corpus/snapshots are shipped |

## Commands

```bash
B=research/submission/demo/injected_gold
RUN=$B/llm_injection/runs/stage-c-2026-10-20
RW=research/submission/demo/validation/real_world

# Freeze checks
PYTHONPATH=src uv run python $B/scripts/freeze_scope_engine.py --verify --freeze $RUN/scope_engine_freeze.json
PYTHONPATH=src uv run python $B/scripts/freeze_corpus.py --verify --freeze $RUN/corpus_freeze.json

# Stage C: engine run + metrics (writes a fresh rescore directory)
OUT=/tmp/stage-c-rescore
PYTHONPATH=src uv run python $B/scripts/score_injections.py \
    --manifest $RUN/scoring_manifest.jsonl --snapshots $RUN/snapshots \
    --out $OUT --force
# stage_c_metrics reads the manifest, design, control config and run stats
cp $RUN/scoring_manifest.jsonl $RUN/corpus_design.json \
   $RUN/control_config.json $RUN/stats.json $OUT/
PYTHONPATH=src uv run python $B/scripts/stage_c_metrics.py --run $OUT

# LLM annotation agreement (uses the frozen labels)
PYTHONPATH=src uv run python $B/scripts/annotation_agreement.py --run $RUN

# Stage B
SB=$B/llm_injection/runs/stage-b-2026-10-20
PYTHONPATH=src uv run python $B/scripts/stage_b_metrics.py --run $SB

# Conformance (writes a fresh output directory)
PYTHONPATH=src uv run python $B/conformance/run.py --out /tmp/conformance-reproduce
PYTHONPATH=src uv run python $B/scripts/score_injections.py \
    --manifest /tmp/conformance-reproduce/manifest.jsonl \
    --snapshots /tmp/conformance-reproduce/snapshots \
    --out /tmp/conformance-reproduce --seed 0

# Real-world corpus and adjudication (network for the pinned clones)
PYTHONPATH=src uv run python $RW/scripts/fetch_corpus.py
PYTHONPATH=src uv run python $RW/scripts/run_corpus.py --date reproduce
PYTHONPATH=src uv run python $RW/scripts/attribute_staleness.py --date reproduce
PYTHONPATH=src uv run python $RW/scripts/merge_triage.py
```

The Stage C, Stage B, conformance and real-world reruns write into fresh
directories; the tracked run trees are inputs, not outputs. The per-repository
`claims.jsonl` files are not shipped (they are fully derived and large); the
shipped `findings.jsonl`, `staleness.jsonl` and `summary.json` are the expected
outputs to compare against.

## What "not reproducible" means here

- **LLM generation/annotation.** The prompts, model IDs, seeds and frozen
  outputs are shipped, but re-running a model is not deterministic and is not
  required to check a reported number. The annotation arm is reproduced from the
  shipped labels, not by re-querying the models.
- **Stage A.** The historical ablation has only its metrics/entries; its
  snapshots/claims are not part of the artifact. It is not used for a reported result
  table.
- **Real-world clones.** The 16 repositories are third-party checkouts. The
  lockfile pins the URL and commit; `fetch_corpus.py` reproduces the checkout
  without this repository redistributing the code.
