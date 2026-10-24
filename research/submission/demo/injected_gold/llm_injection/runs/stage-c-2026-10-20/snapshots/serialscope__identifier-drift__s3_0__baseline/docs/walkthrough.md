# Walkthrough: decoding a balance capture

This tutorial walks through the steps that turn a captured balance response into
a `Decimal` weighing, then points the same steps at a live port. It uses the two
files under `examples/`, so you can follow it without any hardware attached.

## 1. Install the package

From the repository root:

```bash
pip install -e .
python -c "import serialscope; print(serialscope.__version__)"
```

You should see `0.3.1`. If the import fails, check that you are on Python 3.11
or newer — that is what `pyproject.toml` requires.

## 2. Look at the capture

`examples/balance_frames.txt` contains two responses, one per line, written as
space-separated hex:

```
02 53 20 20 20 20 31 32 2e 33 34 35 20 67 03 1a 4f
02 53 20 20 20 20 20 30 2e 30 30 30 20 67 03 12 3d
```

Every response has the same envelope:

| position | content |
| --- | --- |
| first byte | `0x02`, the start-of-frame marker |
| middle | ASCII payload |
| then | `0x03`, the end-of-frame marker |
| last two bytes | checksum |

Because the file is hex text, the first job in your own script is to get real
bytes:

```python
from pathlib import Path

lines = Path("examples/balance_frames.txt").read_text().splitlines()
frames = [bytes.fromhex(line) for line in lines if line.strip()]

print(len(frames), frames[0][:1], frames[0][-3:-2])
```

That prints `2 b'\x02' b'\x03'`: two frames, each starting at `0x02` and ending
its payload at `0x03`.

## 3. Scale up to the payload

With the envelope confirmed, the payload is everything between the markers:

```python
for raw in frames:
    payload = raw[1:-3]
    print(payload.decode("ascii"))
```

```
S    12.345 g
S     0.000 g
```

The two readings differ only in the numeric field: 12.345 g and 0.000 g. Note
that the field widths are padded with spaces, which is why you do not want to
slice by offset in your own code — split on whitespace instead.

## 4. Where `serialscope` takes over

The manual steps above map onto the package like this:

```python
from serialscope.frames import parse_frame
from serialscope.codecs import split_fields, decode_measurement

frame = parse_frame()            # -> Frame, holds address, payload, checksum
fields = split_fields()          # -> list[str], one entry per payload field
reading = decode_measurement()   # -> Decimal, e.g. 12.345
```

- `parse_frame` is the one-shot step for a complete response: the resulting
  `Frame` carries the `address`, the `payload` bytes, and the trailing `checksum`
  as separate attributes. For a stream of responses you use `FrameReader`
  instead, which keeps arriving bytes in `buffer` and knows which scheme to check
  via `checksum_mode`.
- `split_fields` is the payload split from step 3, returning the field strings as
  a `list[str]`.
- `decode_measurement` produces the `Decimal` — not a `float` — so a 0.001 g
  reading keeps its digits.

In 0.3.1 these functions are declared without parameters and return `None`; the
three-step snippet shows the shape of the pipeline and the declared return types,
not a completed conversion. The manual slicing in step 3 is what the parser is
responsible for.

## 5. Check the checksum

The two bytes after `0x03` are the checksum slot, and `Frame.checksum` is where
the parsed response carries them. `serialscope.checksums` provides both schemes
this family of instruments uses:

```python
from serialscope.checksums import crc16_ccitt, xor8, CRC16_INIT
```

`crc16_ccitt` is the CRC path, with `CRC16_INIT` holding its initial value;
`xor8` is the simple one-byte alternative for instruments that use it.
Verifying a response means recomputing over the same bytes and comparing with
`frame.checksum`. A mismatch is the case `errors.ChecksumError` exists for; a
frame whose markers do not line up is the case for `errors.FramingError`. The
error module names all three types — `errors.SerialScopeError`,
`errors.FramingError`, `errors.ChecksumError` — though in this release they are
plain classes with no behavior and no exception base, so you cannot raise or
catch them as exceptions yet.

This is also why the pump capture ends with a different pair of bytes from the
balance frames: checksums are computed over the payload, so a status line
`01:INFUSE;0.50ml/min` and a weighing `S    12.345 g` do not share one.

## 6. From a capture file to a live port

Once the interpretation is right on stored data, switch the source from a file
to the serial line:

```python
from serialscope.transport import open_port, SerialTransport
from serialscope.frames import FrameReader

transport = open_port()          # -> SerialTransport
reader = FrameReader()
```

`SerialTransport` is a small holder for the three connection settings: `port`,
`baudrate`, and `timeout`. `open_port` is the function that establishes the
connection and returns one.

You do not have to hard-code the port and speed. The package recognises two
environment variables, listed in `serialscope/config.py` as `ENV_DEFAULTS`:

```bash
export SERIALSCOPE_PORT=/dev/ttyUSB0
export SERIALSCOPE_BAUD=9600
```

Both default to the empty string, so anything you export overrides an unset
value. The baud rate is a property of the instrument; the fallback constant in
the CLI module is `cli.DEFAULT_BAUD`.

## 7. Checking your setup

- **`ModuleNotFoundError: serialscope`** — install with `pip install -e .` from
  the repository root, not from inside `serialscope/`.
- **A frame that ends early** — the capture is truncated; there is no `0x03` and
  no checksum slot. That is a framing problem, not a decoding one.
- **A payload that will not decode as ASCII** — you are probably including the
  checksum bytes in the slice; the payload ends just before `0x03`.
- **A reading with the wrong number of digits** — the payload is space padded,
  so split fields and take the numeric one rather than slicing by width.

## 8. Next steps

The capture files under `examples/` are the fixture set for this pipeline:
`balance_frames.txt` for the fixed-width weighing format and
`pump_response.txt` for the `;`-separated pump status format. When you add a new
instrument, add a capture in the same hex form and work through steps 2–5 before
touching your acquisition script. `docs/structure.md` describes which module owns
which of those steps.
