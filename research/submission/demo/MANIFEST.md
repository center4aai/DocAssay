# Artifact manifest

This is the DocAssay demo artifact, kept under
`research/submission/demo/` in the authors' tree.

**Size:** ≈79 MB, 6,449 files (6,444 in this directory plus five prompt files at the repository root)
**Version:** the git commit/tag that contains this file
**Checksums:** the git tree hash is the checksum for this directory. The
prebuilt image is available on GitHub Container Registry; `docker buildx
imagetools inspect ghcr.io/furovandrew/docassay:1.0` reports its digest
(`sha256:a56e25a2df932fcbbc51c3ddbac22d3b474406ab63e92f1b1c3a2bb927cf9a10`).

## Contents

| path | contents | files | size |
|---|---|---:|---:|
| `README.md`, `REPRODUCING.md`, `PROVENANCE.md`, `DATA-LICENSE.md`, `MANIFEST.md` | artifact guide, reproduction matrix, provenance, data licence, this manifest | 5 | small |
| `scripts/_paths.py` | shared path helper for the artifact scripts | 1 | 4 KB |
| `demo/` | demo README, `Dockerfile.demo`, compose file, frozen demo corpus, subtitle track | 154 | 692 KB |
| `evidence/` | evidence map, Stage C report/metrics/annotation, real-world aggregate | 16 | 256 KB |
| `validation/` | SCOPE, protocol, Stage C plan, retrospective, real-world scripts/lock, triage, per-repo findings/reports | 104 | 16 MB |
| `injected_gold/` root | method README, boundary, catalogs, normalization | 5 | 60 KB |
| `injected_gold/engine/` | engine-free oracle used to verify injections | 3 | 40 KB |
| `injected_gold/synthetic*/` | frozen synthetic corpora for Stage A, B and C | 206 | 892 KB |
| `injected_gold/conformance/` | conformance templates and their run | 264 | 2.0 MB |
| `injected_gold/scripts/` | freeze, injection, scoring and metric scripts | 21 | 284 KB |
| `injected_gold/llm_injection/README.md` | LLM-injection method guide | 1 | 16 KB |
| `injected_gold/llm_injection/scripts/` | injector harness, exemplar-bank builder, evidence fetcher | 3 | 64 KB |
| `injected_gold/llm_injection/prompts/` | injection and annotation prompts | 6 | 28 KB |
| `injected_gold/llm_injection/exemplars/` | curated exemplar bank and source attribution | 46 | 928 KB |
| `injected_gold/llm_injection/runs/stage-c-2026-10-20/` | Stage C run: snapshots, manifests, claims, metrics, annotations, rescores | 2,655 | 36 MB |
| `injected_gold/llm_injection/runs/stage-b-2026-10-20/` | Stage B run (historical regression trials excluded) | 2,183 | 14 MB |
| `injected_gold/llm_injection/runs/scaled-2026-10-19/` | multi-seed scaled injection run | 591 | 4.9 MB |
| `injected_gold/llm_injection/runs/llm-demo/` | LLM-demo injection run | 165 | 1.5 MB |
| `injected_gold/llm_injection/runs/stage-a-2026-10-20/` | historical Stage A metrics/entries | 15 | 108 KB |
| `.opencode/agents/` (repository root) | five frozen corpus-generation agent prompts | 5 | 24 KB |

The authoritative Stage C run is
`injected_gold/llm_injection/runs/stage-c-2026-10-20/`; the copies under
`evidence/` are curated for reading and the run wins on disagreement.

## Not tracked

| item | why | where |
|---|---|---|
| `validation/real_world/repos/` | 16 third-party clones, 678 MB; not redistributed | `fetch_corpus.py` + `corpus.lock.json` (pinned URL and commit) |
| per-repo `claims.jsonl` | fully derived, ~93 MB | `run_corpus.py` on the pinned clones |
| `demo/video/*.mp4` | binary; the video is hosted on YouTube | YouTube URL referenced from `demo/README.md`; subtitles ship here |
| prebuilt image | build artifact, not source | `ghcr.io/furovandrew/docassay:1.0` (see §2 of `README.md`) |

## Reproduce

From the repository root:

```bash
B=research/submission/demo/injected_gold
RUN=$B/llm_injection/runs/stage-c-2026-10-20
export PYTHONPATH=src
uv run python $B/scripts/freeze_scope_engine.py \
    --verify --freeze $RUN/scope_engine_freeze.json
uv run python $B/scripts/freeze_corpus.py \
    --verify --freeze $RUN/corpus_freeze.json
```

The full experiment matrix is in `REPRODUCING.md`.

## Licences

- Software: MIT (repository `LICENSE`).
- Synthetic corpora, frozen run data and evidence: CC BY 4.0
  (`DATA-LICENSE.md`).
- Third-party quotations and patch excerpts remain under their source
  repository's licence; see `PROVENANCE.md` and the exemplar README.
