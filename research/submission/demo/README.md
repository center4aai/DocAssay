# DocAssay demo artifact

**Artifact:** this repository (tool, Dockerfile, frozen corpora, experiment tree)

This directory is the demo artifact. The tool, the frozen
corpora, the experiment scripts, the run trees needed to replay the reported
numbers and the evidence map are all here. Everything needed is included here.

The only material that is not included is either large and derived (the pinned
real-world clones) or binary and hosted elsewhere (the demonstration video and
the prebuilt Docker image). Their locations are listed in
[`MANIFEST.md`](MANIFEST.md).

---

## 1. What the artifact is

`DocAssay` (`src/docassay`) is a local-first symbolic verifier of
factual claims in repository documentation. It extracts claims with a fixed,
anchor-first predicate vocabulary and adjudicates each one against a
deterministic fact inventory (manifest, tracked file listing, static AST). Every
verdict is `SUPPORTED`, `REFUTED` or `NEI`, with document and code provenance.
No language model is in the deciding path.

- 0 runtime dependencies; Python ≥ 3.12
- CLI (`analyze`, `dump`, `export`, `export-md`, `corpus-md`, `report`, `review`,
  `consolidate`, `mcp`), SARIF output, MCP server, web UI
- 659 tests pass (11 xfailed) in < 5 s

## 2. Run it

### Prebuilt image (recommended)

The image is available on GitHub Container Registry for `linux/amd64` and
`linux/arm64`, so nothing is built during review:

```bash
docker pull ghcr.io/furovandrew/docassay:1.0
docker run --rm --name docassay -p 8000:8000 ghcr.io/furovandrew/docassay:1.0
docker logs docassay | sed -n 's/^open: //p'   # open this URL
```

The image contains the tool, the prebuilt web UI and the frozen demo corpus.
`docker pull` picks the host architecture; `MANIFEST.md` pins the digest for a
byte-identical review.

The server binds a random session token and prints the address that carries it.
A plain `http://localhost:8000/` (or the port you exposed) redirects to that
address, so reloads and new tabs keep working; the token is also printed in
`docker logs`. The token still gates the API: no CORS headers are emitted and a
non-local `Host` is never redirected.

To use another port:

```bash
# same port in the container and on the host
docker run --rm -p 8010:8010 -e DOCASSAY_PORT=8010 \
  --name docassay ghcr.io/furovandrew/docassay:1.0
```

### Build it from source

The tool image is corpus-free. Build it from the repository root, then add the
demo corpus from this directory:

```bash
# 1. tool image, from the repository root
docker build -t docassay:base .

# 2. demo layer, from this directory
cd research/submission/demo/demo
docker build -f Dockerfile.demo --build-arg BASE=docassay:base -t docassay:demo .
docker run --rm -p 8000:8000 docassay:demo
```

### The demo corpus

The image ships a demo corpus, so the UI is populated on first load with no
network access and no repository clone. Twelve projects are listed flat, each
carrying one verified drift, so the UI shows refuted claims out of the box:

- **Stage C** (the corpus the reported results are based on): `contourkit`, `tileplan`,
  `morpheme`, `bibscan`, `serialscope`, `sensorbus`;
- **Stage B** (a disjoint reference corpus): `gaugekit`, `gridwatch`, `palette`,
  `plotline`, `recipecard`, `sheetmusic`.

To analyse another repository, either upload a zip in the UI or paste a URL
(network available in the container), or mount a directory and add a second
corpus root:

```bash
docker run --rm -p 8000:8000 \
  -v "$PWD/my-repo:/repos/my-repo:ro" \
  ghcr.io/furovandrew/docassay:1.0 \
  web --host 0.0.0.0 --static /app/web/dist \
    --corpus /app/demo_corpus --corpus /repos \
    --allow-root /app/demo_corpus --allow-root /repos \
    --allowed-host "*" --allow-bare-index
```

From source, if a reader prefers no Docker at all (the built frontend is
committed, so no Node is needed):

```bash
uv sync --extra web
uv run docassay web --corpus research/submission/demo/demo/corpus
```

