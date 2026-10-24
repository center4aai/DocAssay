# Configuration

quillpad reads its settings through `quillpad.settings.load_settings()`, which returns a `Settings()` object populated from environment variables.

## Environment variables

| Key | Purpose |
| --- | --- |
| `QUILLPAD_HOME` | Base directory for quillpad data. |
| `QUILLPAD_LOG_LEVEL` | Logging verbosity. |
| `QUILLPAD_STORE_PATH` | Path to the YAML-backed store. |

## Settings fields

`quillpad.settings.Settings` carries the resolved values.

| Field | Description |
| --- | --- |
| `home` | Resolved home directory for quillpad data. |
| `log_level` | Resolved logging verbosity. |
| `store_path` | Resolved path to the YAML-backed store. |

## Store data

The store loads notes from `examples/notes.yaml`. Each entry in that file maps to a `quillpad.models.Note` record with the fields `note_id`, `title`, `body_text`, `created_at`, and `status`.

`quillpad.store.open_store()` returns a `NoteStore()` object whose `store_path` points at the store file and whose `notes` collection holds the loaded `quillpad.models.Note` records.

## Limits

`quillpad.constants.Limits` carries the configurable `max_notes` bound.

## Status members

The note status members are defined in the constants module:

| Member |
| --- |
| `NOTE_STATUS_DRAFT` |
| `NOTE_STATUS_PUBLISHED` |
| `NOTE_STATUS_ARCHIVED` |
