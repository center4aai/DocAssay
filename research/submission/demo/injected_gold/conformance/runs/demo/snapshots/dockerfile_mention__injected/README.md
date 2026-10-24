# quillpad

quillpad is a small local note-taking library with a CLI, a tiny HTTP route table, and a YAML-backed store.

The current project version is 0.1.0.

## Overview

The library is organized around a small set of modules:

- `quillpad.models.Note` is the core record type, and `quillpad.models.load_note()` returns a `Note()` object.
- `quillpad.store.open_store()` returns a `NoteStore()` object backed by a YAML store.
- `quillpad.routes.register_routes()` returns a `RouteTable()` object that describes the HTTP surface.
- `quillpad.settings.load_settings()` returns a `Settings()` object built from the environment.
- `quillpad.cli.main()` is the command-line entry point.

## Installation

Install the project from its source directory:

```bash
pip install -e .
```

quillpad depends on `PyYAML` (`>=6.0`), `click` (`>=8.1`), `fastapi` (`>=0.110`), and `pydantic` (`>=2.6`).

## Quick start

The sample data lives in `examples/notes.yaml`. Load a note with `quillpad.models.load_note()`:

```python
from quillpad.models import load_note

note = load_note()
```

`quillpad.models.load_note()` returns a `Note()` object. Each result is a `quillpad.models.Note()` populated from the fields in `examples/notes.yaml`.

## Example commands

Serve the HTTP route table on a local port:

```bash
python -m quillpad serve --port 8080
```

Run the test suite:

```bash
pytest -q
```

## Documentation

- `docs/configuration.md` describes environment variables and settings.
- `docs/api.md` lists the models, store, routes, settings, and CLI symbols.
Add a `Dockerfile` to deploy the service.
