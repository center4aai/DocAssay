"""``python -m docassay.webapp`` — run the web UI (requires ``[web]`` extra)."""

from docassay.webapp.server import main

if __name__ == "__main__":
    raise SystemExit(main())
