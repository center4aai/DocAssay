# API reference

All public names live in submodules of `gaugekit`. The top-level package exposes only `__version__` (`"0.4.2"`).

In this release the functions and class constructors are declared with the signatures shown below but take no parameters and their bodies return `None`. Parameters are therefore not yet documented here.

## `gaugekit.models`

### `Reading`

A single observation. Instances carry these attributes:

| Attribute | Description |
| --- | --- |
| `timestamp` | Reading time. |
| `discharge_cfs` | Discharge in cubic feet per second. |
| `gauge_height_ft` | Gauge height in feet. |

### `GaugeSeries`

A station's data. Instances carry these attributes:

| Attribute | Description |
| --- | --- |
| `station_id` | Gauge station identifier. |
| `readings` | The collection of readings for the station. |

## `gaugekit.loader`

### `load_csv() -> GaugeSeries`

Loads a CSV export into a `GaugeSeries`. The expected columns are described in the [guide](guide.md#csv-format).

### `read_station_id() -> str`

Returns the station identifier from a CSV export as a string.

## `gaugekit.stats`

### `summarize() -> dict[str, float]`

Computes summary statistics for a series, keyed by statistic name.

### `monthly_means() -> dict[str, float]`

Computes monthly mean values for a series, returned as a dictionary of floats.

## `gaugekit.units`

### `CFS_PER_CMS`

Module-level constant with the value `"cfs_per_cms"`. It is a string label and is not a numeric conversion factor.

### `cfs_to_cms() -> float`

Converts a discharge from cubic feet per second to cubic metres per second. Declared to return a `float`.

## `gaugekit.errors`

### `GaugeFormatError`

Error for malformed input. Instances carry:

| Attribute | Description |
| --- | --- |
| `line_number` | Line in the input where the problem was found. |
| `message` | Description of the problem. |

In the current source, `GaugeFormatError` is defined as a plain class and does not subclass `Exception`.
