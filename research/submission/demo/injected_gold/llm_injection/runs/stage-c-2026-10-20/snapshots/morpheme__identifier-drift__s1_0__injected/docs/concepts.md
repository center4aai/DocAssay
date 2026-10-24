# Concepts

`morpheme` is organized around one assumption: a language pack is small enough
to keep as data. Rather than hard-coding morphological rules, the library
separates four things — the affix inventory, the lexicon, the segmentation
procedure, and the lemma lookup — and lets each be inspected on its own.

These notes describe the model the code is shaped around. The modules are
deliberately thin at version `0.4.2`: the classes, attributes, and function
signatures described below exist, but the algorithms behind them are not filled
in yet.

## The affix inventory is the starting point

Everything the segmenter and the lemmatizer can recognize has to be declared in
an affix table. In the example pack, `examples/tir_affixes.yaml`, the table is a
YAML document with two top-level keys:

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

Each entry under `suffixes` becomes an `Affix`:

- `form` is the surface spelling of the morpheme, including its leading hyphen
  (`-alamet`, `-a`, `-ka`). Keeping the hyphen in the form means the written
  affix and the string that has to be matched look the same.
- `gloss` is the grammatical label in the conventional small-caps style —
  `PLURAL`, `GENITIVE`, `DIMINUTIVE`. It is descriptive metadata; it is what
  makes a segmentation readable to a linguist.
- `productivity` records how freely the affix combines: the example table uses
  `high` for the plural and genitive suffixes and `low` for the diminutive,
  since a diminutive is typically more selective about its hosts.
- `kind` is on the `Affix` object but not in the YAML. It is the attribute that
  names which side of the stem the affix attaches to. The shipped table lists
  only suffixes, so it uses only the `suffixes` key and every entry's kind is
  the same.

`parse_affix_table()` is the function that turns a table like this into a
`list[Affix]`. Splitting the table by kind, and turning the productivity
keyword into whatever the segmenter compares against, belongs there rather than
in the segmenter, so that a second language pack only has to add a file.

## The lexicon supplies the stems

An affix table says what can attach. A lexicon says what it attaches to.
`Lexicon` holds three attributes:

- `language` — the language tag, matching the `language` key of the affix
  table. `DEFAULT_LANGUAGE` is the tag used when none is supplied; in this
  version its value is the string `"default_language"`.
- `entries` — the word list for the language. The example list is a plain text
  file, `examples/words.txt`, one word per line.
- `provenance` — where the entries came from. This is the reason the attribute
  is on the object at all: for a hand-curated list, knowing which source a
  cohort of words was drawn from is part of the data, not an afterthought, and
  it keeps the lexicon traceable when entries are merged.

`load_lexicon()` returns a `Lexicon`. Because both the lexicon and the affix
table carry a language tag, the two are meant to be opened for the same language
and passed around together, which is what the `--language` flag in the intended
command lines selects.

## Segmentation

`segment()` returns a `list[str]`: the surface word cut into its morphemes in
order. A `Segmenter` is the object that holds the configuration for doing this:

- `lexicon` — the lexicon whose entries bound what counts as a plausible stem.
- `max_morphemes` — a cap on how many pieces a word may be cut into. Without a
  cap, a table with very short affixes can always produce longer and longer
  analyses, so the limit keeps the search finite.
- `backtrack` — whether the segmenter may abandon a candidate split and try the
  next one. Longest-match-first segmentation is cheap but gets stuck when the
  longest affix leaves an unanalyzable remainder; allowing backtracking is what
  lets the segmenter recover from that.

The example word `bandalamet` shows the intended shape of the problem. The table
offers `-alamet` and `-a`, which overlap, so a greedy pass and a backtracking
pass can disagree about where the boundaries fall, and the lexicon has to be
consulted to decide.

## Lemmatization

Lemmatization is the inverse question: given a surface word, what is the lemma,
and what was removed to get there? `lookup_lemma()` returns a `LemmaResult` with
four attributes:

- `surface` — the word as it was looked up.
- `lemma` — the base form.
- `suffixes` — the affixes that were stripped, so the answer can be shown as an
  explicit alignment rather than a bare string.
- `confidence` — how sure the lookup is. Segmentations that are unique and
  fully attested in the lexicon should score higher than ones that needed
  backtracking or left an unattested stem.

`lookup_many()` applies the same lookup to a series of words and returns a
`list[LemmaResult]`, which is what a word-list input such as
`examples/words.txt` produces.

## Presentation

`format_alignment()` produces a string: the human-readable rendering of a
segmentation or lemma analysis. Keeping formatting in one function means the
CLI and any caller that prints results show the same alignment, and it keeps
string assembly out of the segmentation code.

The CLI in `morpheme/cli.py` is intentionally thin. `main()` returns an `int`
in the usual command-line convention and is where the two intended subcommands
are dispatched:

```bash
morpheme segment --language tir "bandalamet"
morpheme lemma --language tir --file words.txt
```

The first takes a single word on the command line; the second reads a file of
one word per line, like `examples/words.txt`. `pyproject.toml` does not yet
declare a `[project.scripts]` entry point, so these are the target forms rather
than invocations you can run from an installed package.
