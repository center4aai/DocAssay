# Injection task

corpus repository: `sheetmusic`

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
  README.md, docs/api.md, docs/guide.md, pyproject.toml, sheetmusic/__init__.py, sheetmusic/cli.py, sheetmusic/models.py, sheetmusic/notes.py, sheetmusic/parser.py, sheetmusic/transpose.py, spec.json
symbols:
  sheetmusic.cli.main, sheetmusic.models.Chord, sheetmusic.models.Progression, sheetmusic.notes.note_to_semitone, sheetmusic.notes.semitone_to_note, sheetmusic.parser.parse_chord, sheetmusic.parser.parse_progression, sheetmusic.transpose.transpose_chord, sheetmusic.transpose.transpose_progression
dependencies:
  click>=8.1
string literals:
  0.3.0, Module sheetmusic/cli.py., Module sheetmusic/models.py., Module sheetmusic/notes.py., Module sheetmusic/parser.py., Module sheetmusic/transpose.py., Package sheetmusic., Project class., Project function., note_names

## Document excerpts

### README.md
   1: # sheetmusic
   2: 
   3: `sheetmusic` is a small Python library for working with chord symbols and chord
   4: progressions. It is meant for code that needs to represent a chord as a root,
   5: a quality, and an optional bass note, group chords into a titled progression,
   6: and transpose those chords between keys.
   7: 
   8: Version: 0.3.0. Requires Python 3.11 or newer.
   9: 
  10: ## Status
  11: 
  12: The package is an early release. The module layout and public names are in
  13: place, but the functions are currently stubs: each one is declared with its
  14: return type and its body returns `None`. The `Chord` and `Progression` classes
  15: can be constructed and their attributes read and set. See the
  16: [API reference](docs/api.md) for the details of each name.
  17: 
  18: ## Installation
  19: 
  20: From a checkout of the repository:
  21: 
  22: ```bash
  23: pip install .
  24: ```
  25: 
  26: For an editable install while developing:
  27: 
  28: ```bash
  29: pip install -e .
  30: ```
  31: 
  32: The only declared runtime dependency is `click>=8.1`.
  33: 
  34: ## Quick start
  35: 
  36: Import the public names from the submodules:
  37: 
  38: ```python
  39: from sheetmusic.models import Chord, Progression
  40: from sheetmusic.parser import parse_chord, parse_progression
  41: from sheetmusic.transpose import transpose_chord, transpose_progression
  42: from sheetmusic.notes import note_to_semitone, semitone_to_note
  43: 
  44: chord = Chord()
  45: chord.root = "C"
  46: chord.quality = "m"
  47: chord.bass = "G"
  48: 
  49: progression = Progression()
  50: progression.title = "Example"
  51: progression.chords = [chord]
  52: ```
  53: 
  54: The functions `parse_chord`, `parse_progression`, `transpose_chord`,
  55: `transpose_progression`, `note_to_semitone`, and `semitone_to_note` can be
  56: imported, but in the current release they return `None`.
  57: 
  58: ## Documentation
  59: 
  60: - [User guide](docs/guide.md) covers chords, progressions, and the module
  61:   layout.
  62: - [API reference](docs/api.md) lists every public class, function, and
  63:   constant.
