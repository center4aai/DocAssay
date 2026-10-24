# Configuration

ledgerly is configured through environment variables, and each setting flows
into the library components directly.

## Environment keys

| Key | Purpose |
| --- | --- |
| `LEDGERLY_HOME` | Base directory for ledgerly data |
| `LEDGERLY_LEDGER_PATH` | Location of the CSV ledger file |
| `LEDGERLY_LOG_LEVEL` | Verbosity of the CLI log output |
| `LEDGERLY_DEFAULT_CURRENCY` | Currency label used for formatting amounts |

## Pointing at a ledger file

`LEDGERLY_LEDGER_PATH` names the CSV ledger. The bundled sample is
`examples/entries.csv`, and `ledgerly.store.LedgerStore` reads that file through
`ledgerly.store.load_store()`, which returns a `LedgerStore()` instance.

```bash
export LEDGERLY_LEDGER_PATH=examples/entries.csv
```

## Currency and formatting

`LEDGERLY_DEFAULT_CURRENCY` sets the currency label used when amounts are
rendered. `ledgerly.models.format_entry()` formats one record, and
`ledgerly.models.parse_entry()` returns an `Entry()` from a CSV row.

## Data directory

`LEDGERLY_HOME` selects the base directory for ledgerly data, and
`LEDGERLY_LOG_LEVEL` sets log verbosity for `ledgerly.cli.main()`, which returns
an `int` exit status code.

## Ledger file layout

The ledger at `examples/entries.csv` carries these fields on each row:

| Field | Meaning |
| --- | --- |
| `entry_id` | Stable identifier for the posting |
| `account` | Account name that receives the posting |
| `amount` | Signed decimal amount |
| `posted_at` | Posting date |

`ledgerly.store.save_store()` returns an `int` count of the records it persists
back into the ledger file.
