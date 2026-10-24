# Injection task

corpus repository: `bibscan`

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

# Injector — removed-referent drift

**Defect.** A document names a class or function as current API, but that
definition is deleted from the code. The document is left unchanged, so it names
something that no longer exists.

- **Artifact:** a class or function defined in the repository.
- **Direction:** change the code; leave the document unchanged.

## What to look for

Choose a statement that presents a class or function as current, available API.
Do not choose a name that is already described as deprecated, historical, or
illustrative.

The mutation removes a **definition** (a top-level class or function), not a
method or an attribute. Prefer a definition that is not imported or called
elsewhere, so the rest of the tree still parses after the removal.

## The change

Delete the definition as a whole block. The old name must be absent after the
change and the file must still parse. The document line must still name the
**deleted** symbol.

## Output

Emit one JSON object:

```json
{
  "injectable": true,
  "drift_type": "removed-referent-drift",
  "direction": "code_side",
  "file": "<source file that defines the symbol>",
  "old": "<the name as the document writes it>",
  "new": null,
  "symbol": "<bare symbol name>",
  "target": "<the exact name text as written on the document line>",
  "doc_path": "<document file, relative to the repository>",
  "doc_line_text": "<the exact current document line>",
  "target_claim": "<the statement the document makes that the removal falsifies>",
  "exemplar_ids": ["..."],
  "rationale": "<one sentence: why this is a natural current-API statement>"
}
```

If no natural current-API statement exists, emit:

```json
{"injectable": false, "reason": "<short reason>"}
```

## Repository inventory

files:
  README.md, bibscan/__init__.py, bibscan/cli.py, bibscan/format.py, bibscan/model.py, bibscan/names.py, bibscan/parser.py, docs/api.md, docs/recipes.md, examples/library.bib, pyproject.toml, spec.json
symbols:
  bibscan.cli.main, bibscan.cli.scan_file, bibscan.format.format_bibliography, bibscan.format.format_citation, bibscan.model.Entry, bibscan.model.Name, bibscan.model.Style, bibscan.names.format_name, bibscan.names.parse_names, bibscan.parser.BibSyntaxError, bibscan.parser.parse_bibtex, bibscan.parser.parse_csl
dependencies:
  lxml>=4.9, python-dateutil>=2.8
string literals:
  0.4.2, Module bibscan/cli.py., Module bibscan/format.py., Module bibscan/model.py., Module bibscan/names.py., Module bibscan/parser.py., Package bibscan., Project class., Project function., default_locale, particles

## Document excerpts

