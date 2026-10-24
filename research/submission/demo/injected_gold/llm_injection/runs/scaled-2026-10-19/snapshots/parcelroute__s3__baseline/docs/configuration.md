# Configuration

The parcelroute package reads its configuration from environment variables, and
it keeps shipments in a TOML file on disk.

## Environment variables

| Key | Purpose |
| --- | --- |
| `PARCELROUTE_HOME` | Base directory for the parcelroute working files. |
| `PARCELROUTE_LOG_LEVEL` | Log level used by the CLI and the HTTP route table. |
| `PARCELROUTE_STORE_PATH` | Path of the TOML shipment store that `parcelroute.store.read_store()` reads. |
| `PARCELROUTE_MAX_HOPS` | Upper bound on the number of hops that `parcelroute.routing.plan_route()` places in a route plan. |

Each key is read from the process environment at store and route table startup.

## Store layout

`parcelroute.store.ShipmentStore` wraps the TOML shipment store, and each stored
parcel is grouped under a table named after its parcel identifier, with the
fields that `parcelroute.models.Parcel` carries.

`examples/shipments.toml` is the example store that ships with the project:

```toml
# Example shipment store used by the parcelroute docs.

[parcel.parcel_1001]
parcel_id = "parcel_1001"
destination_code = "NL-AMS"
weight_grams = 420
created_at = "2026-01-04T09:15:00Z"

[parcel.parcel_1002]
parcel_id = "parcel_1002"
destination_code = "DE-BER"
weight_grams = 1350
created_at = "2026-01-05T14:02:00Z"
```

Point `PARCELROUTE_STORE_PATH` at `examples/shipments.toml` to exercise the store
with the example data.

## Loading a store

`parcelroute.store.read_store()` returns a `ShipmentStore()` bound to the
configured store path. The returned object exposes the store path, the parcel
listing, and the parcel save operation, so the CLI and the route table work with
one shared handle per process.

`parcelroute.models.load_parcel()` returns a `Parcel()` for a single store entry,
with `parcel_id`, `destination_code`, `weight_grams` and `created_at` filled in.

## Route planning limits

`PARCELROUTE_MAX_HOPS` caps the hop list that `parcelroute.routing.plan_route()`
places in the `RoutePlan()` it returns. `parcelroute.models.RoutePlan` records
the `parcel_id`, the hop codes and the total grams for a planned parcel.

## Store schema

| Field | Meaning |
| --- | --- |
| `parcel_id` | Identifier of the parcel, matching the parcel table name in the store. |
| `destination_code` | Destination code of the parcel, for example `NL-AMS`. |
| `weight_grams` | Parcel weight in grams. |
| `created_at` | Creation timestamp of the parcel record in UTC. |

The schema fields line up with the store entries in `examples/shipments.toml`
and with the attributes of `parcelroute.models.Parcel`.
