# gaugekit guide

This guide covers the CSV layout gaugekit expects, how the package is organized, and how the pieces fit together. For signatures and return types, see the [API reference](api.md).

## Package layout

| Module | Contents |
| --- | --- |
| `gaugekit.models` | `Reading` and `GaugeSeries` data containers. |
| `gaugekit.loader` | `load_csv` and `read_station_id` for reading CSV exports. |
| `gaugekit.stats` | `summarize` and `monthly_means` summary statistics. |
| `gaugekit.units` | `CFS_PER_CMS` constant and the `cfs_to_cms` conversion. |
| `gaugekit.errors` | `GaugeFormatError`, the error type for malformed input. |

The top-level `gaugekit` package only defines `__version__`. Import from the submodules directly.

## CSV format

The loader works with CSV exports that have a header row and the following four columns:

| Column | Meaning |
| --- | --- |
| `station_id` | Gauge station identifier, for example `01646500`. |
| `timestamp` | Reading time in ISO 8601 form, for example `2026-01-01T00:00:00`. |
| `discharge_cfs` | Discharge in cubic feet per second. |
| `gauge_height_ft` | Gauge height in feet. |

The bundled example, `examples/sample_gauge.csv`, looks like this:

```csv
station_id,timestamp,discharge_cfs,gauge_height_ft
01646500,2026-01-01T00:00:00,412.0,3.41
01646500,2026-01-01T01:00:00,405.5,3.38
01646500,2026-02-01T00:00:00,530.2,3.92
01646500,2026-02-01T01:00:00,548.9,3.99
```

Discharge is given in cfs; `gaugekit.units` provides `cfs_to_cms` for converting to cubic metres per second.

## Data containers

- `Reading` holds one observation with the attributes `timestamp`, `discharge_cfs`, and `gauge_height_ft`.
- `GaugeSeries` holds one station's data with the attributes `station_id` and `readings`.

`load_csv` is declared to return a `GaugeSeries`, and `summarize` and `monthly_means` are declared to return `dict[str, float]`.

## Errors

Malformed input is reported with `GaugeFormatError`, which carries `line_number` and `message` attributes.

## Typical workflow

1. Read a file with `load_csv` to get a `GaugeSeries`.
2. Use `read_station_id` when you only need the station identifier.
3. Pass the series to `summarize` for overall statistics, or to `monthly_means` for monthly values.
4. Convert discharge with `cfs_to_cms` when metric units are needed.

As noted in the [README](../README.md), the function bodies in this release are placeholders, so this workflow describes the intended usage rather than working output.
