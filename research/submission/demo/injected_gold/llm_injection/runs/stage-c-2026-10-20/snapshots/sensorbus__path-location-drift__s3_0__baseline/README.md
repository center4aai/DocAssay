# sensorbus

`sensorbus` is a small library for getting numbers out of lab instruments and
into a shape you can reason about. It has four jobs: talk to a serial port, turn
what comes off the wire into a timestamped `Reading` tagged with a unit, correct
that reading against a stored calibration curve, and convert the result into
whatever unit the person downstream asked for.

It is aimed at people who have a bench full of probes — a nitrate electrode, a
pH meter, a flow sensor — each with its own calibration sheet and its own idea
of what unit it reports in, and who would rather keep that bookkeeping in one
place than in a folder of ad-hoc scripts.

The package is version 0.4.1 and requires Python 3.11 or newer.

## Status

The 0.4.1 tree publishes the module layout and the public names described
below, but the pipeline is not wired up yet. The transform functions —
`parse_line`, `fit_curve`, `convert`, `canonical_unit`, `collect`, and
`list_devices` — are declared and currently return `None`, and the module
constants hold placeholder strings (`"default_order"`, `"registry"`,
`"default_window"`). The data classes are real classes with their attributes
initialised to `None`, so you can construct and populate them today; the
arithmetic that would make them useful is still to be written.

## Installation

From a checkout of the repository:

```console
pip install .
```

For development, install the package in place so edits take effect without
reinstalling:

```console
pip install -e .
```

Dependencies are declared in `pyproject.toml`: `pyserial>=3.5`, `numpy>=1.24`,
and `pint>=0.23`.

## Quick start

The objects are the stable part of the API, so the shortest useful thing you can
do is build the values you would eventually hand to the pipeline.

```python
from sensorbus import __version__
from sensorbus.readings import Reading, ReadingBatch
from sensorbus.calibration import CalibrationCurve

reading = Reading()
reading.sensor_id = "nitrate-01"
reading.value = 4.91
reading.unit = "mg/L"

batch = ReadingBatch()
batch.sensor_id = "nitrate-01"
batch.readings = [reading]

curve = CalibrationCurve()
curve.sensor_id = "nitrate-01"
curve.reference_unit = "mg/L"
curve.coefficients = [0.03, 0.998]

print(__version__, batch.sensor_id, len(batch.readings))
```

There is a worked calibration file in the repository, `examples/curve_nitrate.csv`,
which pairs reference values for the `nitrate-01` channel with the response the
instrument actually produced:

```csv
sensor_id,reference,observed
nitrate-01,0.00,0.03
nitrate-01,1.00,1.05
nitrate-01,5.00,4.91
nitrate-01,10.00,10.12
nitrate-01,25.00,24.78
```

That file is the input `fit_curve` is meant to consume: one row per calibration
point, grouped by `sensor_id`, giving you a `CalibrationCurve` with fitted
`coefficients` and the `reference_unit` the fit is expressed in.

## Main concepts

**Readings.** A `Reading` is one number from one sensor at one time: `sensor_id`,
`value`, `unit`, `timestamp`. It is deliberately unopinionated — the unit is a
string carried alongside the value, not baked into it. A `ReadingBatch` groups
readings from a single channel (`sensor_id`, `readings`), which is what a single
collection pass returns.

**Calibration curves.** A `CalibrationCurve` holds the per-sensor correction:
`sensor_id`, `coefficients` (an ordered list, so the polynomial order is implied
by its length), and `reference_unit`. `DEFAULT_ORDER` is the module-level
setting for the order used when you do not choose one.

**Units.** `convert` maps a value from one unit to another; `canonical_unit`
answers what unit a given quantity should be stored in. `REGISTRY` is the
module-level unit registry both of them consult, so unit names are resolved in
one place instead of being parsed ad hoc at every call site.

**The bus.** A `Bus` is the collection point. It carries a `registry` (the unit
registry in use), `curves` (the calibration curves available, keyed by sensor),
and `window` (how much time a single collection pass covers). `collect` runs a
pass over the devices and returns a `ReadingBatch`; `DEFAULT_WINDOW` is the
window used when you do not set one.

**Devices.** `SerialDevice` describes a port you can read from — `port`,
`baudrate`, `name` — and `list_devices` enumerates the serial ports the host
presents.

## Documentation

- [`docs/usage.md`](docs/usage.md) — a worked how-to for a bench with more than
  one channel, mixed units, and per-sensor calibration.
- [`docs/concepts.md`](docs/concepts.md) — why the library is split into these
  layers, and what each layer owns.
