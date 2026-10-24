# User guide

This guide describes the concepts behind `sheetmusic` and how the modules are
laid out. For the exact signatures, see the [API reference](api.md).

## Package layout

| Module | Purpose |
| --- | --- |
| `sheetmusic.models` | The `Chord` and `Progression` classes. |
| `sheetmusic.notes` | Note-name constant and note/semitone conversion functions. |
| `sheetmusic.parser` | Functions that parse chord symbols and progressions. |
| `sheetmusic.transpose` | Functions that transpose chords and progressions. |
| `sheetmusic.cli` | The `main` entry function for a command-line interface. |

The package also exposes `__version__` in `sheetmusic/__init__.py`, set to
`0.3.0`.

## Chords

A `Chord` has three attributes:

- `root`: the root note of the chord.
- `quality`: the chord quality (for example, a minor or seventh quality).
- `bass`: the bass note, when it differs from the root.

`Chord()` takes no arguments. All three attributes are initialized to `None`,
and you assign them directly:

```python
from sheetmusic.models import Chord

c = Chord()
c.root = "A"
c.quality = "m7"
c.bass = "C"
```

The library does not currently define a fixed set of allowed values for
`root`, `quality`, or `bass`. The attributes store whatever you assign.

## Progressions

A `Progression` groups chords under an optional title:

- `chords`: the sequence of chords in the progression.
- `title`: a display name for the progression.

Like `Chord`, `Progression()` takes no arguments and sets both attributes to
`None`:

```python
from sheetmusic.models import Chord, Progression

p = Progression()
p.title = "Two-chord vamp"
p.chords = [Chord(), Chord()]
```

## Parsing

The `sheetmusic.parser` module declares `parse_chord` (returns `Chord`) and
`parse_progression` (returns `Progression`). In the current release their
bodies return `None`, so they do not yet turn a chord symbol string into a
`Chord` object.

## Transposing

The `sheetmusic.transpose` module declares `transpose_chord` (returns `Chord`)
and `transpose_progression` (returns `Progression`). These are also stubs in
the current release.

## Note arithmetic

The `sheetmusic.notes` module declares `note_to_semitone` (returns `int`) and
`semitone_to_note` (returns `str`), which are intended to convert between note
names and semitone numbers. Both currently return `None`. The module-level
constant `NOTE_NAMES` is defined, but its value in the current source is the
placeholder string `"note_names"`.

## Command-line interface

`sheetmusic/cli.py` defines `main()`, declared to return `int`. Its body
currently returns `None`. The `pyproject.toml` file does not declare a console
script, so no `sheetmusic` command is installed by the package at this
version.
