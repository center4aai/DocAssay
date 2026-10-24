# parcelroute

A small parcel routing library with a CLI, a tiny HTTP route table, and a TOML-file shipment store.

The current project version is 0.3.1.

## What the library does

The parcelroute package models a parcel, plans a delivery route for it, stores
parcels in a TOML file, and exposes the whole thing through a command line
interface and a small HTTP route table.

- `parcelroute.models.Parcel` is the core record for one shipment.
- `parcelroute.models.RoutePlan` is the record for the planned hops of a parcel.
- `parcelroute.models.load_parcel()` returns a `Parcel()` built from stored fields.
- `parcelroute.store.ShipmentStore` is the TOML-backed shipment store, and
  `parcelroute.store.read_store()` returns a `ShipmentStore()` for the configured store path.
- `parcelroute.routing.plan_route()` returns a `RoutePlan()` for a parcel and its destination code.
- `parcelroute.api.build_router` assembles the HTTP route table, with
  `parcelroute.api.list_parcels_endpoint` handling the parcel listing route.
- `parcelroute.cli.main` is the CLI entry point and `parcelroute.cli.serve` starts the HTTP server.

## Installation

Runtime dependencies:

| Dependency | Constraint |
| --- | --- |
| `pydantic` | `>=2.6` |
| `click` | `>=8.1` |
| `tomlkit` | `>=0.12` |
| `uvicorn` | `>=0.29` |

The `pydantic` (`>=2.6`), `click` (`>=8.1`), `tomlkit` (`>=0.12`) and
`uvicorn` (`>=0.29`) packages cover data validation, the command line interface,
TOML reading, and serving the route table. `uvicorn` supplies the `uvicorn.run`
entry point that serves the HTTP route table.

Python 3.11 and newer are supported.

## Quick start

Serve the HTTP route table:

```bash
python -m parcelroute serve --port 8080
```

Run the test suite:

```bash
pytest -q
```

## Example shipment store

`examples/shipments.toml` holds two example parcels with the `parcel_id`,
`destination_code`, `weight_grams` and `created_at` fields that
`parcelroute.models.Parcel` carries:

```toml
[parcel.parcel_1001]
parcel_id = "parcel_1001"
destination_code = "NL-AMS"
weight_grams = 420
created_at = "2026-01-04T09:15:00Z"
```

The same file holds a second parcel, `parcel_1002`, routed to `DE-BER`.

## Documentation map

- `docs/configuration.md` covers the environment variables and the store layout.
- `docs/api.md` covers the endpoints, the schema fields and the enum members.
