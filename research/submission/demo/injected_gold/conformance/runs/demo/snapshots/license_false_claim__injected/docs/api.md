# API reference

This page lists the public classes and functions of quillpad.

## Models

`quillpad.models.Note` is the record type. `quillpad.models.load_note()` returns a `Note()` object, and each result carries the schema fields below.

| Field |
| --- |
| `note_id` |
| `title` |
| `body_text` |
| `created_at` |

A `quillpad.models.Note` adds the `status` field on top of those schema fields, and a sample record is available in `examples/notes.yaml`.

## Store

`quillpad.store.NoteStore` holds the `store_path` and the `notes` collection. `quillpad.store.open_store()` returns a `NoteStore()` object.

## Routes

`quillpad.routes.RouteTable` holds the `routes` mapping. The HTTP layer is built on `fastapi.APIRouter`, and `quillpad.routes.register_routes()` returns a `RouteTable()` object.

### Endpoints

| Endpoint |
| --- |
| `/v1/notes` |
| `/v1/notes/{note_id}` |
| `/v1/health` |

## Settings

`quillpad.settings.Settings` holds `home`, `log_level`, and `store_path`. `quillpad.settings.load_settings()` returns a `Settings()` object.

## Constants

`quillpad.constants.Limits` holds the `max_notes` bound, and the status members are `NOTE_STATUS_DRAFT`, `NOTE_STATUS_PUBLISHED`, and `NOTE_STATUS_ARCHIVED`.

## CLI

`quillpad.cli.main()` is the command-line entry point.