### docs/api.md
   1: # API reference
   2: 
   3: All public names are importable from their submodules under the `sheetmusic`
   4: package. Every function in the current release has a body that returns `None`;
   5: the return types below are the declared types.
   6: 
   7: ## `sheetmusic.models`
   8: 
   9: ### `class Chord`
  10: 
  11: ```python
  12: class Chord:
  13:     def __init__(self) -> None: ...
  14: ```
  15: 
  16: A chord. Construction takes no arguments.
  17: 
  18: | Attribute | Initial value | Description |
  19: | --- | --- | --- |
  20: | `root` | `None` | Root note of the chord. |
  21: | `quality` | `None` | Chord quality. |
  22: | `bass` | `None` | Bass note. |
  23: 
  24: ### `class Progression`
  25: 
  26: ```python
  27: class Progression:
  28:     def __init__(self) -> None: ...
  29: ```
  30: 
  31: A sequence of chords. Construction takes no arguments.
  32: 
  33: | Attribute | Initial value | Description |
  34: | --- | --- | --- |
  35: | `chords` | `None` | The chords in the progression. |
  36: | `title` | `None` | Display name for the progression. |
  37: 
  38: ## `sheetmusic.notes`
  39: 
  40: ### `NOTE_NAMES`
  41: 
  42: Module-level constant. In the current source its value is the string
  43: `"note_names"`.
  44: 
  45: ### `note_to_semitone() -> int`
  46: 
  47: Declared to convert a note name to a semitone number. Takes no parameters in
  48: the current source. The body returns `None`.
  49: 
  50: ### `semitone_to_note() -> str`
  51: 
  52: Declared to convert a semitone number to a note name. Takes no parameters in
  53: the current source. The body returns `None`.
  54: 
  55: ## `sheetmusic.parser`
  56: 
  57: ### `parse_chord() -> Chord`
  58: 
  59: Declared to parse a chord symbol into a `Chord`. Takes no parameters in the
  60: current source. The body returns `None`.
  61: 
  62: ### `parse_progression() -> Progression`
  63: 
  64: Declared to parse a progression into a `Progression`. Takes no parameters in
  65: the current source. The body returns `None`.
  66: 
  67: ## `sheetmusic.transpose`
  68: 
  69: ### `transpose_chord() -> Chord`
  70: 
  71: Declared to transpose a `Chord` to another key. Takes no parameters in the
  72: current source. The body returns `None`.
  73: 
  74: ### `transpose_progression() -> Progression`
  75: 
  76: Declared to transpose a `Progression` to another key. Takes no parameters in
  77: the current source. The body returns `None`.
  78: 
  79: ## `sheetmusic.cli`
  80: 
  81: ### `main() -> int`
  82: 
  83: Entry function for the command-line interface. Takes no parameters in the
  84: current source. The body returns `None`. The package does not register a
  85: console script for it in `pyproject.toml`.
  86: 
  87: ## `sheetmusic.__version__`
  88: 
  89: The string `"0.3.0"`, defined in `sheetmusic/__init__.py`.
### docs/guide.md
   1: # User guide
   2: 
   3: This guide describes the concepts behind `sheetmusic` and how the modules are
   4: laid out. For the exact signatures, see the [API reference](api.md).
   5: 
   6: ## Package layout
   7: 
   8: | Module | Purpose |
   9: | --- | --- |
  10: | `sheetmusic.models` | The `Chord` and `Progression` classes. |
  11: | `sheetmusic.notes` | Note-name constant and note/semitone conversion functions. |
  12: | `sheetmusic.parser` | Functions that parse chord symbols and progressions. |
  13: | `sheetmusic.transpose` | Functions that transpose chords and progressions. |
  14: | `sheetmusic.cli` | The `main` entry function for a command-line interface. |
  15: 
  16: The package also exposes `__version__` in `sheetmusic/__init__.py`, set to
  17: `0.3.0`.
  18: 
  19: ## Chords
  20: 
  21: A `Chord` has three attributes:
  22: 
  23: - `root`: the root note of the chord.
  24: - `quality`: the chord quality (for example, a minor or seventh quality).
  25: - `bass`: the bass note, when it differs from the root.
  26: 
  27: `Chord()` takes no arguments. All three attributes are initialized to `None`,
  28: and you assign them directly:
  29: 
  30: ```python
  31: from sheetmusic.models import Chord
  32: 
  33: c = Chord()
  34: c.root = "A"
  35: c.quality = "m7"
  36: c.bass = "C"
  37: ```
  38: 
  39: The library does not currently define a fixed set of allowed values for
  40: `root`, `quality`, or `bass`. The attributes store whatever you assign.
  41: 
  42: ## Progressions
  43: 
  44: A `Progression` groups chords under an optional title:
  45: 
  46: - `chords`: the sequence of chords in the progression.
  47: - `title`: a display name for the progression.
  48: 
  49: Like `Chord`, `Progression()` takes no arguments and sets both attributes to
  50: `None`:
  51: 
  52: ```python
  53: from sheetmusic.models import Chord, Progression
  54: 
  55: p = Progression()
  56: p.title = "Two-chord vamp"
  57: p.chords = [Chord(), Chord()]
  58: ```
  59: 
  60: ## Parsing
  61: 
  62: The `sheetmusic.parser` module declares `parse_chord` (returns `Chord`) and
  63: `parse_progression` (returns `Progression`). In the current release their
  64: bodies return `None`, so they do not yet turn a chord symbol string into a
  65: `Chord` object.
  66: 
  67: ## Transposing
  68: 
  69: The `sheetmusic.transpose` module declares `transpose_chord` (returns `Chord`)
  70: and `transpose_progression` (returns `Progression`). These are also stubs in
  71: the current release.
  72: 
  73: ## Note arithmetic
  74: 
  75: The `sheetmusic.notes` module declares `note_to_semitone` (returns `int`) and
  76: `semitone_to_note` (returns `str`), which are intended to convert between note
  77: names and semitone numbers. Both currently return `None`. The module-level
  78: constant `NOTE_NAMES` is defined, but its value in the current source is the
  79: placeholder string `"note_names"`.
  80: 
  81: ## Command-line interface
  82: 
  83: `sheetmusic/cli.py` defines `main()`, declared to return `int`. Its body
  84: currently returns `None`. The `pyproject.toml` file does not declare a console
  85: script, so no `sheetmusic` command is installed by the package at this
  86: version.

