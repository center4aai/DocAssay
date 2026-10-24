# API reference

All public names are importable from their submodules under the `sheetmusic`
package. Every function in the current release has a body that returns `None`;
the return types below are the declared types.

## `sheetmusic.models`

### `class Chord`

```python
class Chord:
    def __init__(self) -> None: ...
```

A chord. Construction takes no arguments.

| Attribute | Initial value | Description |
| --- | --- | --- |
| `root` | `None` | Root note of the chord. |
| `quality` | `None` | Chord quality. |
| `bass` | `None` | Bass note. |

### `class Progression`

```python
class Progression:
    def __init__(self) -> None: ...
```

A sequence of chords. Construction takes no arguments.

| Attribute | Initial value | Description |
| --- | --- | --- |
| `chords` | `None` | The chords in the progression. |
| `title` | `None` | Display name for the progression. |

## `sheetmusic.notes`

### `NOTE_NAMES`

Module-level constant. In the current source its value is the string
`"note_names"`.

### `note_to_semitone() -> int`

Declared to convert a note name to a semitone number. Takes no parameters in
the current source. The body returns `None`.

### `semitone_to_note() -> str`

Declared to convert a semitone number to a note name. Takes no parameters in
the current source. The body returns `None`.

## `sheetmusic.parser`

### `parse_chord() -> Chord`

Declared to parse a chord symbol into a `Chord`. Takes no parameters in the
current source. The body returns `None`.

### `parse_progression() -> Progression`

Declared to parse a progression into a `Progression`. Takes no parameters in
the current source. The body returns `None`.

## `sheetmusic.transpose`

### `transpose_chord() -> Chord`

Declared to transpose a `Chord` to another key. Takes no parameters in the
current source. The body returns `None`.

### `transpose_progression() -> Progression`

Declared to transpose a `Progression` to another key. Takes no parameters in
the current source. The body returns `None`.

## `sheetmusic.cli`

### `main() -> int`

Entry function for the command-line interface. Takes no parameters in the
current source. The body returns `None`. The package does not register a
console script for it in `pyproject.toml`.

## `sheetmusic.__version__`

The string `"0.3.0"`, defined in `sheetmusic/__init__.py`.
