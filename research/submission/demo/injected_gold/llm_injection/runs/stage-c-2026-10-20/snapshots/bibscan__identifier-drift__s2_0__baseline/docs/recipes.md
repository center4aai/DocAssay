# Recipes

Short, self-contained examples for the tasks you are most likely to want.
They use the public interface described in [`api.md`](api.md).

A note that applies to every recipe below: in `0.4.2` the functions in
`bibscan` take no arguments yet and return `None`, and the record classes start
out empty. The recipes therefore show how to set up and inspect records
directly, and show the call sites that will produce the data once the
implementations are in place.

## Install and confirm the version

```bash
pip install .
python -c "import bibscan; print(bibscan.__version__)"
```

That prints `0.4.2`. The package requires Python 3.11 or newer.

## Find the symbol you need

Each part of the library lives in its own module; nothing beyond
`__version__` is re-exported at package level.

```python
from bibscan.model import Entry, Name, Style
from bibscan.parser import BibSyntaxError, parse_bibtex, parse_csl
from bibscan.names import PARTICLES, parse_names, format_name
from bibscan.format import DEFAULT_LOCALE, format_citation, format_bibliography
from bibscan.cli import scan_file, main
```

## Build an entry record by hand

`Entry` is a plain record with three attributes, all `None` on a fresh
instance.

```python
from bibscan.model import Entry

entry = Entry()
entry.key = "knuth1984"
entry.entry_type = "article"
entry.fields = {
    "author": "Knuth, Donald E.",
    "title": "Literate Programming",
    "journal": "The Computer Journal",
    "year": "1984",
    "volume": "27",
    "number": "2",
    "pages": "97--111",
}

print(entry.key, entry.entry_type)   # knuth1984 article
```

This is the same entry that appears first in `examples/library.bib`.

## Load the bundled example database

The repository ships one database, `examples/library.bib`, with two entries:
`knuth1984` (`@article`) and `lamport1994` (`@book`). Reading it as text needs
nothing from the library:

```python
from pathlib import Path

path = Path("examples/library.bib")
text = path.read_text(encoding="utf-8")
print(text.count("@"))   # 2
```

Once `parse_bibtex` is implemented, pass the file contents to it and iterate
over the returned `Entry` objects:

```python
from bibscan.parser import parse_bibtex

entries = parse_bibtex()
for entry in entries or []:
    print(entry.key, entry.entry_type)
```

The `or []` guard is there because the function currently returns `None`.

## Read a CSL style

A style is a `Style` record: an identifier, a title, and the macros the style
defines.

```python
from bibscan.model import Style

style = Style()
style.style_id = "apa"
style.title = "American Psychological Association 7th edition"
style.macros = {"author": "...", "issued": "..."}

print(style.style_id)
```

`parse_csl` is the function that will build this record from CSL input:

```python
from bibscan.parser import parse_csl

style = parse_csl()
```

## Split and reformat a name

Name handling lives in `bibscan.names`. `Name` keeps the parts separate so that
"family name first" and "given name first" styles can be produced from the same
record.

```python
from bibscan.model import Name
from bibscan.names import format_name, parse_names

name = Name()
name.family = "van Beethoven"
name.given = "Ludwig"
name.suffix = None

# Name lists in, Name records out.
names = parse_names()

# A Name record in, display text out.
label = format_name()
```

The module also exposes `PARTICLES`, the token used for the particle vocabulary
("van", "de", "von", and so on) that the name logic consults:

```python
from bibscan.names import PARTICLES

print(PARTICLES)   # particles
```

If you need a particle list before the parser exists, keep your own:

```python
PARTICLE_WORDS = {"van", "von", "de", "der", "del", "da", "di"}
```

## Render a citation and a bibliography

Both renderers live in `bibscan.format`, which also holds the default locale in
`DEFAULT_LOCALE`.

```python
from bibscan.format import DEFAULT_LOCALE, format_bibliography, format_citation

print(DEFAULT_LOCALE)      # default_locale

inline = format_citation()      # str, once implemented
listing = format_bibliography() # str, once implemented
```

Formatting is intended to take a `Style`, so the usual flow is: parse the
database, parse the style, then render.

```python
from bibscan.format import format_bibliography
from bibscan.parser import parse_bibtex, parse_csl

entries = parse_bibtex()
style = parse_csl()
body = format_bibliography()
```

For the CLI-shaped version of the same job, `scan_file` returns the entries for
a database and `main` returns an exit code:

```python
from bibscan.cli import main, scan_file

entries = scan_file()
raise SystemExit(main())
```

## Handle a syntax error

Parse failures are reported with `BibSyntaxError`, which records where the
problem was found:

```python
from bibscan.parser import BibSyntaxError

err = BibSyntaxError()
err.line = 9
err.column = 1

print(f"bad input at line {err.line}, column {err.column}")
```

One caveat when writing handlers: `BibSyntaxError` is declared as a plain class,
not as a subclass of `Exception`, so an `except BibSyntaxError:` clause will not
catch it as things stand. If you need to raise one yourself, subclass it first:

```python
class BibError(BibSyntaxError, Exception):
    pass
```

## Keep records in a lookup table

Because `Entry` is a simple mutable record, building an index by citation key is
a few lines:

```python
from bibscan.model import Entry
from bibscan.parser import parse_bibtex

by_key = {}
for entry in parse_bibtex() or []:
    by_key[entry.key] = entry

print(by_key.get("lamport1994"))
```

## Constructing records defensively

Every record class takes no constructor arguments and initialises its attributes
to `None`, so tests and fixtures can fill in only the fields they care about:

```python
from bibscan.model import Entry

def make_entry(key: str, entry_type: str = "misc", **fields: str) -> Entry:
    entry = Entry()
    entry.key = key
    entry.entry_type = entry_type
    entry.fields = dict(fields)
    return entry

print(make_entry("example2026", title="A Title").fields)
```
