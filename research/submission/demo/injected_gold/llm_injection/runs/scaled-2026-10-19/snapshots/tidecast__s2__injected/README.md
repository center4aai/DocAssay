# tidecast

A small local weather-forecast cache that fetches forecasts and serves them from a
JSON-file store.

The current project version is 0.4.1.

## Overview

`tidecast` keeps a local cache of weather forecasts. The cache layer is modeled by
`tidecast.store.ForecastStore`, the value object by `tidecast.models.Forecast`, the
routing table by `tidecast.routes.RouteTable`, and the environment settings by
`tidecast.config.Settings`. A `tidecast.models.Forecast` value carries the station
identifier, the issue time, the temperature in Celsius, and the sky condition. The
sample payload in `examples/forecast.json` shows one complete `tidecast.models.Forecast`
record.

## Requirements

The runtime dependencies are `requests` (`>=2.31`), `flask` (`>=3.0`),
`click` (`>=8.1`), and `platformdirs` (`>=4.2`).

| Dependency | Constraint |
| --- | --- |
| `requests` | `>=2.31` |
| `flask` | `>=3.0` |
| `click` | `>=8.1` |
| `platformdirs` | `>=4.2` |

The HTTP surface is served through the web framework exposed as `flask.Flask`.

## Installation

```bash
pip install -e .
```

## Quick start

```bash
python -m tidecast serve --port 8080
```

Run the test suite with:

```bash
pytest -q
```

## Sample data

`examples/forecast.json` holds a single cached forecast with these fields:

| Field | Example value |
| --- | --- |
| `station_id` | `KSFO` |
| `issued_at` | `2026-10-12T09:00:00Z` |
| `temperature_c` | `16.5` |
| `sky_condition` | `SKY_CLOUDY` |

## HTTP endpoints

The route table built by `build_routes()` exposes these paths:

| Endpoint | Purpose |
| --- | --- |
| `/v1/forecast` | Return the cached forecast record |
| `/v1/stations` | List the known stations |
| `/v1/health` | Report service liveness |

## Sky conditions

The sky condition of a `tidecast.models.Forecast` is one of:

| Member | Meaning |
| --- | --- |
| `SKY_CLEAR` | Clear sky |
| `SKY_CLOUDY` | Cloud cover |
| `SKY_RAIN` | Rain |

## Reading a record

`parse_forecast()` returns a `Forecast()` object built from a stored payload, and
`default_store()` returns a `ForecastStore()` rooted at the configured home
directory. Settings come from `load_settings()`, which returns a `Settings()` value.

## Configuration

The environment keys `TIDECAST_HOME`, `TIDECAST_LOG_LEVEL`, `TIDECAST_CACHE_TTL`, and
`TIDECAST_HTTP_PORT` drive the runtime. See the configuration guide for details.

## Command line

The entry points are `tidecast.cli.main` and `tidecast.cli.serve`. Run
`tidecast.cli.serve` to start the HTTP service, and `tidecast.cli.main` for the
top-level dispatcher.
