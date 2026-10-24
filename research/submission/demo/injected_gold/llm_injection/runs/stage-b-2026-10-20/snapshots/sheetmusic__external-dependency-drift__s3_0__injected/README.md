# sheetmusic

`sheetmusic` is a small Python library for working with chord symbols and chord
progressions. It is meant for code that needs to represent a chord as a root,
a quality, and an optional bass note, group chords into a titled progression,
and transpose those chords between keys.

Version: 0.3.0. Requires Python 3.11 or newer.

## Status

The package is an early release. The module layout and public names are in
place, but the functions are currently stubs: each one is declared with its
return type and its body returns `None`. The `Chord` and `Progression` classes
can be constructed and their attributes read and set. See the
[API reference](docs/api.md) for the details of each name.

## Installation

From a checkout of the repository:

```bash
pip install .
```

For an editable install while developing:

```bash
pip install -e .
```

The only declared runtime dependency is `click>=8.1`.

## Quick start

Import the public names from the submodules:

```python
from sheetmusic.models import Chord, Progression
from sheetmusic.parser import parse_chord, parse_progression
from sheetmusic.transpose import transpose_chord, transpose_progression
from sheetmusic.notes import note_to_semitone, semitone_to_note

chord = Chord()
chord.root = "C"
chord.quality = "m"
chord.bass = "G"

progression = Progression()
progression.title = "Example"
progression.chords = [chord]
```

The functions `parse_chord`, `parse_progression`, `transpose_chord`,
`transpose_progression`, `note_to_semitone`, and `semitone_to_note` can be
imported, but in the current release they return `None`.

## Documentation

- [User guide](docs/guide.md) covers chords, progressions, and the module
  layout.
- [API reference](docs/api.md) lists every public class, function, and
  constant.
