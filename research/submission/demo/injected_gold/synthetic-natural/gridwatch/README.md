# gridwatch

`gridwatch` parses smart-meter interval readings from CSV or JSON files and
computes electricity costs under a time-of-use tariff. It is intended for
people who receive interval data from a meter and want to estimate what the
consumption costs under peak and off-peak rates.

Version: 0.3.0 (requires Python 3.11 or newer).

## Installation

From a checkout of this repository:

```bash
pip install .
```

Runtime dependencies, as declared in `pyproject.toml`:

- `PyYAML>=6.0`
- `click>=8.1`

## Quick start

The repository ships two sample files under `data/`:

- `data/meter_jan.csv`: three hourly readings for meter `M-1042` on
  2026-01-05.
- `data/tariff.yaml`: a tariff with a peak rate of 0.32, an off-peak rate of
  0.11, and a peak window from hour 17 to hour 21.

```python
from gridwatch.readers import read_csv
from gridwatch.tariff import load_tariff
from gridwatch.costing import compute_cost

readings = read_csv()
tariff = load_tariff()
total = compute_cost()
```

The functions above are the public entry points. In the current source they
are declared without parameters and their bodies are placeholders that return
`None`, so the example shows the call shape rather than a working result. See
the [API reference](docs/api.md) for the declared names and return types.

The project metadata also lists the command `gridwatch cost data/meter_jan.csv
--tariff data/tariff.yaml`. The `main` function in `gridwatch/cli.py` exists,
but no console script is declared in `pyproject.toml`, so this command is not
installed by the package as it stands.

## Documentation

- [User guide](docs/guide.md): input file formats, tariff fields, and how the
  pieces fit together.
- [API reference](docs/api.md): modules, classes, functions, and the
  `ROUNDING_DECIMALS` constant.
