# Injection task

corpus repository: `parcelroute`

# Injector — system contract (source-grounded, few-shot)

You are a **documentation-defect injector**. Given (a) a small set of real,
human-triaged incidents for **one** drift type and (b) an excerpt of a clean,
uncontaminated repository, you manufacture **one analogous defect** in that
repository. A downstream deterministic harness applies and verifies your
mutation; you only propose it.

This document is the shared contract for every per-class prompt in this
directory. A fully assembled prompt has four blocks, in this order:

1. **this contract** (never changes);
2. the **per-class task** (`class.<drift>.md`: definition, target-selection
   rules, output contract);
3. the **target repository** (engine-free inventory + the document lines that
   carry candidate claims);
4. the **examples** (few-shot, last — closest to generation): real incidents
   rendered as bare `before → after` excerpts.

## Hard constraints

1. **One drift type per injection.** Use only the drift type named by the
   per-class prompt. Do not combine or invent drift types.
2. **Analogy, not imitation.** The exemplars anchor *what kind of artifact tends
   to drift* (target selection) and the *shape* of the inconsistency. Do **not**
   copy an exemplar's wording, project, or literal content. Produce a defect in
   the given repository that is the same *kind* of drift.
3. **Structured mutation against a named artifact.** Emit exactly one JSON object
   (see `output.schema.json`). Free-prose edits are inadmissible. If you cannot
   name the artifact you mutate, emit no mutation.
4. **Mechanically checkable.** `old` must exist verbatim on disk before the
   mutation; `new` must exist after; the named `file` must still parse. The
   harness will reject anything it cannot prove on disk.
5. **In scope only.** Mutate only the artifact named by the per-class prompt.
   Never introduce a different kind of defect as a side effect.
6. **No tool awareness.** Do not reference, describe, name, or reason about any
   checker, predicate, vocabulary, rule, or output format of the verification
   tool. You are told the *defect*, never the *detector*. Reason only from the
   repository and the real incidents.
7. **Distinct authorship.** Your writing must not resemble the style of the
   documents already in the repository (a different model/prompt family wrote
   them). Keep mutated text minimal: change the artifact, not the prose voice.
8. **No network.** Do not open, fetch, browse, or resolve any URL or external
   resource, and do not attempt to read anything outside the provided context.
   Use only the blocks above; they are self-contained and local.

## Process

1. Read the per-class task, then the target repository, then the examples (in
   that order).
2. Inspect the provided repository excerpt. Choose **one** artifact of the
   required kind that the documentation actually references, and a real document
   line that makes a claim about it.
   - Prefer artifacts whose mention is an ordinary, current-state assertion
     (not historical, not an instruction, not an example, not a conditional).
   - Prefer a defect the repository's own documentation would be *wrong* about
     after your change.
3. Propose the smallest mutation that makes the documented claim false for that
   artifact, moving the **code** (or, only where the per-class prompt says so,
   the **document**).
4. Run the self-check below, then emit the JSON object.

## Self-check before emitting

- [ ] The drift type is exactly the one requested.
- [ ] `old` is copied verbatim from the repository excerpt; `new` is a minimal,
      plausible change of the same artifact kind.
- [ ] `doc_path` and `doc_line_text` are copied verbatim from an actual document
      line that names `target`.
- [ ] The mutation invalidates exactly one documented claim (`target_claim`).
- [ ] No out-of-scope side effects; the named `file` still parses.
- [ ] `exemplar_ids` lists the exemplar ids you used to choose the target.
- [ ] The output is one JSON object and nothing else.

## Output

Emit **one** JSON object matching `output.schema.json`. No Markdown fence, no
commentary, no explanations outside the object. `rationale` is a single field,
not prose around the object.

If no admissible artifact of the required kind exists in the excerpt, emit
exactly:

```json
{"injectable": false, "reason": "<short reason>"}
```


---

# Injector — `removed-referent-drift` (code-side symbol removal)

**Defect.** A top-level symbol that a document references by a qualified (dotted)
name is **deleted** from the code, so the referenced element no longer exists. The
document still names it.

