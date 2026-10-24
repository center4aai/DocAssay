# gridwatch user guide

This guide describes the input files `gridwatch` works with and how the
package is organized. For the function and class listing, see the
[API reference](api.md).

## Input data

### Interval readings (CSV)

Meter readings are read from CSV files with the header:

```
meter_id,timestamp,kwh
```

Each row is one interval reading:

| Column      | Meaning                                  |
|-------------|------------------------------------------|
| `meter_id`  | Identifier of the meter, for example `M-1042`. |
| `timestamp` | Start of the interval, ISO 8601 (for example `2026-01-05T16:00:00`). |
| `kwh`       | Energy consumed during the interval, in kilowatt-hours. |

Example, from `data/meter_jan.csv`:

```
meter_id,timestamp,kwh
M-1042,2026-01-05T16:00:00,0.82
M-1042,2026-01-05T17:00:00,1.14
M-1042,2026-01-05T18:00:00,0.97
```

### Interval readings (JSON)

`gridwatch.readers.read_json` is declared to read readings from JSON. The
source does not yet define the JSON layout, so this guide does not document
one.

### Tariff (YAML)

A time-of-use tariff is a YAML mapping with four keys:

| Key               | Meaning                                    |
|-------------------|--------------------------------------------|
| `peak_rate`       | Rate applied during peak hours.            |
| `offpeak_rate`    | Rate applied outside peak hours.           |
| `peak_start_hour` | Hour of day at which the peak window starts. |
| `peak_end_hour`   | Hour of day at which the peak window ends.   |

Example, from `data/tariff.yaml`:

```yaml
peak_rate: 0.32
offpeak_rate: 0.11
peak_start_hour: 17
peak_end_hour: 21
```

The rates are per kilowatt-hour. The file is read with PyYAML, which is why it
is a runtime dependency.

## Package layout

| Module                | Contents                                                |
|-----------------------|---------------------------------------------------------|
| `gridwatch/models.py` | `Reading`, the record for one interval reading.         |
| `gridwatch/readers.py`| `read_csv` and `read_json`, which produce lists of `Reading`. |
| `gridwatch/tariff.py` | `Tariff`, the tariff settings, and `load_tariff`.       |
| `gridwatch/costing.py`| `compute_cost` and the `ROUNDING_DECIMALS` constant.    |
| `gridwatch/cli.py`    | `main`, the command-line entry function.                |

A typical flow is: read readings with a reader, load a tariff, and pass both to
the costing function. The current source declares these steps but does not
connect them, so the flow is a plan for the API rather than working behavior.

## Command line

The `main` function in `gridwatch/cli.py` is declared to return an `int`.
The package metadata lists the command `gridwatch cost <readings file>
--tariff <tariff file>`, but no console script is registered in
`pyproject.toml`. To run `main` today, call it from Python:

```python
from gridwatch.cli import main

exit_code = main()
```