## 3. Where the numbers come from

Every reported number traces to a file here. The mapping is in
`evidence/README.md`; the two entry points are:

| reported element | source |
|---|---|
| Stage C conformance table | `evidence/stage-c/report.md` (T2, T3, T9, T10), `metrics_stage_c.json` |
| LLM confirmation of the Stage C number | `evidence/stage-c/annotation_agreement.md` (T14) |
| freeze / provenance statement | `evidence/stage-c/verification.json`, `scope_engine_freeze.json` in the run |
| real-repository candidates | `evidence/real-world/aggregate-2026-10-21.md` |

The authoritative Stage C run tree is
`injected_gold/llm_injection/runs/stage-c-2026-10-20/`. The copies under
`evidence/` are curated for reading; if a copy and the run disagree, the run
wins.

## 4. How the validation was designed

Normative documents, unchanged in role:

| document | role |
|---|---|
| `validation/SCOPE.md` | the drift types and conditions the tool commits to detecting |
| `validation/protocol.md` | how detection is measured; §5.1 defines the headline estimand |
| `validation/stage-c-plan.md` | the pre-registered Stage C plan, plus amendment A1 |
| `validation/retrospective.md` | what was tried, kept and rejected, and why |

The evaluation is an **injection-based conformance test**: known defects are
manufactured in a frozen corpus, proven on disk by an engine-free oracle, and
the tool's reaction is measured in the baseline→injected finding diff. It is not
an open-world benchmark and makes no population estimate.

## 5. Known limitations

- **Recall on the declared scope is the strong result; refutation precision on
  organic documentation is the stated cost.** The tool abstains a lot. On 16
  popular repositories, 32 of 284 adjudicated candidates are confirmed drift
  (11.3%); the rest are predicate false positives, tutorial examples, generated
  artifacts or historical statements. Confirmed findings are listed with their
  git evidence in `evidence/real-world/confirmed.md`.
- The Stage C corpus is synthetic and LLM-generated (6 repositories, 3 domains,
  18 documents, 69 verified injections, 46 distinct artifacts). Results are
  descriptive for that corpus; no generalisation is claimed.
- Bare symbol names are never refuted by policy; they abstain. `NEI` is counted
  as detection under the tool's KPI, and a conservative bound that counts only
  legitimate abstentions is reported next to it.
- Six repository clusters: the bootstrap interval is descriptive and may be
  degenerate.

## 6. Reproduction

```bash
uv run pytest -q
B=research/submission/demo/injected_gold
PYTHONPATH=src uv run python $B/scripts/freeze_scope_engine.py \
    --verify --freeze $B/llm_injection/runs/stage-c-2026-10-20/scope_engine_freeze.json
PYTHONPATH=src uv run python $B/scripts/freeze_corpus.py \
    --verify --freeze $B/llm_injection/runs/stage-c-2026-10-20/corpus_freeze.json
```

The frozen snapshots, the injected manifests and the scoring scripts required for
a byte-level replay are in
`injected_gold/llm_injection/runs/stage-c-2026-10-20/`. The per-repository
real-world runs ship their findings, staleness attribution and reports; their
full claim dumps are derived and can be regenerated from the pinned clones.

See `REPRODUCING.md` for the experiment-by-experiment matrix: what reproduces
byte-identically, what needs the network (the real-world clones), and what is
not bit-reproducible (LLM generation/annotation and Stage A).

## 7. Licences

- Software: MIT, see the repository `LICENSE`.
- Synthetic corpora, frozen run data and evidence: CC BY 4.0, see
  `DATA-LICENSE.md`.
- Short quotations and patch excerpts from third-party repositories remain under
  the source repository's licence; each record names its source and commit.

## 8. Data Availability

The artifact is archived with this repository. The code is MIT-licensed; the
frozen data are CC BY 4.0. The real-world corpus is identified by URL and commit
in `validation/real_world/corpus.lock.json` and is fetched with
`validation/real_world/scripts/fetch_corpus.py`, so third-party repositories are
not redistributed.
