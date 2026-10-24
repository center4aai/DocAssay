# Provenance

This directory is the artifact for the DocAssay demo.
Everything needed to check the reported numbers is included here.
This file records the material that is intentionally **not** included and how it
can be obtained.

## Not tracked

| path / item | why | how to obtain |
|---|---|---|
| `validation/real_world/repos/` | 16 third-party clones, 678 MB; redistributing them would duplicate third-party code and licences | `validation/real_world/scripts/fetch_corpus.py`; URLs and commits are pinned in `corpus.lock.json` |
| `validation/real_world/runs/*/claims.jsonl` | fully derived per-repository claim dumps, ~93 MB | `validation/real_world/scripts/run_corpus.py` on the pinned clones |
| `demo/video/*.mp4` | binary; the video is hosted on YouTube | the public video URL is referenced from `demo/README.md`; the subtitle track is tracked |
| prebuilt image | build artifact, not source | `docker pull ghcr.io/furovandrew/docassay:1.0` (digest in `MANIFEST.md`) |
| `<private-archive>/`, `other_instruments/`, `test_repos/`, `validation_repos/`, `annotation_repos/` | private predecessor tree, local comparison instruments and working checkouts used during construction | not part of the artifact; historical records name these paths as provenance labels, not links |

## Third-party material

The exemplar bank contains short quotations and patch excerpts from public
commits in third-party repositories. Each record names the source repository and
commit URL. Those excerpts remain under the source repository's licence and are
research data, not part of the MIT-licensed software. See the repository
`THIRD_PARTY_NOTICES.md` and `injected_gold/llm_injection/exemplars/`.

## Historical provenance

The frozen runs record the engine tree hashes they were produced with. The
current public tree is a later commit; `evidence/stage-c/verification.json`
records the pre-release and release hashes and the re-score that proved
the claim dumps byte-identical. The freeze can be verified against the current
tree with the commands in `REPRODUCING.md`.