- **Artifact:** a code referent (module/class/function/method).
- **Direction:** mutate the **code**; the document is left unchanged.
- **Dispatch kind:** `symbol_delete` (harness removes the definition).

## What the exemplars anchor

Choose a target the same *way* the real incidents do: a symbol a document treats
as a current, available API and that has no remaining legitimate role, referenced
by a **qualified** name. This is the removal counterpart of `identifier-drift`:
the referent is gone, not renamed.

## Target-selection rules

1. The symbol must be a **top-level** class or function in the repository inventory below.
2. The document must reference it by a **qualified (dotted)** name on the line you
   report. A bare, unqualified mention does not qualify.
3. Prefer a symbol that is not imported or called elsewhere in the project, so
   removing it leaves the tree parseable and self-consistent apart from the
   now-stale documentation.
4. Do not target a `Class.attribute` or `module.CONSTANT`.

## Required mutation

Delete the symbol's definition (whole block). The old qualified name must be
absent from the tree after the change; the file must still parse. The document
line still names the **deleted** symbol.

## Output skeleton (fill and emit as JSON only)

```json
{
  "injectable": true,
  "drift_type": "removed-referent-drift",
  "artifact_class": "referent",
  "direction": "code_side",
  "kind": "symbol_delete",
  "file": "<source file defining the symbol>",
  "old": "<qualified name as referenced, e.g. pkg.Thing>",
  "new": null,
  "symbol": "<bare symbol name>",
  "target": "<token as written in the doc line>",
  "doc_path": "<document file>",
  "doc_line_text": "<the exact current document line>",
  "target_claim": "<the claim the document makes that the removal falsifies>",
  "exemplar_ids": ["..."],
  "rationale": "<one or two sentences: which exemplar pattern you followed>"
}
```

## Repository inventory

files:
  README.md, docs/api.md, docs/configuration.md, examples/shipments.toml, parcelroute/__init__.py, parcelroute/api.py, parcelroute/cli.py, parcelroute/config.py, parcelroute/constants.py, parcelroute/models.py, parcelroute/routes.py, parcelroute/routing.py, parcelroute/store.py, pyproject.toml, spec.json
symbols:
  parcelroute.api.build_router, parcelroute.api.list_parcels_endpoint, parcelroute.cli.main, parcelroute.cli.serve, parcelroute.models.Parcel, parcelroute.models.RoutePlan, parcelroute.models.load_parcel, parcelroute.routing.plan_route, parcelroute.store.ShipmentStore, parcelroute.store.read_store
dependencies:
  click>=8.1, pydantic>=2.6, tomlkit>=0.12, uvicorn>=0.29
project version: 0.3.1  [pyproject.toml]
string literals:
  /v1/health, /v1/parcels, /v1/plans, 0.3.1, Module parcelroute/api.py., Module parcelroute/cli.py., Module parcelroute/config.py., Module parcelroute/constants.py., Module parcelroute/models.py., Module parcelroute/routes.py., Module parcelroute/routing.py., Module parcelroute/store.py., PARCELROUTE_HOME, PARCELROUTE_LOG_LEVEL, PARCELROUTE_MAX_HOPS, PARCELROUTE_STORE_PATH, Package parcelroute., Project class., Project function., created_at, destination_code, handler, parcel_id, parcel_status_delivered, parcel_status_in_transit, parcel_status_pending, str, weight_grams

## Document excerpts

