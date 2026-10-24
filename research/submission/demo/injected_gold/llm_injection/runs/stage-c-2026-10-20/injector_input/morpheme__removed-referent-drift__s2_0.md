# Injection task

corpus repository: `morpheme`

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
  README.md, docs/api.md, docs/concepts.md, examples/tir_affixes.yaml, examples/words.txt, morpheme/__init__.py, morpheme/affixes.py, morpheme/cli.py, morpheme/lemmatize.py, morpheme/lexicon.py, morpheme/segmenter.py, pyproject.toml, spec.json
symbols:
  morpheme.affixes.Affix, morpheme.affixes.parse_affix_table, morpheme.cli.format_alignment, morpheme.cli.main, morpheme.lemmatize.LemmaResult, morpheme.lemmatize.lookup_lemma, morpheme.lemmatize.lookup_many, morpheme.lexicon.Lexicon, morpheme.lexicon.load_lexicon, morpheme.segmenter.Segmenter, morpheme.segmenter.segment
dependencies:
  pyyaml>=6.0, regex>=2024.5
string literals:
  0.4.2, Module morpheme/affixes.py., Module morpheme/cli.py., Module morpheme/lemmatize.py., Module morpheme/lexicon.py., Module morpheme/segmenter.py., Package morpheme., Project class., Project function., default_language

## Document excerpts

### README.md
   1: # morpheme
   2: 
   3: `morpheme` is a small Python library for morphological segmentation and lemma
   4: lookup against a single language pack. It is meant for work on a modest,
   5: hand-curated lexicon: you describe the affixes of one language in a YAML table,
   6: load that table, and then ask the library how a word splits into morphemes or
   7: what its base form is.
   8: 
   9: The package is at version `0.4.2`. It requires Python 3.11 or newer and depends
  10: on `regex>=2024.5` and `PyYAML>=6.0`.
  11: 
  12: ## Installation
  13: 
  14: The project is built with setuptools and declares a single package,
  15: `morpheme`:
  16: 
  17: ```bash
  18: pip install .
  19: ```
  20: 
  21: For development, install it in editable mode so the example files stay where
  22: they are:
  23: 
  24: ```bash
  25: pip install -e .
  26: ```
  27: 
  28: ## Quick start
  29: 
  30: ```python
  31: from morpheme.affixes import parse_affix_table
  32: from morpheme.lexicon import load_lexicon
  33: from morpheme.lemmatize import lookup_lemma, lookup_many
  34: from morpheme.segmenter import segment
  35: 
  36: affixes = parse_affix_table()
  37: lexicon = load_lexicon()
  38: parts = segment()
  39: result = lookup_lemma()
  40: results = lookup_many()
  41: ```
  42: 
  43: Each call returns a value of the type described in the API reference: a list of
  44: `Affix` objects, a `Lexicon`, a list of strings, and a `LemmaResult` (or a list
  45: of them). The library currently ships as a skeleton: the entry points are in
  46: place and typed, but the parsing, loading, and segmentation logic behind them is
  47: not implemented yet, so they return `None` rather than populated results.
  48: 
  49: ## Example data
  50: 
  51: Two files under `examples/` define the sample language pack used in the
  52: documentation and in the intended command lines:
  53: 
  54: - `examples/tir_affixes.yaml` — an affix table with `language: tir` and three
  55:   suffixes: `-alamet` (gloss `PLURAL`, productivity `high`), `-a` (gloss
  56:   `GENITIVE`, productivity `high`), and `-ka` (gloss `DIMINUTIVE`, productivity
  57:   `low`).
  58: - `examples/words.txt` — a plain word list, one word per line:
  59:   `bandalamet`, `bandaka`, `banda`.
  60: 
  61: The command lines the project is aimed at are:
  62: 
  63: ```bash
  64: morpheme segment --language tir "bandalamet"
  65: morpheme lemma --language tir --file words.txt
  66: ```
  67: 
  68: `pyproject.toml` does not declare a `[project.scripts]` entry point, so there is
  69: no `morpheme` executable installed yet; the CLI lives in `morpheme/cli.py` as
  70: the functions `main()` and `format_alignment()`, which you can call directly.
  71: 
  72: ## Main concepts
  73: 
  74: - **Lexicon** — the word list for one language, together with where it came
  75:   from. `Lexicon` carries `language`, `entries`, and `provenance`, and
  76:   `DEFAULT_LANGUAGE` holds the fallback language tag.
  77: - **Affix** — one entry from an affix table: its `form` (as written, e.g.
  78:   `-ka`), its `kind`, a `gloss` such as `PLURAL`, and a `productivity` rating
  79:   such as `high` or `low`.
  80: - **Segmentation** — splitting a surface word into a list of morphemes. A
  81:   `Segmenter` is configured with a `lexicon`, a `max_morphemes` limit, and a
  82:   `backtrack` setting.
  83: - **Lemmatization** — mapping a surface form back to its lemma. A `LemmaResult`
  84:   reports the `surface` form, the `lemma`, the `suffixes` that were stripped,
  85:   and a `confidence` score.
  86: 
  87: `docs/concepts.md` explains how these pieces are meant to fit together, and
  88: `docs/api.md` lists the classes and functions with their exact signatures.
