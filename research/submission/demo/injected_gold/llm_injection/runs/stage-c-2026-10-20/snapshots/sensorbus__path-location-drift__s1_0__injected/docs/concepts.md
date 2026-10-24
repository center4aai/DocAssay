# Concepts

This document explains how `sensorbus` is put together and why it is split the
way it is. It is about the design, not about calling the API; if you want the
procedure, read [`usage.md`](usage.md).

The library has five modules, and they form a pipeline in one direction:

```
devices.py     ->  readings.py  ->  calibration.py  ->  units.py
 (a port)           (a number)       (a correction)      (a name for it)

                        bus.py
              (holds registry + curves + window,
               runs one pass, returns a batch)
```

`bus.py` is the odd one out: it does not add a new data type so much as hold the
other four together for the length of a collection pass. In 0.4.1 the modules
publish their names and data shapes but the functions that would move data
between them are stubs — `parse_line`, `fit_curve`, `convert`, `canonical_unit`,
`collect`, and `list_devices` all return `None`. The layering described here is
the structure those functions are meant to fill in.

## Why a reading is a value plus a unit, not a quantity

`Reading` has four attributes: `sensor_id`, `value`, `unit`, `timestamp`. There
is no arithmetic on a `Reading` and no normalisation inside it. The unit is
carried as a string next to the number.

That is a deliberate refusal to guess. An instrument hands you a number in
whatever unit its firmware was configured for, and that configuration changes
between probes and sometimes between firmware versions. If `Reading` tried to be
a physically meaningful quantity, it would have to decide *when* the unit is
known, and the only moment it is reliably known is at the wire. So the rule is:
`Reading.unit` is whatever the device said, and conversion happens later, at a
boundary, exactly once.

`ReadingBatch` follows from the same reasoning. It has `sensor_id` and
`readings`, and only one `sensor_id` — a batch is a single channel's worth of
data. It would be convenient to return everything from a pass in one object, but
then the batch-level `sensor_id` could only be one of several values, and every
consumer would have to re-group. One batch per channel keeps that field honest
and makes a consumer that only knows about one probe trivially possible.

## Why calibration is a stored object rather than a function argument

`CalibrationCurve` carries `sensor_id`, `coefficients`, and `reference_unit`.
The point of making it an object is that a curve is a *fact about a sensor* that
outlives any single collection pass. You fit it when the probe is installed,
store it, and reuse it until the next calibration event.

`coefficients` is an ordered list, so the order of the polynomial is implicit in
its length; `DEFAULT_ORDER` names the order used when nobody asks for a specific
one. `fit_curve` is the constructor for the whole object: it takes calibration
points and produces a curve. The example file in the repository,
`examples/curve_nitrate.csv`, shows the shape of those points — `sensor_id`,
`reference`, `observed`, five rows for `nitrate-01`. `reference` is the value the
sensor *should* have read; `observed` is what it did read. Fitting those pairs
against each other is what makes a correction possible at all.

`reference_unit` deserves its own note. A curve maps raw response onto a
reference scale, and that scale has a unit. Putting it on the curve rather than
on the reading means the unit travels with the coefficients that produce it, so
the two can never drift apart.

The obvious alternative — pass coefficients into every conversion call — is what
this design is avoiding. It works fine for one probe and becomes unmanageable at
five, because the mapping from sensor to coefficients ends up duplicated in
every call site.

## Why there is a registry, and why units are converted in one place

`units.py` exposes `convert`, `canonical_unit`, and `REGISTRY`. The registry is
the single authority on what unit names mean; `convert` turns a value in one
unit into a `float` in another; `canonical_unit` answers what unit a quantity
should be stored in.

Two separate problems are being solved here. The first is mechanical: converting
between units is arithmetic you should not reimplement, and the dependency on
`pint` exists precisely so that it is not reimplemented. The second is social: on
a bench, "the" unit for a measurement is a convention, not a fact. One lab
reports nitrate in `mg/L`, another in `µmol/L`, and both are correct. Having a
named canonical unit gives the convention a place to live, so that a batch can be
normalised on the way out without every downstream script inventing its own
answer.

The distinction between the two functions matters. `convert` is per-value and
lossless in intent; `canonical_unit` is a policy decision. Keeping the policy in
one function means changing lab conventions is a one-line change rather than a
search across the codebase.

## Why the bus holds a window

`Bus` has exactly three attributes: `registry`, `curves`, `window`. Two of them
are collections of things already described — the unit registry in use, and the
curves keyed by sensor. `window` is different: it describes the *pass*, not the
data. `DEFAULT_WINDOW` is the value used when you do not choose one.

A collection pass needs a notion of scope. Without one, "collect" is ambiguous:
does it return what is buffered right now, or everything since the last call? The
window is the answer, and holding it on the bus rather than passing it to
`collect` keeps every channel on the same horizon. That is what makes two
channels comparable — a window set per sensor would produce batches that cover
different spans and quietly cannot be plotted on one axis.

`collect` returns a `ReadingBatch`. It is the only function in the pipeline that
touches every layer: it needs a device to read from, `parse_line` to make
readings, the curve for that `sensor_id` to correct them, and the registry to
express the result.

## Why the device layer is so thin

`SerialDevice` is three attributes — `port`, `baudrate`, `name` — and
`list_devices` is declared to return a `list[str]`. Nothing here tries to
abstract over transport types.

That is on purpose. The interesting work in this library happens after bytes have
become numbers, and a device abstraction deep enough to cover every instrument
would be a project of its own. Keeping the device layer to "which port, at what
speed, under what name" means the rest of the pipeline can be tested by
constructing `Reading` objects directly, with no hardware and no serial port.

`name` is the one field that is not about the transport. It is the identity the
device is known by downstream, which is why it is the field that has to agree
with `Reading.sensor_id` and `CalibrationCurve.sensor_id`. The string is the only
join key in the whole design; nothing enforces it at runtime, so it is the first
thing to check when a reading comes back uncorrected.

## Where the boundaries are

Summing up, the design puts each decision in exactly one place:

| Decision | Lives in |
| --- | --- |
| Which port, at what speed | `SerialDevice` |
| What the device said, and in what unit | `Reading` |
| Which readings belong together | `ReadingBatch` |
| How this sensor is off, and against what scale | `CalibrationCurve` |
| What a unit name means, and how to move between them | `REGISTRY`, `convert` |
| Which unit to standardise on | `canonical_unit` |
| How much time a pass covers | `Bus.window`, `DEFAULT_WINDOW` |

When something goes wrong, that table is the shortest route to the module that
owns the problem.