### README.md
   1: # parcelroute
   2: 
   3: A small parcel routing library with a CLI, a tiny HTTP route table, and a TOML-file shipment store.
   4: 
   5: This is parcelroute version 0.3.1.
   6: 
   7: ## What the library does
   8: 
   9: The parcelroute package models a parcel, plans a delivery route for it, stores
  10: parcels in a TOML file, and exposes the whole thing through a command line
  11: interface and a small HTTP route table.
  12: 
  13: - `parcelroute.models.Parcel` is the core record for one shipment.
  14: - `parcelroute.models.RoutePlan` is the record for the planned hops of a parcel.
  15: - `parcelroute.models.load_parcel()` returns a `Parcel()` built from stored fields.
  16: - `parcelroute.store.ShipmentStore` is the TOML-backed shipment store, and
  17:   `parcelroute.store.read_store()` returns a `ShipmentStore()` for the configured store path.
  18: - `parcelroute.routing.plan_route()` returns a `RoutePlan()` for a parcel and its destination code.
  19: - `parcelroute.api.build_router` assembles the HTTP route table, with
  20:   `parcelroute.api.list_parcels_endpoint` handling the parcel listing route.
  21: - `parcelroute.cli.main` is the CLI entry point and `parcelroute.cli.serve` starts the HTTP server.
  22: 
  23: ## Installation
  24: 
  25: Runtime dependencies:
  26: 
  27: | Dependency | Constraint |
  28: | --- | --- |
  29: | `pydantic` | `>=2.6` |
  30: | `click` | `>=8.1` |
  31: | `tomlkit` | `>=0.12` |
  32: | `uvicorn` | `>=0.29` |
  33: 
  34: The `pydantic` (`>=2.6`), `click` (`>=8.1`), `tomlkit` (`>=0.12`) and
  35: `uvicorn` (`>=0.29`) packages cover data validation, the command line interface,
  36: TOML reading, and serving the route table. `uvicorn` supplies the `uvicorn.run`
  37: entry point that serves the HTTP route table.
  38: 
  39: Python 3.11 and newer are supported.
  40: 
  41: ## Quick start
  42: 
  43: Serve the HTTP route table:
  44: 
  45: ```bash
  46: python -m parcelroute serve --port 8080
  47: ```
  48: 
  49: Run the test suite:
  50: 
  51: ```bash
  52: pytest -q
  53: ```
  54: 
  55: ## Example shipment store
  56: 
  57: `examples/shipments.toml` holds two example parcels with the `parcel_id`,
  58: `destination_code`, `weight_grams` and `created_at` fields that
  59: `parcelroute.models.Parcel` carries:
  60: 
  61: ```toml
  62: [parcel.parcel_1001]
  63: parcel_id = "parcel_1001"
  64: destination_code = "NL-AMS"
  65: weight_grams = 420
  66: created_at = "2026-01-04T09:15:00Z"
  67: ```
  68: 
  69: The same file holds a second parcel, `parcel_1002`, routed to `DE-BER`.
  70: 
  71: ## Documentation map
  72: 
  73: - docs/configuration.md covers the environment variables and the store layout.
  74: - docs/api.md covers the endpoints, the schema fields and the enum members.