### docs/api.md
   1: # API reference
   2: 
   3: Version `0.4.2`. All public names live in the `morpheme` package, split across
   4: four data/algorithm modules plus `morpheme.cli`.
   5: 
   6: Every function currently accepts no arguments and returns `None`, and every
   7: class attribute is initialized to `None`; the signatures below are the intended
   8: interface and will gain parameters and implementations as the library is
   9: filled in. `from __future__ import annotations` is used throughout, so the
  10: annotations are not evaluated at import time.
  11: 
  12: ## `morpheme.lexicon`
  13: 
  14: ### `class Lexicon`
  15: 
  16: The word list and its metadata for one language.
  17: 
  18: ```python
  19: Lexicon() -> None
  20: ```
  21: 
  22: Attributes, all set to `None` by the constructor:
  23: 
  24: | Attribute | Meaning |
  25: | --- | --- |
  26: | `language` | Language tag for this lexicon, matching the `language` key of an affix table. |
  27: | `entries` | The words of the lexicon. |
  28: | `provenance` | Where the entries came from, for traceability. |
  29: 
  30: ### `load_lexicon`
  31: 
  32: ```python
  33: load_lexicon() -> Lexicon
  34: ```
  35: 
  36: Returns the lexicon to work with. The annotated return type is `Lexicon`.
  37: 
  38: ### `DEFAULT_LANGUAGE`
  39: 
  40: ```python
  41: DEFAULT_LANGUAGE = "default_language"
  42: ```
  43: 
  44: Language tag used when a caller does not name one explicitly. The value is the
  45: string `"default_language"`.
  46: 
  47: ## `morpheme.affixes`
  48: 
  49: ### `class Affix`
  50: 
  51: One entry of an affix table.
  52: 
  53: ```python
  54: Affix() -> None
  55: ```
  56: 
  57: Attributes, all set to `None` by the constructor:
  58: 
  59: | Attribute | Meaning |
  60: | --- | --- |
  61: | `form` | Surface spelling of the affix, e.g. `-alamet`, `-a`, `-ka`. |
  62: | `kind` | Which kind of affix this entry is; not written in the shipped YAML. |
  63: | `gloss` | Grammatical gloss, e.g. `PLURAL`, `GENITIVE`, `DIMINUTIVE`. |
  64: | `productivity` | Productivity rating, e.g. `high` or `low`. |
  65: 
  66: ### `parse_affix_table`
  67: 
  68: ```python
  69: parse_affix_table() -> list[Affix]
  70: ```
  71: 
  72: Returns the parsed affix entries, one `Affix` per table entry.
  73: 
  74: ### Affix table format
  75: 
  76: The example table, `examples/tir_affixes.yaml`, is a YAML document with a
  77: `language` key and a `suffixes` key holding the entries:
  78: 
  79: ```yaml
  80: language: tir
  81: suffixes:
  82:   - form: -alamet
  83:     gloss: PLURAL
  84:     productivity: high
  85:   - form: -a
  86:     gloss: GENITIVE
  87:     productivity: high
  88:   - form: -ka
  89:     gloss: DIMINUTIVE
  90:     productivity: low
  91: ```
  92: 
  93: Each entry has `form`, `gloss`, and `productivity`. `kind` is filled in on the
  94: `Affix` object rather than read from the file.
  95: 
  96: ## `morpheme.segmenter`
  97: 
  98: ### `class Segmenter`
  99: 
 100: Holds the configuration for segmenting words.
 101: 
 102: ```python
 103: Segmenter() -> None
 104: ```
 105: 
 106: Attributes, all set to `None` by the constructor:
 107: 
 108: | Attribute | Meaning |
 109: | --- | --- |
 110: | `lexicon` | The `Lexicon` the segmenter consults. |
 111: | `max_morphemes` | Upper bound on the number of morphemes per word. |
 112: | `backtrack` | Whether the segmenter may retry a split after a candidate fails. |
 113: 
 114: ### `segment`
 115: 
 116: ```python
 117: segment() -> list[str]
 118: ```
 119: 
 120: Returns the morphemes of a word, in surface order.
 121: 
 122: ## `morpheme.lemmatize`
 123: 
 124: ### `class LemmaResult`
 125: 
 126: The outcome of one lemma lookup.
 127: 
 128: ```python
 129: LemmaResult() -> None
 130: ```
 131: 
 132: Attributes, all set to `None` by the constructor:
 133: 
 134: | Attribute | Meaning |
 135: | --- | --- |
 136: | `surface` | The word that was looked up. |
 137: | `lemma` | The base form it was resolved to. |
 138: | `suffixes` | The suffixes that were stripped. |
 139: | `confidence` | Confidence in the lookup. |
 140: 
 141: ### `lookup_lemma`
 142: 
 143: ```python
 144: lookup_lemma() -> LemmaResult
 145: ```
 146: 
 147: Returns the lemma analysis for a single word.
 148: 
 149: ### `lookup_many`
 150: 
 151: ```python
 152: lookup_many() -> list[LemmaResult]
 153: ```
 154: 
 155: Returns one `LemmaResult` per input word, in input order.
 156: 
 157: ## `morpheme.cli`
 158: 
 159: ### `main`
 160: 
 161: ```python
 162: main() -> int
 163: ```
 164: 
 165: Command-line entry point. Returns an exit status as an `int`.
 166: 
 167: The two subcommand forms the CLI is written for are:
 168: 
 169: ```bash
 170: morpheme segment --language tir "bandalamet"
 171: morpheme lemma --language tir --file words.txt
 172: ```
 173: 
 174: `--language` selects the language pack, `segment` takes the word as a
 175: positional argument, and `lemma --file` reads one word per line as in
 176: `examples/words.txt`. `pyproject.toml` declares no `[project.scripts]` entry
 177: point, so no `morpheme` executable is installed; call `main()` from Python
 178: until one is added.
 179: 
 180: ### `format_alignment`
 181: 
 182: ```python
 183: format_alignment() -> str
 184: ```
 185: 
 186: Returns the string used to display a segmentation or lemma analysis.
 187: 
 188: ## Package
 189: 
 190: ```python
 191: import morpheme
 192: morpheme.__version__  # "0.4.2"
 193: ```
 194: 
 195: The package itself exports only `__version__`; import the classes and functions
 196: from their modules, e.g. `from morpheme.lemmatize import lookup_lemma`.
