# Injection task

corpus repository: `serialscope`

# Injector — natural documentation defects

You are given one documentation-drift type, a clean repository, and a few real
incident excerpts. Propose **one** concrete inconsistency between the
documentation and the repository, of exactly the requested type.

## Rules

1. **One drift type only.** Use the type named by the per-class task. Do not
   combine types or invent a new one.
2. **Choose a natural current-state statement.** Pick a statement in the
   documentation that a maintainer would treat as a current, checkable fact
   about the project — something a reader could rely on. Prefer ordinary
   present-tense statements. Avoid historical notes, examples, conditionals,
   proposals, and statements that are already ambiguous.
3. **Name a real artifact.** The statement must refer to something that actually
   exists in this repository: a file or directory, a class or function, or a
   dependency the project manifest lists. Do not invent anything.
4. **Make the smallest concrete change.** Change the artifact (or, only where
   the class says so, the document) in a way that makes the chosen statement
   false. The change must be a concrete edit to a named artifact: rename or move
   a file, rename or delete a class/function definition, or change/remove a
   dependency in the project manifest.
5. **Do not optimize for a checker.** Choose the target and the change the way a
   maintainer would, from the documentation and the repository. Do not reason
   about any analysis or verification tool, and do not avoid a natural target
   because you think some tool might miss it.
6. **If nothing fits, decline.** If the repository has no natural current-state
   statement of the requested type, return
   `{"injectable": false, "reason": "<short reason>"}`.
7. **Output exactly one JSON object.** No Markdown fence, no commentary, no
   text outside the object. The `rationale` field is a single short field, not
   prose around the object.

## Process

1. Read the per-class task.
2. Read the repository inventory and document excerpts.
3. Choose one statement and one artifact.
4. Check that the artifact exists and the document line is copied exactly.
5. Run the self-check, then emit the JSON object.

## Self-check

- [ ] The drift type is exactly the requested one.
- [ ] The chosen statement is a current-state statement, not historical,
      illustrative, conditional, or already ambiguous.
- [ ] The artifact exists in the repository under the name used.
- [ ] `doc_path` and `doc_line_text` are copied verbatim from the document.
- [ ] The change is minimal and makes exactly that statement false.
- [ ] The named file still parses after the change.
- [ ] No other kind of defect is introduced as a side effect.
- [ ] `exemplar_ids` lists the exemplar ids that informed target selection.


---

# Injector — external-dependency drift

**Defect.** A document presents a third-party dependency as a current
requirement, but the project manifest is changed so that the dependency no longer
satisfies the documented requirement, or the dependency is removed while the
document still names it.

- **Artifact:** a dependency listed in the project manifest.
- **Direction:** change the manifest; leave the document unchanged.

## What to look for

Choose a statement that presents a dependency as a current requirement. If the
document states a version requirement, use the constraint form of the mutation.
If it only names the dependency as something the project uses, use the removal
form.

The mutation edits the project manifest (`pyproject.toml`, `setup.cfg`,
`setup.py`, or `requirements*.txt`), so the dependency must be one the manifest
actually lists; otherwise there is nothing to change. This is a property of the
edit, not a rule about how the document should be written.

## The change

- **Constraint form:** change the manifest constraint to a clearly
  non-overlapping bound (for example `>=999`). The new constraint must be
  parseable and must not intersect the requirement stated in the document.
- **Removal form:** remove the dependency from the manifest while the document
  still names it. Use this form only when the document does not state a
  constraint.

The document line must still name the dependency.

## Output

Emit one JSON object:

```json
{
  "injectable": true,
  "drift_type": "external-dependency-drift",
  "direction": "code_side",
  "file": "<manifest file>",
  "old": "<the existing constraint, or the dependency name for removal>",
  "new": "<the new constraint, or null for removal>",
  "symbol": "<normalized dependency name>",
  "target": "<the exact dependency text as written on the document line>",
  "doc_path": "<document file, relative to the repository>",
  "doc_line_text": "<the exact current document line>",
  "target_claim": "<the statement the document makes that the change falsifies>",
  "exemplar_ids": ["..."],
  "rationale": "<one sentence: why this is a natural current-requirement statement>"
}
```

If no natural current-requirement statement exists, emit:

