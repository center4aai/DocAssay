# bibscan

`bibscan` is a small Python library for working with bibliographic data: it
parses BibTeX databases and CSL (Citation Style Language) styles, and renders
citations and bibliographies from the records it reads.

The package is at version `0.4.2` and requires Python 3.11 or newer.

## Status of this tree

The modules, classes, and function signatures are in place, but the parsing and
formatting functions are not implemented yet. In `0.4.2` every function accepts
no arguments and returns `None`, and every record class is created with no
arguments and starts with all of its attributes set to `None`. This README and
the rest of the documentation describe the surface that is defined today, so
that the shape of the library is clear before the bodies land.

## Installation

From a checkout of this repository:

```bash
pip install .
```

The only runtime dependencies are `lxml>=4.9` and `python-dateutil>=2.8`, both
declared in `pyproject.toml` and installed for you.

For development, install into a virtual environment and run Python from there:

```bash
python -m venv .venv
source .venv/bin/activate
pip install .
```

## Quick start

Import the pieces you need from the modules that define them; the package
`bibscan` itself only exports `__version__`.

```python
import bibscan
from bibscan.model import Entry, Name, Style
from bibscan.parser import parse_bibtex, parse_csl
from bibscan.format import format_citation, format_bibliography

print(bibscan.__version__)        # 0.4.2

entry = Entry()
entry.key = "knuth1984"
entry.entry_type = "article"
entry.fields = {"title": "Literate Programming", "year": "1984"}

name = Name()
name.family = "Knuth"
name.given = "Donald E."

style = Style()
style.style_id = "apa"
```

The bundled database `examples/library.bib` holds two entries — `knuth1984`
(an `@article`) and `lamport1994` (a `@book`) — and is a convenient file to
point the parser at once it is implemented.

## Concepts

**Records.** BibTeX entries are represented by `Entry`, with a citation `key`,
an `entry_type` such as `article` or `book`, and a `fields` mapping of the
remaining BibTeX fields. Personal names are represented by `Name`, split into
`family`, `given`, and `suffix`. CSL styles are represented by `Style`, with a
`style_id`, a human-readable `title`, and a `macros` collection.

**Parsing.** `bibscan.parser.parse_bibtex` is the entry point for BibTeX input
and `bibscan.parser.parse_csl` for CSL styles. The module also defines
`BibSyntaxError` for malformed input, carrying the `line` and `column` of the
problem. As written, `BibSyntaxError` is a plain class rather than a subclass of
`Exception`, so keep that in mind when writing `except` clauses.

**Names.** `bibscan.names` handles the awkward parts of personal names:
`parse_names` splits a name list into `Name` records and `format_name` turns a
record back into text. The module also defines a `PARTICLES` constant for the
name-particle vocabulary.

**Formatting.** `bibscan.format` renders output. `format_citation` produces a
single citation and `format_bibliography` produces a bibliography, and the
module carries the default locale in `DEFAULT_LOCALE`. Styles parsed by
`parse_csl` are what the renderers are meant to work from.

**Command line.** `bibscan.cli` contains `scan_file`, typed as returning a list
of `Entry` objects for a database, and `main`, typed as returning an `int`
process exit code. `pyproject.toml` does not declare a console-script entry
point, so installing the package does not put a `bibscan` command on your
`PATH`; call `bibscan.cli.main()` from Python instead.

## Documentation

- [`docs/recipes.md`](docs/recipes.md) — short, task-oriented examples.
- [`docs/api.md`](docs/api.md) — the complete public interface.
