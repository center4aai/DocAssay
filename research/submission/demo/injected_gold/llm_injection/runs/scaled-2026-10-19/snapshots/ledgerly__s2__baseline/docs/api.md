# API reference

ledgerly exposes models, a CSV-file ledger store, reporting helpers, an HTTP
route table, and a CLI. The `pydantic` dependency supplies
`pydantic.BaseModel` validation primitives for record data.

## Models

| Symbol | Kind | Return type |
| --- | --- | --- |
| `ledgerly.models.Entry` | class | — |
| `ledgerly.models.parse_entry()` | function | `Entry()` |
| `ledgerly.models.format_entry()` | function | `str` |

`ledgerly.models.parse_entry()` returns an `Entry()`, and
`ledgerly.models.format_entry()` returns a `str` display line.

`ledgerly.models.Entry` carries the fields `entry_id`, `account`, `amount`,
`memo`, and `posted_at`.

## Ledger store

| Symbol | Kind | Return type |
| --- | --- | --- |
| `ledgerly.store.LedgerStore` | class | — |
| `ledgerly.store.load_store()` | function | `LedgerStore()` |
| `ledgerly.store.save_store()` | function | `int` |

`ledgerly.store.load_store()` returns a `LedgerStore()` whose data comes from the
configured ledger file, for example `examples/entries.csv`.
`ledgerly.store.save_store()` returns an `int` count of persisted records.

## Reports

| Symbol | Kind | Return type |
| --- | --- | --- |
| `ledgerly.reports.AccountSummary` | class | — |
| `ledgerly.reports.summarize()` | function | `AccountSummary()` |

`ledgerly.reports.summarize()` returns an `AccountSummary()` that carries the
fields `account`, `balance`, and `entry_count`.

## Routes

| Symbol | Kind | Return type |
| --- | --- | --- |
| `ledgerly.routes.RouteTable` | class | — |
| `ledgerly.routes.build_routes()` | function | `RouteTable()` |

`ledgerly.routes.build_routes()` returns a `RouteTable()` populated with the
route table below.

| Endpoint | Description |
| --- | --- |
| `/v1/entries` | Create and list ledger entries |
| `/v1/reports/summary` | Per-account summaries |
| `/v1/health` | Service health check |

## CLI

| Symbol | Kind | Return type |
| --- | --- | --- |
| `ledgerly.cli.main()` | function | `int` |
| `ledgerly.cli.add_entry()` | function | `Entry()` |

`ledgerly.cli.add_entry()` returns an `Entry()`, and `ledgerly.cli.main()`
returns an `int` exit status code.

## Schema fields

| Field | Meaning |
| --- | --- |
| `entry_id` | Stable identifier for the posting |
| `account` | Account name that receives the posting |
| `amount` | Signed decimal amount |
| `posted_at` | Posting date |

## Entry status values

| Member | Value |
| --- | --- |
| `ENTRY_STATUS_PENDING` | Pending posting |
| `ENTRY_STATUS_POSTED` | Posted posting |
| `ENTRY_STATUS_VOID` | Voided posting |

A ledger persisted by `ledgerly.store.LedgerStore`, such as `examples/entries.csv`,
holds entries across all three status values.