```json
{"injectable": false, "reason": "<short reason>"}
```

## Repository inventory

files:
  README.md, docs/structure.md, docs/walkthrough.md, examples/balance_frames.txt, examples/pump_response.txt, pyproject.toml, serialscope/__init__.py, serialscope/checksums.py, serialscope/cli.py, serialscope/codecs.py, serialscope/config.py, serialscope/errors.py, serialscope/frames.py, serialscope/transport.py, spec.json
symbols:
  serialscope.checksums.crc16_ccitt, serialscope.checksums.xor8, serialscope.cli.build_parser, serialscope.cli.main, serialscope.codecs.decode_measurement, serialscope.codecs.split_fields, serialscope.errors.ChecksumError, serialscope.errors.FramingError, serialscope.errors.SerialScopeError, serialscope.frames.Frame, serialscope.frames.FrameReader, serialscope.frames.parse_frame, serialscope.transport.SerialTransport, serialscope.transport.open_port
dependencies:
  pyserial>=3.5
string literals:
  0.3.1, Module serialscope/checksums.py., Module serialscope/cli.py., Module serialscope/codecs.py., Module serialscope/config.py., Module serialscope/errors.py., Module serialscope/frames.py., Module serialscope/transport.py., Package serialscope., Project class., Project function., SERIALSCOPE_BAUD, SERIALSCOPE_PORT, crc16_init, default_baud, stx

## Document excerpts

