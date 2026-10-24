# serialscope

`serialscope` is about the serial-line responses that lab instruments send back —
the kind you get from a balance that answers `S    12.345 g` or a syringe pump
that answers `01:INFUSE;0.50ml/min`. It provides the framing, checksum, and
decoding layers that stand between those bytes and a usable value.

The package is aimed at people writing small acquisition scripts or rig
controllers: you already know which port your instrument is on, and you want the
bytes turned into a number without re-implementing the same envelope parser for
every device model.

Version 0.3.1. Python 3.11 or newer.

## Install

```bash
pip install -e .
```

The only runtime dependency is `pyserial>=3.5`, which is installed for you.

## What a response looks like

Instrument responses in this family are short ASCII payloads wrapped in a
delimiter envelope. Both capture files in `examples/` follow the same shape:

```
0x02  ... ASCII payload ...  0x03  <checksum> <checksum>
```

`examples/balance_frames.txt` holds two weighings:

```
02 53 20 20 20 20 31 32 2e 33 34 35 20 67 03 1a 4f
02 53 20 20 20 20 20 30 2e 30 30 30 20 67 03 12 3d
```

which read as `S    12.345 g` and `S     0.000 g`, and
`examples/pump_response.txt` holds one pump status line:

```
02 30 31 3a 49 4e 46 55 53 45 3b 30 2e 35 30 6d 6c 2f 6d 69 6e 03 5c 2a
```

which reads as `01:INFUSE;0.50ml/min`.

## Quick start

The pipeline, in code — a stored response in, a `Decimal` out:

```python
from serialscope.frames import parse_frame
from serialscope.codecs import split_fields, decode_measurement

raw = bytes.fromhex("02 53 20 20 20 20 31 32 2e 33 34 35 20 67 03 1a 4f")

frame = parse_frame()            # -> Frame: address, payload, checksum
fields = split_fields()          # -> list[str]
value = decode_measurement()     # -> Decimal
```

Read live from an instrument instead:

```python
from serialscope.transport import open_port
from serialscope.frames import FrameReader

transport = open_port()          # -> SerialTransport
reader = FrameReader()
```

`open_port()` hands back a `SerialTransport` whose `port`, `baudrate`, and
`timeout` attributes describe the connection; `FrameReader` accumulates incoming
bytes in `buffer` and validates with the checksum scheme named by
`checksum_mode`.

Note that in 0.3.1 these entry points are declared without parameters and return
`None` — the snippet shows where each call sits in the pipeline, not a working
conversion. The `->` comments are the declared return types.

## Main concepts

**Frames.** A `Frame` is the unit everything else works on: the instrument
`address`, the raw `payload` bytes, and the `checksum` that came with them.
`frames.parse_frame` is the one-shot parser for a complete captured response, and
`STX` names the start-of-frame marker the module is built around. `FrameReader`
is the streaming counterpart — it keeps a `buffer` of whatever has arrived so far
and a `checksum_mode` selecting how checksums are checked.

**Checksums.** `checksums.crc16_ccitt` and `checksums.xor8` are the two schemes
the module offers for the trailing checksum bytes; `CRC16_INIT` is the initial
value for the CRC routine.

**Decoding.** Raw payloads are two different things depending on the instrument:
balances send fixed-width numeric text, pumps send `;`-separated status fields.
`codecs.split_fields` breaks a payload into its fields, and
`codecs.decode_measurement` converts a measurement field into a `Decimal` so you
do not inherit binary floating-point rounding on a 0.001 g reading.

**Transport.** `transport.open_port` opens the serial line and returns a
`SerialTransport`; `transport.SerialTransport` is the small holder for `port`,
`baudrate`, and `timeout`.

**Configuration and the command line.** `config.ENV_DEFAULTS` lists the two
environment variables the package recognises, `SERIALSCOPE_PORT` and
`SERIALSCOPE_BAUD`, both defaulting to the empty string. `cli.build_parser`
builds the argument parser and `cli.main` is the entry point, with
`cli.DEFAULT_BAUD` as the fallback baud rate.

**Errors.** `errors` defines `SerialScopeError` together with the two specific
failure modes it names: `FramingError` (the envelope did not line up) and
`ChecksumError` (the trailing bytes did not match the payload).

## Current state

The modules in this release define the public surface — names, attributes, and
declared return types — but every function takes no arguments, its body is an
empty placeholder, the error classes have no exception base, and
`pyproject.toml` registers no `serialscope` console script. Treat the signatures
and attributes described here as the contract, and see `docs/walkthrough.md` for
what each step of the pipeline is
for.

## Where to go next

- `docs/walkthrough.md` — decode a captured balance response end to end.
- `docs/structure.md` — what each module is responsible for and how the pieces
  fit together.
