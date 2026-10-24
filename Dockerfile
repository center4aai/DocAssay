# syntax=docker/dockerfile:1
# DocAssay — local-first documentation verifier.
#
# Build and run it:
#   docker build -t docassay:demo .
#   docker run --rm -p 8000:8000 docassay:demo
#
# The image serves the prebuilt web UI from /app/web/dist. A corpus is optional;
# mount one and pass --corpus/--allow-root, or upload a zip / paste a URL in the UI.

# ---- stage 1: build the SPA -------------------------------------------------
FROM node:20-alpine AS web
WORKDIR /web
COPY web/package.json web/package-lock.json ./
RUN npm ci
COPY web/ ./
RUN npm run build

# ---- stage 2: the tool ------------------------------------------------------
FROM python:3.12-slim AS app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# The venv lives outside the default PATH, but the entrypoint is absolute. Put it
# on PATH too, so `docker exec <id> docassay …` (the walkthrough commands) works.
ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# git is required by the clone path and by the tracked-file evidence layer
# (git ls-files); the slim base image ships neither git nor CA roots.
RUN apt-get update \
    && apt-get install -y --no-install-recommends git ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock README.md LICENSE ./
COPY src ./src
RUN uv sync --frozen --no-dev --extra web --extra agent

COPY --from=web /web/dist ./web/dist

RUN useradd --create-home --uid 10001 app \
    && install -d -o app -g app /home/app/.local/share/docassay
USER app

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=3s --retries=5 \
    CMD python -c "import os, urllib.request; urllib.request.urlopen('http://127.0.0.1:' + os.environ.get('DOCASSAY_PORT', '8000') + '/health').read()"

ENTRYPOINT ["/app/.venv/bin/docassay"]
CMD ["web", \
     "--host", "0.0.0.0", \
     "--static", "/app/web/dist", \
     "--allowed-host", "*", \
     "--allow-bare-index"]