### README.md
   1: # serialscope
   2: 
   3: `serialscope` is about the serial-line responses that lab instruments send back —
   4: the kind you get from a balance that answers `S    12.345 g` or a syringe pump
   5: that answers `01:INFUSE;0.50ml/min`. It provides the framing, checksum, and
   6: decoding layers that stand between those bytes and a usable value.
   7: 
   8: The package is aimed at people writing small acquisition scripts or rig
   9: controllers: you already know which port your instrument is on, and you want the
  10: bytes turned into a number without re-implementing the same envelope parser for
  11: every device model.
  12: 
  13: Version 0.3.1. Python 3.11 or newer.
  14: 
  15: ## Install
  16: 
  17: ```bash
  18: pip install -e .
  19: ```
  20: 
  21: The only runtime dependency is `pyserial>=3.5`, which is installed for you.
  22: 
  23: ## What a response looks like
  24: 
  25: Instrument responses in this family are short ASCII payloads wrapped in a
  26: delimiter envelope. Both capture files in `examples/` follow the same shape:
  27: 
  28: ```
  29: 0x02  ... ASCII payload ...  0x03  <checksum> <checksum>
  30: ```
  31: 
  32: `examples/balance_frames.txt` holds two weighings:
  33: 
  34: ```
  35: 02 53 20 20 20 20 31 32 2e 33 34 35 20 67 03 1a 4f
  36: 02 53 20 20 20 20 20 30 2e 30 30 30 20 67 03 12 3d
  37: ```
  38: 
  39: which read as `S    12.345 g` and `S     0.000 g`, and
  40: `examples/pump_response.txt` holds one pump status line:
  41: 
  42: ```
  43: 02 30 31 3a 49 4e 46 55 53 45 3b 30 2e 35 30 6d 6c 2f 6d 69 6e 03 5c 2a
  44: ```
  45: 
  46: which reads as `01:INFUSE;0.50ml/min`.
  47: 
  48: ## Quick start
  49: 
  50: The pipeline, in code — a stored response in, a `Decimal` out:
  51: 
  52: ```python
  53: from serialscope.frames import parse_frame
  54: from serialscope.codecs import split_fields, decode_measurement
  55: 
  56: raw = bytes.fromhex("02 53 20 20 20 20 31 32 2e 33 34 35 20 67 03 1a 4f")
  57: 
  58: frame = parse_frame()            # -> Frame: address, payload, checksum
  59: fields = split_fields()          # -> list[str]
  60: value = decode_measurement()     # -> Decimal
  61: ```
  62: 
  63: Read live from an instrument instead:
  64: 
  65: ```python
  66: from serialscope.transport import open_port
  67: from serialscope.frames import FrameReader
  68: 
  69: transport = open_port()          # -> SerialTransport
  70: reader = FrameReader()
  71: ```
  72: 
  73: `open_port()` hands back a `SerialTransport` whose `port`, `baudrate`, and
  74: `timeout` attributes describe the connection; `FrameReader` accumulates incoming
  75: bytes in `buffer` and validates with the checksum scheme named by
  76: `checksum_mode`.
  77: 
  78: Note that in 0.3.1 these entry points are declared without parameters and return
  79: `None` — the snippet shows where each call sits in the pipeline, not a working
  80: conversion. The `->` comments are the declared return types.
  81: 
  82: ## Main concepts
  83: 
  84: **Frames.** A `Frame` is the unit everything else works on: the instrument
  85: `address`, the raw `payload` bytes, and the `checksum` that came with them.
  86: `frames.parse_frame` is the one-shot parser for a complete captured response, and
  87: `STX` names the start-of-frame marker the module is built around. `FrameReader`
  88: is the streaming counterpart — it keeps a `buffer` of whatever has arrived so far
  89: and a `checksum_mode` selecting how checksums are checked.
  90: 
  91: **Checksums.** `checksums.crc16_ccitt` and `checksums.xor8` are the two schemes
  92: the module offers for the trailing checksum bytes; `CRC16_INIT` is the initial
  93: value for the CRC routine.
  94: 
  95: **Decoding.** Raw payloads are two different things depending on the instrument:
  96: balances send fixed-width numeric text, pumps send `;`-separated status fields.
  97: `codecs.split_fields` breaks a payload into its fields, and
  98: `codecs.decode_measurement` converts a measurement field into a `Decimal` so you
  99: do not inherit binary floating-point rounding on a 0.001 g reading.
 100: 
 101: **Transport.** `transport.open_port` opens the serial line and returns a
 102: `SerialTransport`; `transport.SerialTransport` is the small holder for `port`,
 103: `baudrate`, and `timeout`.
 104: 
 105: **Configuration and the command line.** `config.ENV_DEFAULTS` lists the two
 106: environment variables the package recognises, `SERIALSCOPE_PORT` and
 107: `SERIALSCOPE_BAUD`, both defaulting to the empty string. `cli.build_parser`
 108: builds the argument parser and `cli.main` is the entry point, with
 109: `cli.DEFAULT_BAUD` as the fallback baud rate.
 110: 
 111: **Errors.** `errors` defines `SerialScopeError` together with the two specific
 112: failure modes it names: `FramingError` (the envelope did not line up) and
 113: `ChecksumError` (the trailing bytes did not match the payload).
 114: 
 115: ## Current state
 116: 
 117: The modules in this release define the public surface — names, attributes, and
 118: declared return types — but every function takes no arguments, its body is an
 119: empty placeholder, the error classes have no exception base, and
 120: `pyproject.toml` registers no `serialscope` console script. Treat the signatures
 121: and attributes described here as the contract, and see `docs/walkthrough.md` for
 122: what each step of the pipeline is
 123: for.
 124: 
 125: ## Where to go next
 126: 
 127: - `docs/walkthrough.md` — decode a captured balance response end to end.
 128: - `docs/structure.md` — what each module is responsible for and how the pieces
 129:   fit together.