### README.md
   1: # bibscan
   2: 
   3: `bibscan` is a small Python library for working with bibliographic data: it
   4: parses BibTeX databases and CSL (Citation Style Language) styles, and renders
   5: citations and bibliographies from the records it reads.
   6: 
   7: The package is at version `0.4.2` and requires Python 3.11 or newer.
   8: 
   9: ## Status of this tree
  10: 
  11: The modules, classes, and function signatures are in place, but the parsing and
  12: formatting functions are not implemented yet. In `0.4.2` every function accepts
  13: no arguments and returns `None`, and every record class is created with no
  14: arguments and starts with all of its attributes set to `None`. This README and
  15: the rest of the documentation describe the surface that is defined today, so
  16: that the shape of the library is clear before the bodies land.
  17: 
  18: ## Installation
  19: 
  20: From a checkout of this repository:
  21: 
  22: ```bash
  23: pip install .
  24: ```
  25: 
  26: The only runtime dependencies are `lxml>=4.9` and `python-dateutil>=2.8`, both
  27: declared in `pyproject.toml` and installed for you.
  28: 
  29: For development, install into a virtual environment and run Python from there:
  30: 
  31: ```bash
  32: python -m venv .venv
  33: source .venv/bin/activate
  34: pip install .
  35: ```
  36: 
  37: ## Quick start
  38: 
  39: Import the pieces you need from the modules that define them; the package
  40: `bibscan` itself only exports `__version__`.
  41: 
  42: ```python
  43: import bibscan
  44: from bibscan.model import Entry, Name, Style
  45: from bibscan.parser import parse_bibtex, parse_csl
  46: from bibscan.format import format_citation, format_bibliography
  47: 
  48: print(bibscan.__version__)        # 0.4.2
  49: 
  50: entry = Entry()
  51: entry.key = "knuth1984"
  52: entry.entry_type = "article"
  53: entry.fields = {"title": "Literate Programming", "year": "1984"}
  54: 
  55: name = Name()
  56: name.family = "Knuth"
  57: name.given = "Donald E."
  58: 
  59: style = Style()
  60: style.style_id = "apa"
  61: ```
  62: 
  63: The bundled database `examples/library.bib` holds two entries — `knuth1984`
  64: (an `@article`) and `lamport1994` (a `@book`) — and is a convenient file to
  65: point the parser at once it is implemented.
  66: 
  67: ## Concepts
  68: 
  69: **Records.** BibTeX entries are represented by `Entry`, with a citation `key`,
  70: an `entry_type` such as `article` or `book`, and a `fields` mapping of the
  71: remaining BibTeX fields. Personal names are represented by `Name`, split into
  72: `family`, `given`, and `suffix`. CSL styles are represented by `Style`, with a
  73: `style_id`, a human-readable `title`, and a `macros` collection.
  74: 
  75: **Parsing.** `bibscan.parser.parse_bibtex` is the entry point for BibTeX input
  76: and `bibscan.parser.parse_csl` for CSL styles. The module also defines
  77: `BibSyntaxError` for malformed input, carrying the `line` and `column` of the
  78: problem. As written, `BibSyntaxError` is a plain class rather than a subclass of
  79: `Exception`, so keep that in mind when writing `except` clauses.
  80: 
  81: **Names.** `bibscan.names` handles the awkward parts of personal names:
  82: `parse_names` splits a name list into `Name` records and `format_name` turns a
  83: record back into text. The module also defines a `PARTICLES` constant for the
  84: name-particle vocabulary.
  85: 
  86: **Formatting.** `bibscan.format` renders output. `format_citation` produces a
  87: single citation and `format_bibliography` produces a bibliography, and the
  88: module carries the default locale in `DEFAULT_LOCALE`. Styles parsed by
  89: `parse_csl` are what the renderers are meant to work from.
  90: 
  91: **Command line.** `bibscan.cli` contains `scan_file`, typed as returning a list
  92: of `Entry` objects for a database, and `main`, typed as returning an `int`
  93: process exit code. `pyproject.toml` does not declare a console-script entry
  94: point, so installing the package does not put a `bibscan` command on your
  95: `PATH`; call `bibscan.cli.main()` from Python instead.
  96: 
  97: ## Documentation
  98: 
  99: - [`docs/recipes.md`](docs/recipes.md) — short, task-oriented examples.
 100: - [`docs/api.md`](docs/api.md) — the complete public interface.
