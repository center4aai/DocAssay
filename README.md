**DocAssay** (`docassay`) is a local-first **symbolic verifier** of
natural-language claims in repository documentation. It checks claims against a
deterministic fact inventory harvested from the code, with explicit abstention
(`NEI`) where the evidence is not conclusive. Because the same inventory is a
ground-truth description of the repository, the tool doubles as a
**deterministic source of truth for coding agents** (see "Use as an agent's
source of truth" below). The verdict path is free of LLMs.

## What DocAssay does

- scans a repository's documentation and code inventory;
- extracts claims by a fixed predicate vocabulary (anchor-first, deterministic);
- matches each claim against a deterministic fact inventory (manifests, file
  listing, AST);
- returns `SUPPORTED / REFUTED / NEI` verdicts per assertion;
- reports provenance: which facts support or refute each verdict.

## What works today

Predicate layer (`src/docassay/predicates/`):

- `DEPENDENCY` (closed-world over manifest: presence → SUPPORTED, negation →
  REFUTED, version → not-contradiction; undeclared → NEI).
- `PATH_EXISTS` (closed-world over the project file+directory listing: a stale
  **anchored** path reference is REFUTED. Anchors: a backtick-quoted path or
  directory, a `the \`X\` directory` phrase, a **Markdown link/image target**,
  or a framed bare `name.ext`. A bare `dir/name.ext` in prose is not anchored
  and forms no claim).
- `SYMBOL_EXISTS` (closed-world over the project Python AST: modules, classes,
  functions, methods, fields; third-party and bare-call mentions abstain).
- `LICENSE` (closed-world over the manifest license field + `LICENSE` file: a
  claimed license that contradicts the declared one → REFUTED).
- `HAS_DOCKERFILE` / `HAS_CI_WORKFLOW` (closed-world over the listing: a stale
  reference to a `Dockerfile` or to CI tooling is refuted by its absence).

## Fast start

From a checkout of this repository:

```bash
uv sync

uv run docassay analyze /path/to/repo
uv run docassay dump /path/to/repo /tmp/claims.jsonl
```

## Use as an agent's source of truth

A coding agent can ask the tool for facts about the repository instead of
guessing them. The inventory is exposed over the **Model Context Protocol**: the
answers are the same deterministic, LLM-free verdicts the CLI reports, each with
source provenance.

```bash
uv sync --extra agent
uv run docassay mcp --repo /path/to/repo   # serves over stdio
```

Tools: `list_facts(predicate?, limit?)`, `verify_claim(claim)`,
`lookup(predicate, name)`, `project_metadata()`; plus the `repo://summary`
resource with the project-level metadata (counts, licences, dependencies, infra).
The full inventory is paged through `list_facts` on purpose: on a large
repository it reaches tens of megabytes, so it is never dumped as one resource.

For **Claude Code / Cursor** (`mcpServers` format):

```json
{
  "mcpServers": {
    "docassay": {
      "command": "uv",
      "args": ["run", "docassay", "mcp", "--repo", "/path/to/repo"]
    }
  }
}
```

For **OpenCode V2** (or just run `opencode mcp add docassay -- uv run docassay mcp --repo .`):

```jsonc
{
  "mcp": {
    "servers": {
      "docassay": {
        "type": "local",
        "command": ["uv", "run", "docassay", "mcp", "--repo", "."]
      }
    }
  }
}
```

Tools then appear as `docassay_list_facts`, `docassay_verify_claim`,
`docassay_lookup`, `docassay_project_metadata` (or under
`tools.docassay.*` in Code Mode), and the resource as `repo://summary`.

The same surface is available from Python (`docassay.api`):

```python
from docassay.api import Oracle

oracle = Oracle("/path/to/repo")
oracle.verify_claim("The project depends on requests.")  # SUPPORTED / REFUTED / NEI
oracle.lookup("SYMBOL_EXISTS", "Klass")                  # facts with provenance
oracle.project_metadata()                                # license, deps, infra
```

## Web UI

The same analysis pipeline, but in the browser: clone a URL, upload a zip, or
analyze a local path, then inspect verdicts, claims, evidence and provenance
with a live pipeline log.

### Run it — no npm, no build step

The prebuilt frontend is committed under `web/dist/` and served by the backend,
so **you do not need Node, npm, or any frontend build** to use the web UI:

```bash
uv sync --extra web
uv run docassay web
# prints: open: http://127.0.0.1:8000/?token=…  — open that address
```

The server serves the API and the static UI from one process. Useful options:

```bash
uv run docassay web --port 8000                      # bind to localhost
uv run docassay web --port 8010                      # bind another port
DOCASSAY_PORT=8010 uv run docassay web               # same, via environment
uv run docassay web --corpus /path/to/corpus        # extra corpus repos
uv run docassay web --allow-root /path/to/checkouts  # allow local path analysis
```

Security model: the API is same-origin (no CORS), and every `/api` request must
carry a session token. The token is part of the start address printed at
startup (`/?token=…`); the UI moves it into session storage on first load and
never receives it from the server otherwise. On loopback the server redirects a
bare `http://127.0.0.1:8000/` — or an address carrying a token from an earlier
run — to the current printed address, so bookmarks, new tabs and reloads keep
working; when bound to another interface the printed URL stays mandatory. A
container that publishes the UI on `localhost` can pass `--allow-bare-index`,
which also treats a loopback `Host` header as local (the browser's connection
arrives through the bridge, not from 127.0.0.1). For scripted/curl access send
the token as `X-Session-Token`. The server answers only its own `Host` values
(the loopback names, or the bind address plus `--allowed-host` values when
bound to another interface). Repository URLs are cloned over `https://` only.

Local **path** analysis is available on loopback (`127.0.0.1`, `localhost`,
`::1`) by default. Binding a non-loopback host (`--host 0.0.0.0`) disables it
unless you whitelist roots with `--allow-root` (repeatable); clone and zip
upload still work because they run in a server-owned directory.

### Run in Docker

The published demo image is `ghcr.io/furovandrew/docassay:1.0` (it includes the
frozen demo corpus). The commands below build the corpus-free base image
locally; it serves the same prebuilt UI and ships no corpus, so mount one (or
use the upload and clone paths in the browser):

```bash
docker build -t docassay:base .
docker run --rm -p 8000:8000 \
  -v "$PWD/my-repo:/repos/my-repo:ro" \
  docassay:base \
  web --host 0.0.0.0 --static /app/web/dist \
    --corpus /repos --allow-root /repos \
    --allowed-host "*" --allow-bare-index
docker logs <container-id> | grep -o 'http://[^ ]*token=[^ ]*'   # open this URL
```

Binding a non-loopback host disables local path analysis unless the root is
whitelisted with `--allow-root`, which the command above does for the mount. The
image installs the `agent` extra too, so `docker exec -it <container-id>
docassay mcp --repo /repos/my-repo` serves the MCP tools from the container.

### Rebuilding the frontend (developers only)

npm is needed **only** when changing the React frontend. For hot-reload
development, start the backend and the Vite dev server together:

```bash
uv run docassay web          # terminal 1 (API on :8000, prints the token)
cd web && npm install && npm run dev # terminal 2 (UI on :5173, proxies /api)
# open http://localhost:5173/?token=<token printed in terminal 1>
```

After frontend changes, regenerate the committed bundle that the server serves:

```bash
cd web && npm run build
```

> Note: when installed as a package (e.g. `uv tool install` / `pip install`),
> the built frontend is not bundled into the wheel, so the web UI is guaranteed
> to run from a git checkout. If you need a fully self-contained installed UI,
> install from this checkout and point `--static` at `web/dist`.

## Primary workflows

### `analyze`

Print a verdict summary for a repository:

```bash
uv run docassay analyze /path/to/repo
```

Output includes code verdicts (SUPPORTED/REFUTED/NEI), resolved count and
coverage.

### CI and pre-commit

`analyze` can fail a build and report findings in SARIF 2.1.0 (one result per
refuted claim, located at the documentation line, with the refuting inventory
lines as related locations):

```bash
uv run docassay analyze --format sarif --output docassay.sarif --fail-on refuted .
```

`--fail-on refuted` exits with status 1 when any claim is refuted (`NEI` never
fails a build). The repository also ships a pre-commit hook
(`.pre-commit-hooks.yaml`, hook id `docassay`) that runs the same check.

### `dump`

Dump every claim with its verdict and provenance to JSONL:

```bash
uv run docassay dump /path/to/repo /tmp/claims.jsonl
```

## Research artifact

The paper, frozen corpora, experiment scripts, run trees and the evidence map
are distributed separately from this code repository. The tool tree is
unchanged.

## Verdict semantics

- `SUPPORTED` — claim confirmed by inventory facts.
- `REFUTED` — claim contradicted by inventory facts.
- `NEI` — abstention: evidence absent or inconclusive (open world, or
  negation without counter-evidence).

## Development

```bash
uv sync --group dev
uv run pytest            # runs src/docassay/tests
uv run ruff check src/   # lint
```

## Notes

- Python 3.12+ is required; `uv` is the supported dependency manager.
- No runtime dependencies; the verdict path is deterministic and offline.
- No LLM is used in the deciding path; the shipped extractor is the
  deterministic anchor-first regex. The claim schema reserves an
  `extraction_source` field for a future, opt-in LLM fallback, which is not
  wired in the current release.

## License

MIT. See `LICENSE` and `THIRD_PARTY_NOTICES.md`.