### docs/structure.md
   1: # Module map
   2: 
   3: `serialscope` is a flat package: seven small modules under `serialscope/`, each
   4: owning one step of the job, plus a pair of capture files under `examples/` that
   5: serve as fixtures. There is no plugin layer; every public name is importable from
   6: the module that defines it.
   7: 
   8: ```
   9: serialscope/
  10:   README.md                  introduction and quick start
  11:   spec.json                  project description (name, version, modules)
  12:   pyproject.toml             packaging metadata, requires-python, pyserial
  13:   serialscope/
  14:     __init__.py              package docstring and __version__
  15:     errors.py                error types
  16:     checksums.py             crc16_ccitt, xor8, CRC16_INIT
  17:     frames.py                Frame, FrameReader, parse_frame, STX
  18:     codecs.py                split_fields, decode_measurement
  19:     transport.py             SerialTransport, open_port
  20:     config.py                ENV_DEFAULTS
  21:     cli.py                   build_parser, main, DEFAULT_BAUD
  22:   examples/
  23:     balance_frames.txt       two hex-encoded balance responses
  24:     pump_response.txt        one hex-encoded pump status response
  25:   docs/
  26:     walkthrough.md           tutorial
  27:     structure.md             this file
  28: ```
  29: 
  30: ## How the pieces relate
  31: 
  32: The modules follow the path a response takes from the wire to a value:
  33: 
  34: ```
  35: serial port ── transport.open_port ──> SerialTransport
  36:                                             │  raw bytes
  37:                                             ▼
  38:                        frames.FrameReader / frames.parse_frame
  39:                                  │            │
  40:                                  │            └── checksums.crc16_ccitt / xor8
  41:                                  ▼
  42:                               frames.Frame (address, payload, checksum)
  43:                                             │
  44:                                             ▼
  45:                         codecs.split_fields ──> codecs.decode_measurement
  46:                                             │
  47:                                             ▼
  48:                                          Decimal
  49: ```
  50: 
  51: `cli` and `config` sit alongside that path rather than inside it: `config`
  52: supplies the default port and baud rate, and `cli` is where a command-line caller
  53: would wire the other modules together.
  54: 
  55: In this release no module imports another one. Each file only has
  56: `from __future__ import annotations` at the top, so the modules can be read and
  57: tested one at a time; the arrows above are the intended data flow, not import
  58: statements.
  59: 
  60: ## `serialscope/__init__.py`
  61: 
  62: The package marker. It carries the package docstring and `__version__`, which is
  63: `"0.3.1"` — the same version as `pyproject.toml`. It does not re-export any
  64: names, so imports go to the defining module (`from serialscope.frames import
  65: parse_frame`, not `from serialscope import parse_frame`).
  66: 
  67: ## `serialscope/errors.py`
  68: 
  69: The three error types:
  70: 
  71: - `SerialScopeError` — the umbrella name for this package's failures.
  72: - `FramingError` — the response envelope did not line up: missing start marker,
  73:   missing end marker, or too few bytes for a checksum.
  74: - `ChecksumError` — the trailing bytes did not match the payload.
  75: 
  76: All three are declared as plain classes with an empty `__init__`. They do not
  77: inherit from `Exception` in this release, so they currently function as names and
  78: documentation of the failure modes; see `docs/walkthrough.md` step 5.
  79: 
  80: ## `serialscope/checksums.py`
  81: 
  82: The two checksum routines and their starting value:
  83: 
  84: - `crc16_ccitt()` — the CRC-16 path, declared to return `int`.
  85: - `xor8()` — the eight-bit XOR alternative, declared to return `int`.
  86: - `CRC16_INIT` — module-level constant holding the CRC's initial value.
  87: 
  88: Code that validates a response calls one of these and compares the result with
  89: `Frame.checksum`. Which one applies is a property of the instrument, which is
  90: what `FrameReader.checksum_mode` is for.
  91: 
  92: ## `serialscope/frames.py`
  93: 
  94: The core of the package. Everything downstream consumes a `Frame`.
  95: 
  96: - `Frame` — a parsed response. The constructor takes no arguments and sets three
  97:   attributes: `address`, `payload`, `checksum`.
  98: - `FrameReader` — the streaming reader. Keeps `buffer` (bytes received but not
  99:   yet formed into a frame) and `checksum_mode` (which scheme to verify with).
 100:   This is the class you keep alive across reads from a port.
 101: - `parse_frame()` — one-shot conversion of a complete response into a `Frame`,
 102:   declared to return `Frame`.
 103: - `STX` — module-level constant naming the start-of-frame marker.
 104: 
 105: The envelope the module is built around is `0x02`, payload, `0x03`, then two
 106: checksum bytes, as in `examples/balance_frames.txt`. `parse_frame` is for data you
 107: already have in hand (a capture file, a single read); `FrameReader` is for data
 108: that arrives in pieces.
 109: 
 110: ## `serialscope/codecs.py`
 111: 
 112: Payload interpretation, split from framing so that a new instrument format does
 113: not require touching the frame layer.
 114: 
 115: - `split_fields()` — breaks a payload into field strings, declared to return
 116:   `list[str]`.
 117: - `decode_measurement()` — converts a measurement field to a `Decimal`, declared
 118:   to return `Decimal`. Decimal, not float, is the point: a balance that reports
 119:   three decimals should not pick up binary rounding on the way in.
 120: 
 121: `examples/balance_frames.txt` decodes to space-separated fields
 122: (`S`, `12.345`, `g`), while `examples/pump_response.txt` decodes to a
 123: `;`-separated status line (`01:INFUSE;0.50ml/min`). Both end up in `split_fields`;
 124: what counts as a measurement is decided per format.
 125: 
 126: ## `serialscope/transport.py`
 127: 
 128: The serial line. This is the module that `pyserial` is a dependency for.
 129: 
 130: - `SerialTransport` — holder for the three connection settings: `port`,
 131:   `baudrate`, `timeout`. Constructed with no arguments; all three attributes
 132:   start as `None`.
 133: - `open_port()` — opens the connection and returns a `SerialTransport`.
 134: 
 135: Keeping this in its own module means the rest of the package works on bytes
 136: rather than on a live device, so a captured response can be replayed without any
 137: hardware attached.
 138: 
 139: ## `serialscope/config.py`
 140: 
 141: `ENV_DEFAULTS` is a dictionary of the two environment variables the package
 142: recognises:
 143: 
 144: | key | default |
 145: | --- | --- |
 146: | `SERIALSCOPE_PORT` | `""` |
 147: | `SERIALSCOPE_BAUD` | `""` |
 148: 
 149: Because both default to the empty string, a value you export always wins over an
 150: unset one. `config` holds the names and defaults only; it does not read the
 151: environment or open anything itself.
 152: 
 153: ## `serialscope/cli.py`
 154: 
 155: The command-line layer:
 156: 
 157: - `build_parser()` — builds and returns an `argparse.ArgumentParser`.
 158: - `main()` — the entry point, declared to return `int`.
 159: - `DEFAULT_BAUD` — module-level constant for the fallback baud rate.
 160: 
 161: `pyproject.toml` declares `packages = ["serialscope"]` and no `[project.scripts]`
 162: entry, so installing the package does not put a `serialscope` command on your
 163: `PATH`; `main` is reachable as a normal function call. Wiring subcommands, the
 164: port from `SERIALSCOPE_PORT`, and the baud from `SERIALSCOPE_BAUD` is what this
 165: module exists for.
 166: 
 167: ## `examples/`
 168: 
 169: Two hex-encoded captures, one response per line:
 170: 
 171: - `balance_frames.txt` — `S    12.345 g` and `S     0.000 g`.
 172: - `pump_response.txt` — `01:INFUSE;0.50ml/min`.
 173: 
 174: They are plain text, not packaged data files: `pyproject.toml` ships only the
 175: `serialscope` package, so read them relative to a checkout. They are the fixture
 176: set the walkthrough builds on.
 177: 
 178: ## Current state of the tree
 179: 
 180: Every function in the package is declared without parameters and has a body that
 181: returns `None`; every class constructor takes no arguments and sets its
 182: attributes to `None`; the three error classes have no base class. The module map
 183: above describes what each piece is responsible for, and the signatures and
 184: attributes are the contract the rest of the package is written against. There are
 185: no tests in this tree and no console-script entry point.