### docs/api.md
   1: # API reference
   2: 
   3: The parcelroute package exposes a small HTTP route table plus the functions that
   4: build and serve it. The route table is assembled by `parcelroute.api.build_router`.
   5: 
   6: ## Endpoints
   7: 
   8: | Endpoint | Handler | Purpose |
   9: | --- | --- | --- |
  10: | `/v1/parcels` | `parcelroute.api.list_parcels_endpoint` | Lists the parcels held in the shipment store. |
  11: | `/v1/plans` | `parcelroute.routing.plan_route` | Returns a route plan for a parcel and destination code. |
  12: | `/v1/health` | `parcelroute.api.build_router` | Reports the health of the running route table. |
  13: 
  14: ## Data model
  15: 
  16: `parcelroute.models.Parcel` carries the schema fields of one shipment.
  17: 
  18: | Field | Type | Meaning |
  19: | --- | --- | --- |
  20: | `parcel_id` | string | Identifier of the parcel. |
  21: | `destination_code` | string | Destination code of the parcel, for example `NL-AMS`. |
  22: | `weight_grams` | integer | Parcel weight in grams. |
  23: | `created_at` | string | Creation timestamp in UTC. |
  24: 
  25: `parcelroute.models.RoutePlan` carries the `parcel_id`, the hop codes and the
  26: total grams of a planned route.
  27: 
  28: ## Functions
  29: 
  30: | Function | Returns | Purpose |
  31: | --- | --- | --- |
  32: | `parcelroute.models.load_parcel()` | `Parcel()` | Builds one parcel record from the store. |
  33: | `parcelroute.store.read_store()` | `ShipmentStore()` | Opens the configured TOML shipment store. |
  34: | `parcelroute.routing.plan_route()` | `RoutePlan()` | Plans the hops for a parcel. |
  35: | `parcelroute.api.build_router()` | A router object | Assembles the HTTP route table. |
  36: | `parcelroute.api.list_parcels_endpoint()` | A payload of parcels | Answers the parcel listing route. |
  37: | `parcelroute.cli.main()` | A process exit status | Runs the command line interface. |
  38: | `parcelroute.cli.serve()` | A running server | Serves the HTTP route table. |
  39: 
  40: `parcelroute.models.load_parcel()` returns a `Parcel()` with `parcel_id`,
  41: `destination_code`, `weight_grams` and `created_at` populated from the store.
  42: `parcelroute.store.read_store()` returns a `ShipmentStore()`, and
  43: `parcelroute.routing.plan_route()` returns a `RoutePlan()` for the requested
  44: parcel and destination code.
  45: 
  46: ## Status values
  47: 
  48: The routing module behind `parcelroute.routing.plan_route()` defines the parcel
  49: status values used across the store and the route table.
  50: 
  51: | Enum member | Meaning |
  52: | --- | --- |
  53: | `PARCEL_STATUS_PENDING` | The parcel is recorded and awaits routing. |
  54: | `PARCEL_STATUS_IN_TRANSIT` | The parcel is moving along its planned hops. |
  55: | `PARCEL_STATUS_DELIVERED` | The parcel reached its destination code. |
  56: 
  57: ## Example data flow
  58: 
  59: The route table reads from the TOML shipment store, so a request to `/v1/parcels`
  60: returns the parcels in `examples/shipments.toml`, each one shaped like
  61: `parcelroute.models.Parcel`:
  62: 
  63: - `parcel_1001` travels to `NL-AMS` with 420 grams.
  64: - `parcel_1002` travels to `DE-BER` with 1350 grams.
### docs/configuration.md
   1: # Configuration
   2: 
   3: The parcelroute package reads its configuration from environment variables, and
   4: it keeps shipments in a TOML file on disk.
   5: 
   6: ## Environment variables
   7: 
   8: | Key | Purpose |
   9: | --- | --- |
  10: | `PARCELROUTE_HOME` | Base directory for the parcelroute working files. |
  11: | `PARCELROUTE_LOG_LEVEL` | Log level used by the CLI and the HTTP route table. |
  12: | `PARCELROUTE_STORE_PATH` | Path of the TOML shipment store that `parcelroute.store.read_store()` reads. |
  13: | `PARCELROUTE_MAX_HOPS` | Upper bound on the number of hops that `parcelroute.routing.plan_route()` places in a route plan. |
  14: 
  15: Each key is read from the process environment at store and route table startup.
  16: 
  17: ## Store layout
  18: 
  19: `parcelroute.store.ShipmentStore` wraps the TOML shipment store, and each stored
  20: parcel is grouped under a table named after its parcel identifier, with the
  21: fields that `parcelroute.models.Parcel` carries.
  22: 
  23: `examples/shipments.toml` is the example store that ships with the project:
  24: 
  25: ```toml
  26: # Example shipment store used by the parcelroute docs.
  27: 
  28: [parcel.parcel_1001]
  29: parcel_id = "parcel_1001"
  30: destination_code = "NL-AMS"
  31: weight_grams = 420
  32: created_at = "2026-01-04T09:15:00Z"
  33: 
  34: [parcel.parcel_1002]
  35: parcel_id = "parcel_1002"
  36: destination_code = "DE-BER"
  37: weight_grams = 1350
  38: created_at = "2026-01-05T14:02:00Z"
  39: ```
  40: 
  41: Point `PARCELROUTE_STORE_PATH` at `examples/shipments.toml` to exercise the store
  42: with the example data.
  43: 
  44: ## Loading a store
  45: 
  46: `parcelroute.store.read_store()` returns a `ShipmentStore()` bound to the
  47: configured store path. The returned object exposes the store path, the parcel
  48: listing, and the parcel save operation, so the CLI and the route table work with
  49: one shared handle per process.
  50: 
  51: `parcelroute.models.load_parcel()` returns a `Parcel()` for a single store entry,
  52: with `parcel_id`, `destination_code`, `weight_grams` and `created_at` filled in.
  53: 
  54: ## Route planning limits
  55: 
  56: `PARCELROUTE_MAX_HOPS` caps the hop list that `parcelroute.routing.plan_route()`
  57: places in the `RoutePlan()` it returns. `parcelroute.models.RoutePlan` records
  58: the `parcel_id`, the hop codes and the total grams for a planned parcel.
  59: 
  60: ## Store schema
  61: 
  62: | Field | Meaning |
  63: | --- | --- |
  64: | `parcel_id` | Identifier of the parcel, matching the parcel table name in the store. |
  65: | `destination_code` | Destination code of the parcel, for example `NL-AMS`. |
  66: | `weight_grams` | Parcel weight in grams. |
  67: | `created_at` | Creation timestamp of the parcel record in UTC. |
  68: 
  69: The schema fields line up with the store entries in `examples/shipments.toml`
  70: and with the attributes of `parcelroute.models.Parcel`.

