# ledgerly

A small double-entry bookkeeping library with a CLI, a tiny HTTP route table, and
a CSV-file ledger store.

This is ledgerly version 0.4.2.

## Installation

ledgerly requires Python 3.11 or newer and installs with the following
dependencies:

| Dependency | Constraint |
| --- | --- |
| `click` | `>=8.1` |
| `pydantic` | `>=2.6` |
| `python-dateutil` | `>=2.9` |
| `tabulate` | `>=0.9` |

## Quick start

The bundled sample ledger is the CSV file `examples/entries.csv`, which holds
four columns and a handful of example postings:

```csv
entry_id,account,amount,memo,posted_at
1e2f3a,cash,42.50,invoice 1042,2026-03-01
4b5c6d,revenue,-42.50,invoice 1042,2026-03-01
7a8b9c,rent,-1200.00,march rent,2026-03-02
```

Record a new posting and start the HTTP server with the built-in CLI:

```bash
python -m ledgerly add --account cash --amount 42.50 --memo "invoice 1042"
python -m ledgerly serve --port 8080
```

## Core concepts

`ledgerly.models.Entry` is the in-memory record for one posting, and
`ledgerly.models.parse_entry()` returns an `Entry()` built from a single CSV row.
`ledgerly.models.format_entry()` renders that record as a display line.

`ledgerly.store.LedgerStore` is the CSV-file ledger store. `ledgerly.store.load_store()`
returns a `LedgerStore()` for the configured ledger path, and
`ledgerly.store.save_store()` returns an `int` count of the records it writes back
to disk.

`ledgerly.reports.AccountSummary` aggregates one account, and
`ledgerly.reports.summarize()` returns an `AccountSummary()` for the account you
name. `ledgerly.routes.RouteTable` carries the HTTP route table, and
`ledgerly.routes.build_routes()` returns a `RouteTable()`.

## Configuration

ledgerly reads its settings from environment variables:

| Key | Purpose |
| --- | --- |
| `LEDGERLY_HOME` | Base directory for ledgerly data |
| `LEDGERLY_LEDGER_PATH` | Location of the CSV ledger file |
| `LEDGERLY_LOG_LEVEL` | Verbosity of the CLI log output |
| `LEDGERLY_DEFAULT_CURRENCY` | Currency label used for formatting amounts |

The full walkthrough lives in the configuration guide. Setting
`LEDGERLY_LEDGER_PATH` to `examples/entries.csv` points `ledgerly.store.LedgerStore`
at the bundled sample data.

## HTTP endpoints

`ledgerly.routes.build_routes()` produces a `RouteTable()` with these routes:

| Endpoint | Description |
| --- | --- |
| `/v1/entries` | Create and list ledger entries |
| `/v1/reports/summary` | Per-account summaries |
| `/v1/health` | Service health check |

## CLI

| Command | Symbol | Return type |
| --- | --- | --- |
| python -m ledgerly add | `ledgerly.cli.add_entry()` | `Entry()` |
| python -m ledgerly serve | `ledgerly.cli.main()` | `int` |

`ledgerly.cli.main()` returns an `int` exit status code.
