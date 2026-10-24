# Demonstration material

## Demonstration video

The 3–5 minute video required by the track is hosted on YouTube:

<https://www.youtube.com/watch?v=aLjg3uMwGXk>

The subtitle track is in `video/demo.srt` (and `video/demo.ass`).

## Run the prebuilt image

The demo image is published on GitHub Container Registry and built for both
`linux/amd64` and `linux/arm64`. It contains the tool, the prebuilt web UI and
the twelve-project corpus, so nothing is built and no mount is needed:

```bash
docker pull ghcr.io/furovandrew/docassay:1.0
docker run --rm --name docassay -p 8000:8000 ghcr.io/furovandrew/docassay:1.0
docker logs docassay | sed -n 's/^open: //p'   # open this URL
```

`docker pull` picks the architecture of the host, so both an x86_64 Linux
machine and an Apple Silicon one run natively. The digest is pinned in
`MANIFEST.md`; pull `ghcr.io/furovandrew/docassay@sha256:…` when the exact
bytes matter.

Open the printed URL, or the plain `http://localhost:8000/` — the container
redirects a local Host to the token address, so reloads and new tabs work. The
token still gates the API; a non-local `Host` is never redirected.

For another port, add `-p 8010:8010 -e DOCASSAY_PORT=8010` and use
`http://localhost:8010/`.

## Build the image from source

The public code repository keeps the tool image corpus-free. Build it from the
repository root, then add the demo corpus from this directory:

```bash
# 1. tool image, from the public code checkout
docker build -t docassay:base .

# 2. demo layer, from this directory
docker build -f Dockerfile.demo --build-arg BASE=docassay:base -t docassay:demo .
docker run --rm -p 8000:8000 docassay:demo
```

The UI lists twelve projects from `demo/corpus/`. Each one is a frozen Stage B
or Stage C project with a single injected drift, so the corpus reproduces the
paper's setting rather than a clean baseline: every project carries exactly one
refuted claim (two in `serialscope`), and the drift classes are spread across
the corpus.

| project | corpus | injected drift | refuted claim |
|---|---|---|---|
| `contourkit` | Stage C | path-location | `PATH_EXISTS docs/walkthrough.md` |
| `tileplan` | Stage C | removed referent | `SYMBOL_EXISTS tileplan.quadkey.from_quadkey` |
| `morpheme` | Stage C | identifier | `SYMBOL_EXISTS morpheme.cli.format_alignment` |
| `bibscan` | Stage C | external dependency | `DEPENDENCY python-dateutil` |
| `serialscope` | Stage C | path-location | `PATH_EXISTS examples/pump_response.txt`, `pump_response.txt` |
| `sensorbus` | Stage C | path-location | `PATH_EXISTS examples/curve_nitrate.csv` |
| `gaugekit` | Stage B | external dependency | `DEPENDENCY numpy` |
| `gridwatch` | Stage B | identifier | `SYMBOL_EXISTS gridwatch.readers.read_json` |
| `palette` | Stage B | path-location | `PATH_EXISTS docs/guide.md` |
| `plotline` | Stage B | removed referent | `SYMBOL_EXISTS plotline.scales.nice_ticks` |
| `recipecard` | Stage B | external dependency | `DEPENDENCY click` |
| `sheetmusic` | Stage B | identifier | `SYMBOL_EXISTS sheetmusic.parser.parse_chord` |

Stage C is the corpus the paper validates on, so the numbers in Table 1 are
reachable from these projects; Stage B is a disjoint reference corpus for a live
"other domains" walk.

Projects are listed before they are analysed: `/api/repos` reports
`analyzed: false`, and the pipeline for a project runs the first time you open
it (live log and timer in the UI, sub-second on the demo corpus). The result is
cached in `/home/app/.local/share/docassay`, so later visits are instant.

Nothing needs network access on first load. To analyse another repository:

