# bibscan API reference

Version `0.4.2`. Python 3.11 or newer.

```python
import bibscan
bibscan.__version__   # "0.4.2"
```

The package's `__init__.py` defines only `__version__`. Import everything else
from the module that defines it.

Module summary:

| Module | Contents |
| --- | --- |
| `bibscan.model` | `Entry`, `Name`, `Style` |
| `bibscan.parser` | `BibSyntaxError`, `parse_bibtex`, `parse_csl` |
| `bibscan.names` | `PARTICLES`, `parse_names`, `format_name` |
| `bibscan.format` | `DEFAULT_LOCALE`, `format_citation`, `format_bibliography` |
| `bibscan.cli` | `scan_file`, `main` |

## bibscan.model

### `class Entry`

A single BibTeX record. Constructed with no arguments; all attributes are
initialised to `None`.

| Attribute | Meaning |
| --- | --- |
| `key` | The citation key, e.g. `"knuth1984"` |
| `entry_type` | The BibTeX entry type, e.g. `"article"` or `"book"` |
| `fields` | The remaining BibTeX fields for the entry |

```python
from bibscan.model import Entry

entry = Entry()
entry.key = "lamport1994"
entry.entry_type = "book"
entry.fields = {"title": "LaTeX: A Document Preparation System", "year": "1994"}
```

### `class Name`

One personal name, split into parts so that different name orders can be
rendered from the same record. Constructed with no arguments; all attributes are
initialised to `None`.

| Attribute | Meaning |
| --- | --- |
| `family` | Family name, including any particle |
| `given` | Given names |
| `suffix` | Name suffix such as `"Jr."` |

### `class Style`

A CSL style. Constructed with no arguments; all attributes are initialised to
`None`.

| Attribute | Meaning |
| --- | --- |
| `style_id` | Identifier of the style, e.g. `"apa"` |
| `title` | Human-readable style title |
| `macros` | The macros defined by the style |

## bibscan.parser

### `class BibSyntaxError`

Reports a malformed input. Constructed with no arguments; attributes are
initialised to `None`.

| Attribute | Meaning |
| --- | --- |
| `line` | Line number where the problem was found |
| `column` | Column number where the problem was found |

`BibSyntaxError` is declared as a plain class with no base class other than the
implicit `object`; it is **not** a subclass of `Exception`.

### `parse_bibtex() -> list[Entry]`

Parses a BibTeX database and returns its entries as `Entry` objects.

The function is declared with an empty parameter list and currently returns
`None`.

### `parse_csl() -> Style`

Parses a CSL style and returns it as a `Style`.

The function is declared with an empty parameter list and currently returns
`None`.

## bibscan.names

### `PARTICLES`

Module-level constant:

```python
PARTICLES = "particles"
```

It is the token for the particle vocabulary used when splitting names such as
"van Beethoven" or "de la Cruz".

### `parse_names() -> list[Name]`

Splits a name list into `Name` records.

The function is declared with an empty parameter list and currently returns
`None`.

### `format_name() -> str`

Formats a `Name` record as display text.

The function is declared with an empty parameter list and currently returns
`None`.

## bibscan.format

### `DEFAULT_LOCALE`

Module-level constant holding the default locale for rendered output:

```python
DEFAULT_LOCALE = "default_locale"
```

### `format_citation() -> str`

Renders a single citation.

The function is declared with an empty parameter list and currently returns
`None`.

### `format_bibliography() -> str`

Renders a bibliography.

The function is declared with an empty parameter list and currently returns
`None`.

## bibscan.cli

### `scan_file() -> list[Entry]`

Reads a BibTeX database and returns its entries, in the same form as
`parse_bibtex`.

The function is declared with an empty parameter list and currently returns
`None`.

### `main() -> int`

Command-line entry function; the return value is the process exit code.

The function is declared with an empty parameter list and currently returns
`None`.

`pyproject.toml` declares no console-script entry point, so there is no
installed `bibscan` command. Call it from Python:

```python
from bibscan.cli import main

raise SystemExit(main())
```

## Notes on the current implementation

- Function bodies are placeholders: they take no arguments and return `None`.
  Calls are safe, but they do not read files, parse anything, or produce output.
- The record classes have no constructor parameters. Create an instance with no
  arguments and assign the attributes you need.
- Type annotations on the parser functions (`list[Entry]`, `Style`) are written
  as strings by `from __future__ import annotations`, and `Entry` and `Style`
  are not imported in `bibscan/parser.py`. The annotations describe intent; they
  are not resolvable at runtime here.
