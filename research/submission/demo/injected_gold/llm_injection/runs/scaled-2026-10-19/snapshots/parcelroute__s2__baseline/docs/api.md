# API reference

The parcelroute package exposes a small HTTP route table plus the functions that
build and serve it. The route table is assembled by `parcelroute.api.build_router`.

## Endpoints

| Endpoint | Handler | Purpose |
| --- | --- | --- |
| `/v1/parcels` | `parcelroute.api.list_parcels_endpoint` | Lists the parcels held in the shipment store. |
| `/v1/plans` | `parcelroute.routing.plan_route` | Returns a route plan for a parcel and destination code. |
| `/v1/health` | `parcelroute.api.build_router` | Reports the health of the running route table. |

## Data model

`parcelroute.models.Parcel` carries the schema fields of one shipment.

| Field | Type | Meaning |
| --- | --- | --- |
| `parcel_id` | string | Identifier of the parcel. |
| `destination_code` | string | Destination code of the parcel, for example `NL-AMS`. |
| `weight_grams` | integer | Parcel weight in grams. |
| `created_at` | string | Creation timestamp in UTC. |

`parcelroute.models.RoutePlan` carries the `parcel_id`, the hop codes and the
total grams of a planned route.

## Functions

| Function | Returns | Purpose |
| --- | --- | --- |
| `parcelroute.models.load_parcel()` | `Parcel()` | Builds one parcel record from the store. |
| `parcelroute.store.read_store()` | `ShipmentStore()` | Opens the configured TOML shipment store. |
| `parcelroute.routing.plan_route()` | `RoutePlan()` | Plans the hops for a parcel. |
| `parcelroute.api.build_router()` | A router object | Assembles the HTTP route table. |
| `parcelroute.api.list_parcels_endpoint()` | A payload of parcels | Answers the parcel listing route. |
| `parcelroute.cli.main()` | A process exit status | Runs the command line interface. |
| `parcelroute.cli.serve()` | A running server | Serves the HTTP route table. |

`parcelroute.models.load_parcel()` returns a `Parcel()` with `parcel_id`,
`destination_code`, `weight_grams` and `created_at` populated from the store.
`parcelroute.store.read_store()` returns a `ShipmentStore()`, and
`parcelroute.routing.plan_route()` returns a `RoutePlan()` for the requested
parcel and destination code.

## Status values

The routing module behind `parcelroute.routing.plan_route()` defines the parcel
status values used across the store and the route table.

| Enum member | Meaning |
| --- | --- |
| `PARCEL_STATUS_PENDING` | The parcel is recorded and awaits routing. |
| `PARCEL_STATUS_IN_TRANSIT` | The parcel is moving along its planned hops. |
| `PARCEL_STATUS_DELIVERED` | The parcel reached its destination code. |

## Example data flow

The route table reads from the TOML shipment store, so a request to `/v1/parcels`
returns the parcels in `examples/shipments.toml`, each one shaped like
`parcelroute.models.Parcel`:

- `parcel_1001` travels to `NL-AMS` with 420 grams.
- `parcel_1002` travels to `DE-BER` with 1350 grams.
