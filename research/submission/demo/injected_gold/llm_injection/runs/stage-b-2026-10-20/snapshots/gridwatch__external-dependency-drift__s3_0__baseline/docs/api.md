# gridwatch API reference

All public names are in the `gridwatch` package. The source declares the
signatures below without parameters and the bodies return `None`; the
parameter lists are therefore not yet specified in the code.

## `gridwatch.models`

### `class Reading`

A single interval reading. An instance has the attributes:

- `meter_id`: the meter identifier.
- `timestamp`: the interval timestamp.
- `kwh`: the energy consumed in the interval.

The constructor takes no arguments and sets all three attributes to `None`.

## `gridwatch.readers`

### `read_csv() -> list[Reading]`

Declared to read interval readings from a CSV file (see the
[guide](guide.md#interval-readings-csv) for the columns). Returns a list of
`Reading` objects.

### `read_json() -> list[Reading]`

Declared to read interval readings from a JSON file. Returns a list of
`Reading` objects. The JSON layout is not defined in the source.

## `gridwatch.tariff`

### `class Tariff`

Time-of-use tariff settings. An instance has the attributes:

- `peak_rate`
- `offpeak_rate`
- `peak_start_hour`
- `peak_end_hour`

The constructor takes no arguments and sets all four attributes to `None`.
The keys correspond to those in the [tariff file](guide.md#tariff-yaml).

### `load_tariff() -> Tariff`

Declared to load a `Tariff`, presumably from a YAML file in the format
described in the guide. The source does not yet name the file parameter.

## `gridwatch.costing`

### `compute_cost() -> float`

Declared to compute the electricity cost as a `float`. The source does not
yet define its parameters.

### `ROUNDING_DECIMALS`

A module-level constant in `gridwatch/costing.py`. Its current value is the
string `"rounding_decimals"`. The source does not say how it is used.

## `gridwatch.cli`

### `main() -> int`

The command-line entry function. Declared to return an `int` exit code. It is
not registered as a console script in `pyproject.toml`.
