# morpheme

`morpheme` is a small Python library for morphological segmentation and lemma
lookup against a single language pack. It is meant for work on a modest,
hand-curated lexicon: you describe the affixes of one language in a YAML table,
load that table, and then ask the library how a word splits into morphemes or
what its base form is.

The package is at version `0.4.2`. It requires Python 3.11 or newer and depends
on `regex>=2024.5` and `PyYAML>=6.0`.

## Installation

The project is built with setuptools and declares a single package,
`morpheme`:

```bash
pip install .
```

For development, install it in editable mode so the example files stay where
they are:

```bash
pip install -e .
```

## Quick start

```python
from morpheme.affixes import parse_affix_table
from morpheme.lexicon import load_lexicon
from morpheme.lemmatize import lookup_lemma, lookup_many
from morpheme.segmenter import segment

affixes = parse_affix_table()
lexicon = load_lexicon()
parts = segment()
result = lookup_lemma()
results = lookup_many()
```

Each call returns a value of the type described in the API reference: a list of
`Affix` objects, a `Lexicon`, a list of strings, and a `LemmaResult` (or a list
of them). The library currently ships as a skeleton: the entry points are in
place and typed, but the parsing, loading, and segmentation logic behind them is
not implemented yet, so they return `None` rather than populated results.

## Example data

Two files under `examples/` define the sample language pack used in the
documentation and in the intended command lines:

- `examples/tir_affixes.yaml` — an affix table with `language: tir` and three
  suffixes: `-alamet` (gloss `PLURAL`, productivity `high`), `-a` (gloss
  `GENITIVE`, productivity `high`), and `-ka` (gloss `DIMINUTIVE`, productivity
  `low`).
- `examples/words.txt` — a plain word list, one word per line:
  `bandalamet`, `bandaka`, `banda`.

The command lines the project is aimed at are:

```bash
morpheme segment --language tir "bandalamet"
morpheme lemma --language tir --file words.txt
```

`pyproject.toml` does not declare a `[project.scripts]` entry point, so there is
no `morpheme` executable installed yet; the CLI lives in `morpheme/cli.py` as
the functions `main()` and `format_alignment()`, which you can call directly.

## Main concepts

- **Lexicon** — the word list for one language, together with where it came
  from. `Lexicon` carries `language`, `entries`, and `provenance`, and
  `DEFAULT_LANGUAGE` holds the fallback language tag.
- **Affix** — one entry from an affix table: its `form` (as written, e.g.
  `-ka`), its `kind`, a `gloss` such as `PLURAL`, and a `productivity` rating
  such as `high` or `low`.
- **Segmentation** — splitting a surface word into a list of morphemes. A
  `Segmenter` is configured with a `lexicon`, a `max_morphemes` limit, and a
  `backtrack` setting.
- **Lemmatization** — mapping a surface form back to its lemma. A `LemmaResult`
  reports the `surface` form, the `lemma`, the `suffixes` that were stripped,
  and a `confidence` score.

`docs/concepts.md` explains how these pieces are meant to fit together, and
`docs/api.md` lists the classes and functions with their exact signatures.
