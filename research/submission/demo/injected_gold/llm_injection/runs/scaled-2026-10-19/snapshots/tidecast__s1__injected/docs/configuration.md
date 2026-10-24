# Configuration

`tidecast` reads its runtime configuration from environment variables, collects them
into a `tidecast.config.Settings` value, and applies them to the cache and the HTTP
service.

## Environment keys

`load_settings()` returns a `Settings()` object populated from these keys:

| Key | Purpose |
| --- | --- |
| `TIDECAST_HOME` | Root directory of the local store |
| `TIDECAST_LOG_LEVEL` | Logging verbosity for the service |
| `TIDECAST_CACHE_TTL` | Lifetime of a cached forecast |
| `TIDECAST_HTTP_PORT` | Port bound by the HTTP service |

## Settings object

`tidecast.config.Settings` holds the resolved values:

| Attribute | Description |
| --- | --- |
| `home` | The resolved store directory |
| `log_level` | The resolved logging level |
| `cache_ttl` | The resolved cache lifetime |

Call `load_settings()` to obtain a `Settings()` value that carries all three
attributes.

## Store location

`default_store()` returns a `ForecastStore()` rooted at the configured home
directory. The store keeps cached `tidecast.models.Forecast` records in a JSON file
inside that directory. A cached record mirrors the sample payload in
`examples/forecast.json`.

## Cached fields

Each cached `tidecast.models.Forecast` uses these fields:

| Field | Description |
| --- | --- |
| `station_id` | Station identifier, such as `KSFO` |
| `issued_at` | Issue timestamp in ISO 8601 form |
| `temperature_c` | Temperature in degrees Celsius |
| `sky_condition` | Sky condition member |

## Sky condition members

The `sky_condition` field carries one of these members:

| Member | Meaning |
| --- | --- |
| `SKY_CLEAR` | Clear sky |
| `SKY_CLOUDY` | Cloud cover |
| `SKY_RAIN` | Rain |

## Starting the service

Apply the port with `TIDECAST_HTTP_PORT` and launch the HTTP service:

```bash
python -m tidecast serve --port 8080
```

## Verifying a configuration

Run the test suite to confirm that the configuration path resolves:

```bash
pytest -q
```