### docs/api.md
   1: # bibscan API reference
   2: 
   3: Version `0.4.2`. Python 3.11 or newer.
   4: 
   5: ```python
   6: import bibscan
   7: bibscan.__version__   # "0.4.2"
   8: ```
   9: 
  10: The package's `__init__.py` defines only `__version__`. Import everything else
  11: from the module that defines it.
  12: 
  13: Module summary:
  14: 
  15: | Module | Contents |
  16: | --- | --- |
  17: | `bibscan.model` | `Entry`, `Name`, `Style` |
  18: | `bibscan.parser` | `BibSyntaxError`, `parse_bibtex`, `parse_csl` |
  19: | `bibscan.names` | `PARTICLES`, `parse_names`, `format_name` |
  20: | `bibscan.format` | `DEFAULT_LOCALE`, `format_citation`, `format_bibliography` |
  21: | `bibscan.cli` | `scan_file`, `main` |
  22: 
  23: ## bibscan.model
  24: 
  25: ### `class Entry`
  26: 
  27: A single BibTeX record. Constructed with no arguments; all attributes are
  28: initialised to `None`.
  29: 
  30: | Attribute | Meaning |
  31: | --- | --- |
  32: | `key` | The citation key, e.g. `"knuth1984"` |
  33: | `entry_type` | The BibTeX entry type, e.g. `"article"` or `"book"` |
  34: | `fields` | The remaining BibTeX fields for the entry |
  35: 
  36: ```python
  37: from bibscan.model import Entry
  38: 
  39: entry = Entry()
  40: entry.key = "lamport1994"
  41: entry.entry_type = "book"
  42: entry.fields = {"title": "LaTeX: A Document Preparation System", "year": "1994"}
  43: ```
  44: 
  45: ### `class Name`
  46: 
  47: One personal name, split into parts so that different name orders can be
  48: rendered from the same record. Constructed with no arguments; all attributes are
  49: initialised to `None`.
  50: 
  51: | Attribute | Meaning |
  52: | --- | --- |
  53: | `family` | Family name, including any particle |
  54: | `given` | Given names |
  55: | `suffix` | Name suffix such as `"Jr."` |
  56: 
  57: ### `class Style`
  58: 
  59: A CSL style. Constructed with no arguments; all attributes are initialised to
  60: `None`.
  61: 
  62: | Attribute | Meaning |
  63: | --- | --- |
  64: | `style_id` | Identifier of the style, e.g. `"apa"` |
  65: | `title` | Human-readable style title |
  66: | `macros` | The macros defined by the style |
  67: 
  68: ## bibscan.parser
  69: 
  70: ### `class BibSyntaxError`
  71: 
  72: Reports a malformed input. Constructed with no arguments; attributes are
  73: initialised to `None`.
  74: 
  75: | Attribute | Meaning |
  76: | --- | --- |
  77: | `line` | Line number where the problem was found |
  78: | `column` | Column number where the problem was found |
  79: 
  80: `BibSyntaxError` is declared as a plain class with no base class other than the
  81: implicit `object`; it is **not** a subclass of `Exception`.
  82: 
  83: ### `parse_bibtex() -> list[Entry]`
  84: 
  85: Parses a BibTeX database and returns its entries as `Entry` objects.
  86: 
  87: The function is declared with an empty parameter list and currently returns
  88: `None`.
  89: 
  90: ### `parse_csl() -> Style`
  91: 
  92: Parses a CSL style and returns it as a `Style`.
  93: 
  94: The function is declared with an empty parameter list and currently returns
  95: `None`.
  96: 
  97: ## bibscan.names
  98: 
  99: ### `PARTICLES`
 100: 
 101: Module-level constant:
 102: 
 103: ```python
 104: PARTICLES = "particles"
 105: ```
 106: 
 107: It is the token for the particle vocabulary used when splitting names such as
 108: "van Beethoven" or "de la Cruz".
 109: 
 110: ### `parse_names() -> list[Name]`
 111: 
 112: Splits a name list into `Name` records.
 113: 
 114: The function is declared with an empty parameter list and currently returns
 115: `None`.
 116: 
 117: ### `format_name() -> str`
 118: 
 119: Formats a `Name` record as display text.
 120: 
 121: The function is declared with an empty parameter list and currently returns
 122: `None`.
 123: 
 124: ## bibscan.format
 125: 
 126: ### `DEFAULT_LOCALE`
 127: 
 128: Module-level constant holding the default locale for rendered output:
 129: 
 130: ```python
 131: DEFAULT_LOCALE = "default_locale"
 132: ```
 133: 
 134: ### `format_citation() -> str`
 135: 
 136: Renders a single citation.
 137: 
 138: The function is declared with an empty parameter list and currently returns
 139: `None`.
 140: 
 141: ### `format_bibliography() -> str`
 142: 
 143: Renders a bibliography.
 144: 
 145: The function is declared with an empty parameter list and currently returns
 146: `None`.
 147: 
 148: ## bibscan.cli
 149: 
 150: ### `scan_file() -> list[Entry]`
 151: 
 152: Reads a BibTeX database and returns its entries, in the same form as
 153: `parse_bibtex`.
 154: 
 155: The function is declared with an empty parameter list and currently returns
 156: `None`.
 157: 
 158: ### `main() -> int`
 159: 
 160: Command-line entry function; the return value is the process exit code.
 161: 
 162: The function is declared with an empty parameter list and currently returns
 163: `None`.
 164: 
 165: `pyproject.toml` declares no console-script entry point, so there is no
 166: installed `bibscan` command. Call it from Python:
 167: 
 168: ```python
 169: from bibscan.cli import main
 170: 
 171: raise SystemExit(main())
 172: ```
 173: 
 174: ## Notes on the current implementation
 175: 
 176: - Function bodies are placeholders: they take no arguments and return `None`.
 177:   Calls are safe, but they do not read files, parse anything, or produce output.
 178: - The record classes have no constructor parameters. Create an instance with no
 179:   arguments and assign the attributes you need.
 180: - Type annotations on the parser functions (`list[Entry]`, `Style`) are written
 181:   as strings by `from __future__ import annotations`, and `Entry` and `Style`
 182:   are not imported in `bibscan/parser.py`. The annotations describe intent; they
 183:   are not resolvable at runtime here.