### docs/walkthrough.md
   1: # Walkthrough: decoding a balance capture
   2: 
   3: This tutorial walks through the steps that turn a captured balance response into
   4: a `Decimal` weighing, then points the same steps at a live port. It uses the two
   5: files under `examples/`, so you can follow it without any hardware attached.
   6: 
   7: ## 1. Install the package
   8: 
   9: From the repository root:
  10: 
  11: ```bash
  12: pip install -e .
  13: python -c "import serialscope; print(serialscope.__version__)"
  14: ```
  15: 
  16: You should see `0.3.1`. If the import fails, check that you are on Python 3.11
  17: or newer — that is what `pyproject.toml` requires.
  18: 
  19: ## 2. Look at the capture
  20: 
  21: `examples/balance_frames.txt` contains two responses, one per line, written as
  22: space-separated hex:
  23: 
  24: ```
  25: 02 53 20 20 20 20 31 32 2e 33 34 35 20 67 03 1a 4f
  26: 02 53 20 20 20 20 20 30 2e 30 30 30 20 67 03 12 3d
  27: ```
  28: 
  29: Every response has the same envelope:
  30: 
  31: | position | content |
  32: | --- | --- |
  33: | first byte | `0x02`, the start-of-frame marker |
  34: | middle | ASCII payload |
  35: | then | `0x03`, the end-of-frame marker |
  36: | last two bytes | checksum |
  37: 
  38: Because the file is hex text, the first job in your own script is to get real
  39: bytes:
  40: 
  41: ```python
  42: from pathlib import Path
  43: 
  44: lines = Path("examples/balance_frames.txt").read_text().splitlines()
  45: frames = [bytes.fromhex(line) for line in lines if line.strip()]
  46: 
  47: print(len(frames), frames[0][:1], frames[0][-3:-2])
  48: ```
  49: 
  50: That prints `2 b'\x02' b'\x03'`: two frames, each starting at `0x02` and ending
  51: its payload at `0x03`.
  52: 
  53: ## 3. Scale up to the payload
  54: 
  55: With the envelope confirmed, the payload is everything between the markers:
  56: 
  57: ```python
  58: for raw in frames:
  59:     payload = raw[1:-3]
  60:     print(payload.decode("ascii"))
  61: ```
  62: 
  63: ```
  64: S    12.345 g
  65: S     0.000 g
  66: ```
  67: 
  68: The two readings differ only in the numeric field: 12.345 g and 0.000 g. Note
  69: that the field widths are padded with spaces, which is why you do not want to
  70: slice by offset in your own code — split on whitespace instead.
  71: 
  72: ## 4. Where `serialscope` takes over
  73: 
  74: The manual steps above map onto the package like this:
  75: 
  76: ```python
  77: from serialscope.frames import parse_frame
  78: from serialscope.codecs import split_fields, decode_measurement
  79: 
  80: frame = parse_frame()            # -> Frame, holds address, payload, checksum
  81: fields = split_fields()          # -> list[str], one entry per payload field
  82: reading = decode_measurement()   # -> Decimal, e.g. 12.345
  83: ```
  84: 
  85: - `parse_frame` is the one-shot step for a complete response: the resulting
  86:   `Frame` carries the `address`, the `payload` bytes, and the trailing `checksum`
  … (truncated)
