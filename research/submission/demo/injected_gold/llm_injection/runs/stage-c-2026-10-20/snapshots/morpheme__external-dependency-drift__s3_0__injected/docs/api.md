# API reference

Version `0.4.2`. All public names live in the `morpheme` package, split across
four data/algorithm modules plus `morpheme.cli`.

Every function currently accepts no arguments and returns `None`, and every
class attribute is initialized to `None`; the signatures below are the intended
interface and will gain parameters and implementations as the library is
filled in. `from __future__ import annotations` is used throughout, so the
annotations are not evaluated at import time.

## `morpheme.lexicon`

### `class Lexicon`

The word list and its metadata for one language.

```python
Lexicon() -> None
```

Attributes, all set to `None` by the constructor:

| Attribute | Meaning |
| --- | --- |
| `language` | Language tag for this lexicon, matching the `language` key of an affix table. |
| `entries` | The words of the lexicon. |
| `provenance` | Where the entries came from, for traceability. |

### `load_lexicon`

```python
load_lexicon() -> Lexicon
```

Returns the lexicon to work with. The annotated return type is `Lexicon`.

### `DEFAULT_LANGUAGE`

```python
DEFAULT_LANGUAGE = "default_language"
```

Language tag used when a caller does not name one explicitly. The value is the
string `"default_language"`.

## `morpheme.affixes`

### `class Affix`

One entry of an affix table.

```python
Affix() -> None
```

Attributes, all set to `None` by the constructor:

| Attribute | Meaning |
| --- | --- |
| `form` | Surface spelling of the affix, e.g. `-alamet`, `-a`, `-ka`. |
| `kind` | Which kind of affix this entry is; not written in the shipped YAML. |
| `gloss` | Grammatical gloss, e.g. `PLURAL`, `GENITIVE`, `DIMINUTIVE`. |
| `productivity` | Productivity rating, e.g. `high` or `low`. |

### `parse_affix_table`

```python
parse_affix_table() -> list[Affix]
```

Returns the parsed affix entries, one `Affix` per table entry.

### Affix table format

The example table, `examples/tir_affixes.yaml`, is a YAML document with a
`language` key and a `suffixes` key holding the entries:

```yaml
language: tir
suffixes:
  - form: -alamet
    gloss: PLURAL
    productivity: high
  - form: -a
    gloss: GENITIVE
    productivity: high
  - form: -ka
    gloss: DIMINUTIVE
    productivity: low
```

Each entry has `form`, `gloss`, and `productivity`. `kind` is filled in on the
`Affix` object rather than read from the file.

## `morpheme.segmenter`

### `class Segmenter`

Holds the configuration for segmenting words.

```python
Segmenter() -> None
```

Attributes, all set to `None` by the constructor:

| Attribute | Meaning |
| --- | --- |
| `lexicon` | The `Lexicon` the segmenter consults. |
| `max_morphemes` | Upper bound on the number of morphemes per word. |
| `backtrack` | Whether the segmenter may retry a split after a candidate fails. |

### `segment`

```python
segment() -> list[str]
```

Returns the morphemes of a word, in surface order.

## `morpheme.lemmatize`

### `class LemmaResult`

The outcome of one lemma lookup.

```python
LemmaResult() -> None
```

Attributes, all set to `None` by the constructor:

| Attribute | Meaning |
| --- | --- |
| `surface` | The word that was looked up. |
| `lemma` | The base form it was resolved to. |
| `suffixes` | The suffixes that were stripped. |
| `confidence` | Confidence in the lookup. |

### `lookup_lemma`

```python
lookup_lemma() -> LemmaResult
```

Returns the lemma analysis for a single word.

### `lookup_many`

```python
lookup_many() -> list[LemmaResult]
```

Returns one `LemmaResult` per input word, in input order.

## `morpheme.cli`

### `main`

```python
main() -> int
```

Command-line entry point. Returns an exit status as an `int`.

The two subcommand forms the CLI is written for are:

```bash
morpheme segment --language tir "bandalamet"
morpheme lemma --language tir --file words.txt
```

`--language` selects the language pack, `segment` takes the word as a
positional argument, and `lemma --file` reads one word per line as in
`examples/words.txt`. `pyproject.toml` declares no `[project.scripts]` entry
point, so no `morpheme` executable is installed; call `main()` from Python
until one is added.

### `format_alignment`

```python
format_alignment() -> str
```

Returns the string used to display a segmentation or lemma analysis.

## Package

```python
import morpheme
morpheme.__version__  # "0.4.2"
```

The package itself exports only `__version__`; import the classes and functions
from their modules, e.g. `from morpheme.lemmatize import lookup_lemma`.
