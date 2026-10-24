# Module map

`serialscope` is a flat package: seven small modules under `serialscope/`, each
owning one step of the job, plus a pair of capture files under `examples/` that
serve as fixtures. There is no plugin layer; every public name is importable from
the module that defines it.

```
serialscope/
  README.md                  introduction and quick start
  spec.json                  project description (name, version, modules)
  pyproject.toml             packaging metadata, requires-python, pyserial
  serialscope/
    __init__.py              package docstring and __version__
    errors.py                error types
    checksums.py             crc16_ccitt, xor8, CRC16_INIT
    frames.py                Frame, FrameReader, parse_frame, STX
    codecs.py                split_fields, decode_measurement
    transport.py             SerialTransport, open_port
    config.py                ENV_DEFAULTS
    cli.py                   build_parser, main, DEFAULT_BAUD
  examples/
    balance_frames.txt       two hex-encoded balance responses
    pump_response.txt        one hex-encoded pump status response
  docs/
    walkthrough.md           tutorial
    structure.md             this file
```

## How the pieces relate

The modules follow the path a response takes from the wire to a value:

```
serial port ── transport.open_port ──> SerialTransport
                                            │  raw bytes
                                            ▼
                       frames.FrameReader / frames.parse_frame
                                 │            │
                                 │            └── checksums.crc16_ccitt / xor8
                                 ▼
                              frames.Frame (address, payload, checksum)
                                            │
                                            ▼
                        codecs.split_fields ──> codecs.decode_measurement
                                            │
                                            ▼
                                         Decimal
```

`cli` and `config` sit alongside that path rather than inside it: `config`
supplies the default port and baud rate, and `cli` is where a command-line caller
would wire the other modules together.

In this release no module imports another one. Each file only has
`from __future__ import annotations` at the top, so the modules can be read and
tested one at a time; the arrows above are the intended data flow, not import
statements.

## `serialscope/__init__.py`

The package marker. It carries the package docstring and `__version__`, which is
`"0.3.1"` — the same version as `pyproject.toml`. It does not re-export any
names, so imports go to the defining module (`from serialscope.frames import
parse_frame`, not `from serialscope import parse_frame`).

## `serialscope/errors.py`

The three error types:

- `SerialScopeError` — the umbrella name for this package's failures.
- `FramingError` — the response envelope did not line up: missing start marker,
  missing end marker, or too few bytes for a checksum.
- `ChecksumError` — the trailing bytes did not match the payload.

All three are declared as plain classes with an empty `__init__`. They do not
inherit from `Exception` in this release, so they currently function as names and
documentation of the failure modes; see `docs/walkthrough.md` step 5.

## `serialscope/checksums.py`

The two checksum routines and their starting value:

- `crc16_ccitt()` — the CRC-16 path, declared to return `int`.
- `xor8()` — the eight-bit XOR alternative, declared to return `int`.
- `CRC16_INIT` — module-level constant holding the CRC's initial value.

Code that validates a response calls one of these and compares the result with
`Frame.checksum`. Which one applies is a property of the instrument, which is
what `FrameReader.checksum_mode` is for.

## `serialscope/frames.py`

The core of the package. Everything downstream consumes a `Frame`.

- `Frame` — a parsed response. The constructor takes no arguments and sets three
  attributes: `address`, `payload`, `checksum`.
- `FrameReader` — the streaming reader. Keeps `buffer` (bytes received but not
  yet formed into a frame) and `checksum_mode` (which scheme to verify with).
  This is the class you keep alive across reads from a port.
- `parse_frame()` — one-shot conversion of a complete response into a `Frame`,
  declared to return `Frame`.
- `STX` — module-level constant naming the start-of-frame marker.

The envelope the module is built around is `0x02`, payload, `0x03`, then two
checksum bytes, as in `examples/balance_frames.txt`. `parse_frame` is for data you
already have in hand (a capture file, a single read); `FrameReader` is for data
that arrives in pieces.

## `serialscope/codecs.py`

Payload interpretation, split from framing so that a new instrument format does
not require touching the frame layer.

- `split_fields()` — breaks a payload into field strings, declared to return
  `list[str]`.
- `decode_measurement()` — converts a measurement field to a `Decimal`, declared
  to return `Decimal`. Decimal, not float, is the point: a balance that reports
  three decimals should not pick up binary rounding on the way in.

`examples/balance_frames.txt` decodes to space-separated fields
(`S`, `12.345`, `g`), while `examples/pump_response.txt` decodes to a
`;`-separated status line (`01:INFUSE;0.50ml/min`). Both end up in `split_fields`;
what counts as a measurement is decided per format.

## `serialscope/transport.py`

The serial line. This is the module that `pyserial` is a dependency for.

- `SerialTransport` — holder for the three connection settings: `port`,
  `baudrate`, `timeout`. Constructed with no arguments; all three attributes
  start as `None`.
- `open_port()` — opens the connection and returns a `SerialTransport`.

Keeping this in its own module means the rest of the package works on bytes
rather than on a live device, so a captured response can be replayed without any
hardware attached.

## `serialscope/config.py`

`ENV_DEFAULTS` is a dictionary of the two environment variables the package
recognises:

| key | default |
| --- | --- |
| `SERIALSCOPE_PORT` | `""` |
| `SERIALSCOPE_BAUD` | `""` |

Because both default to the empty string, a value you export always wins over an
unset one. `config` holds the names and defaults only; it does not read the
environment or open anything itself.

## `serialscope/cli.py`

The command-line layer:

- `build_parser()` — builds and returns an `argparse.ArgumentParser`.
- `main()` — the entry point, declared to return `int`.
- `DEFAULT_BAUD` — module-level constant for the fallback baud rate.

`pyproject.toml` declares `packages = ["serialscope"]` and no `[project.scripts]`
entry, so installing the package does not put a `serialscope` command on your
`PATH`; `main` is reachable as a normal function call. Wiring subcommands, the
port from `SERIALSCOPE_PORT`, and the baud from `SERIALSCOPE_BAUD` is what this
module exists for.

## `examples/`

Two hex-encoded captures, one response per line:

- `balance_frames.txt` — `S    12.345 g` and `S     0.000 g`.
- `pump_response.txt` — `01:INFUSE;0.50ml/min`.

They are plain text, not packaged data files: `pyproject.toml` ships only the
`serialscope` package, so read them relative to a checkout. They are the fixture
set the walkthrough builds on.

## Current state of the tree

Every function in the package is declared without parameters and has a body that
returns `None`; every class constructor takes no arguments and sets its
attributes to `None`; the three error classes have no base class. The module map
above describes what each piece is responsible for, and the signatures and
attributes are the contract the rest of the package is written against. There are
no tests in this tree and no console-script entry point.