### docs/concepts.md
   1: # Concepts
   2: 
   3: `morpheme` is organized around one assumption: a language pack is small enough
   4: to keep as data. Rather than hard-coding morphological rules, the library
   5: separates four things — the affix inventory, the lexicon, the segmentation
   6: procedure, and the lemma lookup — and lets each be inspected on its own.
   7: 
   8: These notes describe the model the code is shaped around. The modules are
   9: deliberately thin at version `0.4.2`: the classes, attributes, and function
  10: signatures described below exist, but the algorithms behind them are not filled
  11: in yet.
  12: 
  13: ## The affix inventory is the starting point
  14: 
  15: Everything the segmenter and the lemmatizer can recognize has to be declared in
  16: an affix table. In the example pack, `examples/tir_affixes.yaml`, the table is a
  17: YAML document with two top-level keys:
  18: 
  19: ```yaml
  20: language: tir
  21: suffixes:
  22:   - form: -alamet
  23:     gloss: PLURAL
  24:     productivity: high
  25:   - form: -a
  26:     gloss: GENITIVE
  27:     productivity: high
  28:   - form: -ka
  29:     gloss: DIMINUTIVE
  30:     productivity: low
  31: ```
  32: 
  33: Each entry under `suffixes` becomes an `Affix`:
  34: 
  35: - `form` is the surface spelling of the morpheme, including its leading hyphen
  36:   (`-alamet`, `-a`, `-ka`). Keeping the hyphen in the form means the written
  37:   affix and the string that has to be matched look the same.
  38: - `gloss` is the grammatical label in the conventional small-caps style —
  39:   `PLURAL`, `GENITIVE`, `DIMINUTIVE`. It is descriptive metadata; it is what
  40:   makes a segmentation readable to a linguist.
  41: - `productivity` records how freely the affix combines: the example table uses
  42:   `high` for the plural and genitive suffixes and `low` for the diminutive,
  43:   since a diminutive is typically more selective about its hosts.
  44: - `kind` is on the `Affix` object but not in the YAML. It is the attribute that
  45:   names which side of the stem the affix attaches to. The shipped table lists
  46:   only suffixes, so it uses only the `suffixes` key and every entry's kind is
  47:   the same.
  48: 
  49: `parse_affix_table()` is the function that turns a table like this into a
  50: `list[Affix]`. Splitting the table by kind, and turning the productivity
  51: keyword into whatever the segmenter compares against, belongs there rather than
  52: in the segmenter, so that a second language pack only has to add a file.
  53: 
  54: ## The lexicon supplies the stems
  55: 
  56: An affix table says what can attach. A lexicon says what it attaches to.
  57: `Lexicon` holds three attributes:
  58: 
  59: - `language` — the language tag, matching the `language` key of the affix
  60:   table. `DEFAULT_LANGUAGE` is the tag used when none is supplied; in this
  61:   version its value is the string `"default_language"`.
  62: - `entries` — the word list for the language. The example list is a plain text
  63:   file, `examples/words.txt`, one word per line.
  64: - `provenance` — where the entries came from. This is the reason the attribute
  65:   is on the object at all: for a hand-curated list, knowing which source a
  66:   cohort of words was drawn from is part of the data, not an afterthought, and
  67:   it keeps the lexicon traceable when entries are merged.
  68: 
  69: `load_lexicon()` returns a `Lexicon`. Because both the lexicon and the affix
  70: table carry a language tag, the two are meant to be opened for the same language
  71: and passed around together, which is what the `--language` flag in the intended
  72: command lines selects.
  73: 
  74: ## Segmentation
  75: 
  76: `segment()` returns a `list[str]`: the surface word cut into its morphemes in
  77: order. A `Segmenter` is the object that holds the configuration for doing this:
  78: 
  79: - `lexicon` — the lexicon whose entries bound what counts as a plausible stem.
  80: - `max_morphemes` — a cap on how many pieces a word may be cut into. Without a
  81:   cap, a table with very short affixes can always produce longer and longer
  82:   analyses, so the limit keeps the search finite.
  83: - `backtrack` — whether the segmenter may abandon a candidate split and try the
  84:   next one. Longest-match-first segmentation is cheap but gets stuck when the
  85:   longest affix leaves an unanalyzable remainder; allowing backtracking is what
  86:   lets the segmenter recover from that.
  87: 
  88: The example word `bandalamet` shows the intended shape of the problem. The table
  89: offers `-alamet` and `-a`, which overlap, so a greedy pass and a backtracking
  90: pass can disagree about where the boundaries fall, and the lexicon has to be
  91: consulted to decide.
  92: 
  93: ## Lemmatization
  94: 
  95: Lemmatization is the inverse question: given a surface word, what is the lemma,
  96: and what was removed to get there? `lookup_lemma()` returns a `LemmaResult` with
  97: four attributes:
  98: 
  99: - `surface` — the word as it was looked up.
 100: - `lemma` — the base form.
 101: - `suffixes` — the affixes that were stripped, so the answer can be shown as an
 102:   explicit alignment rather than a bare string.
 103: - `confidence` — how sure the lookup is. Segmentations that are unique and
 104:   fully attested in the lexicon should score higher than ones that needed
 105:   backtracking or left an unattested stem.
 106: 
 107: `lookup_many()` applies the same lookup to a series of words and returns a
 108: `list[LemmaResult]`, which is what a word-list input such as
 109: `examples/words.txt` produces.
 110: 
 111: ## Presentation
 112: 
 113: `format_alignment()` produces a string: the human-readable rendering of a
 114: segmentation or lemma analysis. Keeping formatting in one function means the
 115: CLI and any caller that prints results show the same alignment, and it keeps
 116: string assembly out of the segmentation code.
  … (truncated)
### examples/words.txt
  … (truncated)

## Examples (few-shot)

Real incidents of this kind, rendered as bare `before → after` excerpts under a
`<file> (doc|code)` header. Use them to understand what kind of artifact tends to
drift; do not copy their wording or content.

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
Documentation/rust/quick-start.rst (doc)
  - 
  - If GDB/Binutils is used and Rust symbols are not getting demangled, the reason
  - is the toolchain does not support Rust's new v0 mangling scheme yet.
  - There are a few ways out:
  - 
  - - Install a newer release (GDB >= 10.2, Binutils >= 2.36).
  - 
  - - Some versions of GDB (e.g. vanilla GDB 10.1) are able to use

