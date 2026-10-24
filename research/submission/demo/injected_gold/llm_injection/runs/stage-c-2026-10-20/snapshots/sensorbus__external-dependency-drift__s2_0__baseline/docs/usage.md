# Usage

This guide assumes you have read the README and know what a `Reading`, a
`CalibrationCurve`, and a `Bus` are. It walks through one concrete situation:
you already have the `nitrate-01` channel working, and now a second nitrate
probe is going on the bench. It reports in a different unit, it needs its own
calibration, and both channels have to come back from a collection pass as one
coherent set of numbers.

A note before the steps: in 0.4.1 the pieces that do arithmetic are still
placeholders. `collect`, `convert`, `canonical_unit`, `fit_curve`,
`parse_line`, and `list_devices` are declared but return `None`, and
`REGISTRY`, `DEFAULT_ORDER`, and `DEFAULT_WINDOW` hold placeholder strings. The
data classes work normally. So the procedure below is the sequence of objects
you assemble, and where a step would call into the pipeline it says what that
call is expected to produce.

## 1. Find and describe the port

`SerialDevice` is a plain record of where to read from. Set the fields yourself
if you already know the port name from your OS, or call `list_devices`, which is
declared to return a `list[str]` of the serial ports the host presents.

```python
from sensorbus.devices import SerialDevice, list_devices

print(list_devices())          # currently returns None; see the status note

second = SerialDevice()
second.name = "nitrate-02"
second.port = "/dev/ttyUSB1"
second.baudrate = 9600
```

Use the `name` you want to see in the data, not necessarily the one the OS
assigned: `name` is what ties a device to a sensor id in the rest of the
pipeline.

## 2. Give the new channel its own curve

The new probe does not share `nitrate-01`'s calibration, even though both
measure the same analyte. `fit_curve` takes calibration points and returns a
`CalibrationCurve`; `DEFAULT_ORDER` is the module-level setting for the order
used when you do not choose one. The points come from the same three-column
layout as `examples/curve_nitrate.csv` — `sensor_id`, `reference`, `observed` —
with the probe's own sheet supplying the values and its own id in the first
column.

```python
import csv
from sensorbus.calibration import CalibrationCurve, DEFAULT_ORDER, fit_curve

points = []
with open("examples/curve_nitrate.csv", newline="") as handle:
    for row in csv.DictReader(handle):
        points.append(row)
# in practice the file would be the second probe's own sheet; the columns are
# the same either way

# The intended call: fit_curve(points) -> CalibrationCurve
curve = fit_curve()
if curve is None:
    # 0.4.1 fallback: build the record by hand so downstream code has a shape
    # to work with.
    curve = CalibrationCurve()
    curve.sensor_id = "nitrate-02"
    curve.reference_unit = "mg/L"
    curve.coefficients = [0.03, 0.998]

first_curve = CalibrationCurve()
first_curve.sensor_id = "nitrate-01"
first_curve.reference_unit = "mg/L"
first_curve.coefficients = [0.03, 0.998]

print(DEFAULT_ORDER)  # placeholder string in 0.4.1
```

Two things are worth getting right here even while the fit is unimplemented:

- **`reference_unit` is part of the curve, not of the reading.** The curve
  converts "what this probe said" into "the reference scale", and that scale has
  a unit. Record it once on the curve instead of repeating it at every call
  site.
- **`sensor_id` on the curve must match the readings' `sensor_id`.** That
  string is the only link between a batch of numbers and the correction that
  applies to it.

## 3. Register the curve on the bus

`Bus` exists to hold the things a collection pass needs, so you give it a
dictionary of curves keyed by sensor id rather than passing a curve to each
call.

```python
from sensorbus.bus import Bus, DEFAULT_WINDOW

bus = Bus()
bus.registry = None            # starts as None; set it to the registry to use
bus.curves = {"nitrate-01": first_curve, "nitrate-02": curve}
bus.window = DEFAULT_WINDOW    # or your own window
```

`window` is a property of the collection pass, not of a sensor: it answers "how
much time does one `collect` call cover". Setting it on the bus keeps every
channel on the same sampling horizon, which matters as soon as you want to
compare two channels or average them together.

## 4. Collect and get one batch back

```python
from sensorbus.bus import collect

batch = collect()   # intended: a ReadingBatch covering one channel
```

`collect` is declared to return a `ReadingBatch`, and a batch belongs to exactly
one channel — it has a single `sensor_id` and a list of `readings`. Collecting
two channels therefore means two batches, which is deliberate: it keeps the
`sensor_id` on the batch from being a lie, and lets you hand a single channel's
data to a consumer that knows nothing about the rest of the bench.

If you are assembling the batch yourself while the pipeline is incomplete, fill
in both fields:

```python
from sensorbus.readings import Reading, ReadingBatch

raw = Reading()
raw.sensor_id = "nitrate-02"
raw.value = 5.08
raw.unit = "mg/L"
raw.timestamp = "2026-10-20T09:14:03"

batch = ReadingBatch()
batch.sensor_id = "nitrate-02"
batch.readings = [raw]
```

## 5. Reconcile the units before anything downstream sees them

This is the step that the second probe makes unavoidable. Two channels that
report the same analyte in different units cannot be compared, averaged, or
plotted on one axis until they agree.

`canonical_unit` is declared to return the `str` name of the unit a quantity
should be stored in; `convert` takes a value in one unit and returns a `float`
in another, using `REGISTRY` to resolve the names. The pattern is:

```python
from sensorbus.units import REGISTRY, canonical_unit, convert

target = canonical_unit()   # intended: the unit to normalise onto
print(target)               # None in 0.4.1
print(REGISTRY)             # placeholder string in 0.4.1

value = convert()            # intended: convert(value, from_unit, to_unit)
```

Whatever you do in the meantime, keep the original unit on the `Reading`
(`raw.unit`) and do the conversion at the boundary where the value leaves the
pipeline. Overwriting `Reading.unit` with the converted unit while leaving the
old number in `Reading.value` is the one mistake that reliably costs an
afternoon later.

## A checklist for the next channel

Adding a third probe follows the same five steps, and each step has exactly one
place it can go wrong:

| Step | What to set | What to check |
| --- | --- | --- |
| Port | `SerialDevice.port`, `.baudrate`, `.name` | `name` matches the id used everywhere else |
| Curve | `CalibrationCurve.sensor_id`, `.coefficients`, `.reference_unit` | `sensor_id` matches the readings, `reference_unit` is the scale the coefficients produce |
| Bus | `Bus.curves[sensor_id]`, `Bus.window` | every channel on the bus has a curve; the window is the one you meant |
| Batch | `ReadingBatch.sensor_id`, `.readings` | one batch per channel |
| Units | `canonical_unit`, `convert` | every reading carries the unit it was actually measured in |