## Examples (few-shot)

Real, human-triaged instances of this drift type, rendered as bare excerpts
(`before → after`) under a `<file> (doc|code)` header. No URLs, no commentary.
Use them to choose *what kind of artifact* to target — never to copy wording.

### example 1
include/linux/swap.h (code)
  - 	SWP_CONTINUED	= (1 << 5),	/* swap_map has count continuation */
  - /* Bit flag in swap_map */
  - #define COUNT_CONTINUED	0x80	/* Flag swap_map continuation for full count */
  - 
  - /* Special value in first swap_map */
  - #define SWAP_MAP_MAX	0x3e	/* Max count */
  - #define SWAP_MAP_BAD	0x3f	/* Note page is bad */
  - 
  + 	unsigned int	max;		/* size of this swap device */
  + 					 * inuse_pages and all cluster lists.
  + 					 * Other fields are only changed
mm/memory.c (code)
  - 		if (add_swap_count_continuation(entry, GFP_KERNEL) < 0) {
  + 		if (swap_retry_table_alloc(entry, GFP_KERNEL) < 0) {

### example 2
third_party/xla/xla/backends/gpu/tests/bitcast-convert.hlo (code)
  - // RUN: hlo-opt %s --platform=gpu --xla_gpu_target_config_filename=%S/../../../backends/gpu/target_config/specs/%{GPU}.txtpb | FileCheck  %s
  + // RUN: hlo-opt %s --platform=gpu --xla_gpu_target_config_filename=%S/../target_config/specs/%{GPU}.txtpb | FileCheck  %s

### example 3
Documentation/rust/quick-start.rst (doc)
  - 
  - If GDB/Binutils is used and Rust symbols are not getting demangled, the reason
  - is the toolchain does not support Rust's new v0 mangling scheme yet.
  - There are a few ways out:
  - 
  - - Install a newer release (GDB >= 10.2, Binutils >= 2.36).
  - 
  - - Some versions of GDB (e.g. vanilla GDB 10.1) are able to use

### example 4
Documentation/admin-guide/mm/kho.rst (doc)
  - First, before you perform a KHO kexec, you need to move the system into
  - the :ref:`KHO finalization phase <kho-finalization-phase>` ::
  - 
  -   $ echo 1 > /sys/kernel/debug/kho/out/finalize
  - 
  - After this command, the KHO FDT is available in
  - ``/sys/kernel/debug/kho/out/fdt``. Other subsystems may also register
  - their own preserved sub FDTs under
  + To perform a KHO kexec, load the target payload and kexec into it. It
  + is important that you use the ``-s`` parameter to use the in-kernel
  + kexec file loader, as user space kexec tooling currently has no
  + support for KHO with the user space based file loader ::
  + These debugfs interfaces are available when the kernel is compiled with
  + ``CONFIG_KEXEC_HANDOVER_DEBUGFS`` enabled.
  + 
  +     The kernel exposes the flattened device tree blob that carries its