### docs/recipes.md
   1: # Recipes
   2: 
   3: Short, self-contained examples for the tasks you are most likely to want.
   4: They use the public interface described in [`api.md`](api.md).
   5: 
   6: A note that applies to every recipe below: in `0.4.2` the functions in
   7: `bibscan` take no arguments yet and return `None`, and the record classes start
   8: out empty. The recipes therefore show how to set up and inspect records
   9: directly, and show the call sites that will produce the data once the
  10: implementations are in place.
  11: 
  12: ## Install and confirm the version
  13: 
  14: ```bash
  15: pip install .
  16: python -c "import bibscan; print(bibscan.__version__)"
  17: ```
  18: 
  19: That prints `0.4.2`. The package requires Python 3.11 or newer.
  20: 
  21: ## Find the symbol you need
  22: 
  23: Each part of the library lives in its own module; nothing beyond
  24: `__version__` is re-exported at package level.
  25: 
  26: ```python
  27: from bibscan.model import Entry, Name, Style
  28: from bibscan.parser import BibSyntaxError, parse_bibtex, parse_csl
  29: from bibscan.names import PARTICLES, parse_names, format_name
  30: from bibscan.format import DEFAULT_LOCALE, format_citation, format_bibliography
  31: from bibscan.cli import scan_file, main
  32: ```
  33: 
  34: ## Build an entry record by hand
  35: 
  36: `Entry` is a plain record with three attributes, all `None` on a fresh
  37: instance.
  38: 
  39: ```python
  40: from bibscan.model import Entry
  41: 
  42: entry = Entry()
  43: entry.key = "knuth1984"
  44: entry.entry_type = "article"
  45: entry.fields = {
  46:     "author": "Knuth, Donald E.",
  47:     "title": "Literate Programming",
  48:     "journal": "The Computer Journal",
  49:     "year": "1984",
  50:     "volume": "27",
  51:     "number": "2",
  52:     "pages": "97--111",
  53: }
  54: 
  55: print(entry.key, entry.entry_type)   # knuth1984 article
  56: ```
  57: 
  58: This is the same entry that appears first in `examples/library.bib`.
  59: 
  60: ## Load the bundled example database
  61: 
  62: The repository ships one database, `examples/library.bib`, with two entries:
  63: `knuth1984` (`@article`) and `lamport1994` (`@book`). Reading it as text needs
  64: nothing from the library:
  65: 
  66: ```python
  67: from pathlib import Path
  68: 
  69: path = Path("examples/library.bib")
  70: text = path.read_text(encoding="utf-8")
  71: print(text.count("@"))   # 2
  72: ```
  73: 
  74: Once `parse_bibtex` is implemented, pass the file contents to it and iterate
  75: over the returned `Entry` objects:
  76: 
  77: ```python
  78: from bibscan.parser import parse_bibtex
  79: 
  80: entries = parse_bibtex()
  81: for entry in entries or []:
  82:     print(entry.key, entry.entry_type)
  83: ```
  84: 
  85: The `or []` guard is there because the function currently returns `None`.
  86: 
  87: ## Read a CSL style
  88: 
  89: A style is a `Style` record: an identifier, a title, and the macros the style
  90: defines.
  91: 
  92: ```python
  93: from bibscan.model import Style
  94: 
  95: style = Style()
  96: style.style_id = "apa"
  97: style.title = "American Psychological Association 7th edition"
  98: style.macros = {"author": "...", "issued": "..."}
  99: 
 100: print(style.style_id)
 101: ```
 102: 
 103: `parse_csl` is the function that will build this record from CSL input:
 104: 
 105: ```python
 106: from bibscan.parser import parse_csl
 107: 
 108: style = parse_csl()
 109: ```
 110: 
 111: ## Split and reformat a name
 112: 
 113: Name handling lives in `bibscan.names`. `Name` keeps the parts separate so that
 114: "family name first" and "given name first" styles can be produced from the same
 115: record.
 116: 
 117: ```python
  … (truncated)

## Examples (few-shot)

Real incidents of this kind, rendered as bare `before → after` excerpts under a
`<file> (doc|code)` header. Use them to understand what kind of artifact tends to
drift; do not copy their wording or content.

### example 1
classic/forge/forge/llm/providers/groq.py (code)
  -     LLAMA3_8B = "llama3-8b-8192"
  -     LLAMA3_70B = "llama3-70b-8192"
  -         ChatModelInfo(
  -             name=GroqModelName.LLAMA3_8B,
  -             provider_name=ModelProviderName.GROQ,
  -             prompt_token_cost=0.05 / 1e6,
  -             completion_token_cost=0.10 / 1e6,
  -             max_tokens=8192,

### example 2
cmd/tui/tui.go (code)
  - 	"github.com/ollama/ollama/internal/modelref"
  - 	if name == "" {
  - 		return false
  - 	}
  - 	if modelref.HasExplicitCloudSource(name) {
  - 		return true
  - 	}
  - 	if m.availableModels == nil {
  + 	if m.availableModels == nil || name == "" {
  + 	return strings.HasSuffix(name, ":cloud") || strings.HasSuffix(name, "-cloud")
server/create.go (code)
  - 			fromRef, err := parseAndValidateModelRef(r.From)
  - 			if err != nil {
  - 
  - 			fromName := fromRef.Name
  - 			remoteHost := r.RemoteHost
  - 			if fromRef.Source == modelSourceCloud && remoteHost == "" {
  - 				remoteHost = cloudProxyBaseURL
  - 			}
  + 			fromName := model.ParseName(r.From)
  + 			if !fromName.IsValid() {
  + 			if r.RemoteHost != "" {
  + 				ru, err := remoteURL(r.RemoteHost)
  + 				config.RemoteModel = r.From

### example 3
third_party/xla/xla/backends/gpu/tests/bitcast-convert.hlo (code)
  - // RUN: hlo-opt %s --platform=gpu --xla_gpu_target_config_filename=%S/../../../backends/gpu/target_config/specs/%{GPU}.txtpb | FileCheck  %s
  + // RUN: hlo-opt %s --platform=gpu --xla_gpu_target_config_filename=%S/../target_config/specs/%{GPU}.txtpb | FileCheck  %s

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