## Examples (few-shot)

Real incidents of this kind, rendered as bare `before → after` excerpts under a
`<file> (doc|code)` header. Use them to understand what kind of artifact tends to
drift; do not copy their wording or content.

### example 1
arch/Kconfig (code)
  - 	depends on RUSTC_VERSION >= 107900
  - 	depends on (RUSTC_LLVM_VERSION >= 190103 && RUSTC_VERSION >= 108200) || \
  + 	depends on RUSTC_LLVM_VERSION >= 190103 || \
arch/arm64/Kconfig (code)
  - 	# Shadow call stack is only supported on certain rustc versions.
  - 	#
  - 	# When using the UNWIND_PATCH_PAC_INTO_SCS option, rustc version 1.80+ is
  - 	# required due to use of the -Zfixed-x18 flag.
  - 	#
  - 	# Otherwise, rustc version 1.82+ is required due to use of the
  - 	# -Zsanitizer=shadow-call-stack flag.
  - 	depends on !SHADOW_CALL_STACK || RUSTC_VERSION >= 108200 || RUSTC_VERSION >= 108000 && UNWIND_PATCH_PAC_INTO_SCS

### example 2
docs/integrations/pi.mdx (doc)
  + ---
  + title: Pi
  + ---
  + 
  + Pi is a minimal AI agent toolkit with plugin support.
  + 
  + ## Install
  + 

### example 3
.github/workflows/platform-frontend-ci.yml (code)
  -           node-version: "21"
  -           node-version: "21"
  -           node-version: "21"
  -           node-version: "21"
  +           node-version: "22.18.0"
  +           node-version: "22.18.0"
  +           node-version: "22.18.0"
  +           node-version: "22.18.0"
.github/workflows/platform-fullstack-ci.yml (code)
  -           node-version: "21"
  -           node-version: "21"
  +           node-version: "22.18.0"
  +           node-version: "22.18.0"

### example 4
autogpt_platform/backend/backend/copilot/tools/agent_browser.py (code)
  + """Agent-browser tools — multi-step browser automation for the Copilot.
  + 
  + Uses the agent-browser CLI (https://github.com/vercel-labs/agent-browser)
  + which runs a local Chromium instance managed by a persistent daemon.
  + 
  + - Runs locally — no cloud account required
  + - Full interaction support: click, fill, scroll, login flows, multi-step
  + - Session persistence via --session-name: cookies/auth carry across tool calls