### examples/balance_frames.txt
  … (truncated)
### examples/pump_response.txt
  … (truncated)

## Examples (few-shot)

Real incidents of this kind, rendered as bare `before → after` excerpts under a
`<file> (doc|code)` header. Use them to understand what kind of artifact tends to
drift; do not copy their wording or content.

### example 1
docs/development.md (doc)
  - 
  + - (Optional) VULKAN GPU support
  +     - [VULKAN SDK](https://vulkan.lunarg.com/sdk/home) - useful for AMD/Intel GPUs
  + > Building for Vulkan requires VULKAN_SDK environment variable:
  + > 
  + > PowerShell
  + > ```powershell
  + > $env:VULKAN_SDK="C:\VulkanSDK\<version>"
  + > ```

### example 2
docs/integrations/nemoclaw.mdx (doc)
  + ---
  + title: NemoClaw
  + ---
  + 
  + NemoClaw is NVIDIA's open source security stack for [OpenClaw](/integrations/openclaw). It wraps OpenClaw with the NVIDIA OpenShell runtime to provide kernel-level sandboxing, network policy controls, and audit trails for AI agents. 
  + 
  + ## Quick start
  + 

### example 3
autogpt_platform/backend/backend/copilot/tools/agent_browser.py (code)
  + """Agent-browser tools — multi-step browser automation for the Copilot.
  + 
  + Uses the agent-browser CLI (https://github.com/vercel-labs/agent-browser)
  + which runs a local Chromium instance managed by a persistent daemon.
  + 
  + - Runs locally — no cloud account required
  + - Full interaction support: click, fill, scroll, login flows, multi-step
  + - Session persistence via --session-name: cookies/auth carry across tool calls

### example 4
Documentation/process/changes.rst (doc)
  - bindgen (optional)     0.65.1           bindgen --version
  + bindgen (optional)     0.71.1           bindgen --version
scripts/min-tool-version.sh (code)
  - 	echo 0.65.1
  + 	echo 0.71.1