- upload a zip in the UI; or
- paste a repository URL (the container clones it); or
- mount a directory and allow it explicitly:

```bash
docker run --rm -p 8000:8000 \
  -v "$PWD/my-repo:/repos/my-repo:ro" \
  ghcr.io/furovandrew/docassay:1.0 \
  web --host 0.0.0.0 --static /app/web/dist \
    --corpus /app/demo_corpus --corpus /repos \
    --allow-root /app/demo_corpus --allow-root /repos \
    --allowed-host "*" --allow-bare-index
```

## Run with compose

```bash
docker compose -f research/submission/demo/demo/docker-compose.yml up
# another port:
DOCASSAY_PORT=8010 docker compose -f research/submission/demo/demo/docker-compose.yml up
```

## Suggested 3-minute walkthrough (matches the video)

1. **Claim → code in one click.** Open `contourkit`, filter to
   `PATH_EXISTS`, and open the `REFUTED` card for `docs/walkthrough.md`: the
   provenance chain runs from the documentation line to the missing listing
   entry.
2. **Abstention is visible.** Filter to `SYMBOL_EXISTS` and open a `NEI`: the
   card names the layer (`CLAIM_GATE` / `WORLD` / `DECIDABILITY`) and the
   verbatim reason. This is the difference from a binary flag.
3. **The same inventory, for an agent.** In a terminal:
   `docker exec -it docassay docassay mcp --repo /app/demo_corpus/bibscan`
   and show a tool call returning a verdict with provenance. The image installs
   the `agent` extra, so the server starts from the container's `.venv`; the
   first tool call answers in well under a second on a demo-corpus project.
   The bare command looks idle by design — see the next section for how to make
   a call visible without an agent.
4. **Scale.** Open `gridwatch` — the same interface on a different domain and corpus.

## The MCP server looks idle until a client asks

`docker exec -it docassay docassay mcp --repo …` starts a stdio server: it
speaks JSON-RPC on stdin and prints nothing until a client sends `initialize`,
so running it by hand looks like a hang. The image still ships it, and the
`agent` extra is installed there — you only need something on the other end.

**Point a client at it** (Claude Code / Cursor entry; OpenCode uses
`mcp.servers` with `"type": "local"`, see the root `README.md`):

```json
{
  "mcpServers": {
    "docassay-demo": {
      "command": "docker",
      "args": ["exec", "-i", "docassay", "docassay", "mcp", "--repo", "/app/demo_corpus/bibscan"]
    }
  }
}
```

**Drive one call by hand.** The `sleep`s keep stdin open long enough for the
server to answer; without them the process can exit on EOF first:

```bash
{ echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"probe","version":"0"}}}'
  sleep 1; echo '{"jsonrpc":"2.0","method":"notifications/initialized"}'
  sleep 1; echo '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"verify_claim","arguments":{"claim":"The project depends on lxml."}}}'
  sleep 3; } | docker exec -i docassay docassay mcp --repo /app/demo_corpus/bibscan
```

The reply is `serverInfo {"name":"docassay","version":"0.1.0"}` plus the server
instructions, then `"status": "SUPPORTED"` with
`"supporting": ["lxml:pyproject.toml:>=4.9"]` and the manifest line. The server
advertises `list_facts`, `verify_claim`, `lookup`, `project_metadata` and the
`repo://summary` resource (counts, licences, dependencies, infra flags); the full
inventory is paged through `list_facts`, not returned as one document.

## Files

| file | purpose |
|---|---|
| `Dockerfile` (public code repository root) | two-stage build: SPA, then the tool; no baked corpus |
| `Dockerfile.demo` | adds `corpus/` on top of the public image, so the demo runs without a mount |
| `docker-compose.yml` | local run of the demo image with a persistent analysis cache |
| `corpus/` | twelve Stage B + Stage C demo projects with one injected drift each, baked at `/app/demo_corpus` |
| `video/` | subtitle track for the demonstration video; the video itself is hosted on YouTube |
