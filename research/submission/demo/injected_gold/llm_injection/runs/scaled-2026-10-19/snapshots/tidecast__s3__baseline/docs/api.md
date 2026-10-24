# API reference

This reference describes the public classes and functions of `tidecast`, the HTTP
endpoints it serves, and the shape of a cached forecast record.

## Modules and symbols

| Module | Symbol | Kind |
| --- | --- | --- |
| models | `tidecast.models.Forecast` | class |
| models | `parse_forecast()` | function |
| store | `tidecast.store.ForecastStore` | class |
| store | `default_store()` | function |
| routes | `tidecast.routes.RouteTable` | class |
| routes | `build_routes()` | function |
| config | `tidecast.config.Settings` | class |
| config | `load_settings()` | function |
| cli | `tidecast.cli.main` | function |
| cli | `tidecast.cli.serve` | function |

## Value model

`tidecast.models.Forecast` is the value object for a single cached forecast. Its
fields are:

| Field | Description |
| --- | --- |
| `station_id` | Station identifier |
| `issued_at` | Issue timestamp |
| `temperature_c` | Temperature in degrees Celsius |
| `sky_condition` | Sky condition member |

`parse_forecast()` returns a `Forecast()` built from a stored payload. A payload that
matches `examples/forecast.json` produces a `tidecast.models.Forecast` with the
`station_id` `KSFO`, the `issued_at` `2026-10-12T09:00:00Z`, the `temperature_c` `16.5`,
and the `sky_condition` `SKY_CLOUDY`.

## Sky conditions

The `sky_condition` field of a `tidecast.models.Forecast` is one of:

| Member | Meaning |
| --- | --- |
| `SKY_CLEAR` | Clear sky |
| `SKY_CLOUDY` | Cloud cover |
| `SKY_RAIN` | Rain |

## Cache store

`tidecast.store.ForecastStore` holds the store root together with its load and save
operations. `default_store()` returns a `ForecastStore()` bound to the configured home
directory. Records written by the store use the same fields as
`examples/forecast.json`.

## Routing

`tidecast.routes.RouteTable` collects the served routes and offers an add operation.
`build_routes()` returns a `RouteTable()` populated with the service endpoints.

| Endpoint | Method | Purpose |
| --- | --- | --- |
| `/v1/forecast` | GET | Return the cached forecast record |
| `/v1/stations` | GET | List the known stations |
| `/v1/health` | GET | Report service liveness |

The HTTP layer is provided by the web framework exposed as `flask.Flask`.

## Settings

`load_settings()` returns a `Settings()` object. `tidecast.config.Settings` carries the
`home`, `log_level`, and `cache_ttl` attributes, populated from the `TIDECAST_HOME`,
`TIDECAST_LOG_LEVEL`, `TIDECAST_CACHE_TTL`, and `TIDECAST_HTTP_PORT` environment keys.

## Command line

`tidecast.cli.main` is the top-level dispatcher and `tidecast.cli.serve` starts the HTTP
service. Launch the service with:

```bash
python -m tidecast serve --port 8080
```

Verify the package with:

```bash
pytest -q
```
