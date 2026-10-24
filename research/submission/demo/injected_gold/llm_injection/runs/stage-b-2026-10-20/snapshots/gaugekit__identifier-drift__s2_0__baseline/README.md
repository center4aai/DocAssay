# gaugekit

gaugekit is a small Python library for loading public stream-gauge CSV exports and computing summary statistics for discharge and gauge height. It is aimed at people who work with river gauge data downloaded as CSV and want a few typed building blocks for reading it and summarizing it.

Current version: **0.4.2**. Requires Python 3.11 or newer.

## Installation

gaugekit depends on NumPy (`numpy>=1.24`). From a checkout of the repository:

```bash
pip install .
```

## Quick start

The package exposes its public functions from submodules rather than from the top-level `gaugekit` package:

```python
from gaugekit.loader import load_csv
from gaugekit.stats import summarize, monthly_means
from gaugekit.units import cfs_to_cms

series = load_csv("examples/sample_gauge.csv")
stats = summarize(series)
by_month = monthly_means(series)
```

The repository includes `examples/sample_gauge.csv`, a four-row file in the expected layout (see the [guide](docs/guide.md#csv-format)).

> **Status:** the functions in this release are declared with their signatures and return types, but their bodies are placeholders that return `None`. The quick start shows the intended calling pattern; it will not produce values until the implementations are filled in.

## Documentation

- [Guide](docs/guide.md): data format, module layout, and typical usage.
- [API reference](docs/api.md): every public class, function, and constant.
