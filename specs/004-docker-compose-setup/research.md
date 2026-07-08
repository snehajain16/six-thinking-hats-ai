# Research: Docker & Docker Compose Setup

**Feature**: specs/004-docker-compose-setup
**Date**: 2026-07-08

## Decision: Multi-Stage Dockerfile

- **Decision**: Two stages — `builder` (installs pip deps into `/opt/venv`) and `runtime` (copies venv + app only).
- **Rationale**: Keeps the final image free of `pip`, build headers, and package caches. `python:3.11-slim` as base is the standard minimal Python image.
- **Alternatives considered**: Single-stage with `pip install --no-cache-dir` — still leaves pip and wheel in the image; rejected.

## Decision: Entrypoint Pulls Model via Ollama HTTP API

- **Decision**: `entrypoint.sh` waits for Ollama to be reachable (polling `/api/tags`), then issues a pull via `POST /api/pull`, then starts uvicorn. Uses `wget` (available in `python:3.11-slim`) rather than the `ollama` CLI (which is not in the API container).
- **Rationale**: The `ollama` CLI binary lives inside the `ollama/ollama` image, not the API image. The HTTP pull API (`POST /api/pull`) achieves the same result and only requires `wget` or `curl`.
- **Alternatives considered**: Relying on Ollama's auto-download on first `/api/chat` call — risks the first real user request timing out while the model downloads; rejected in favour of eager pull at startup.

## Decision: `depends_on` with `service_healthy`

- **Decision**: Use `depends_on: ollama: condition: service_healthy` with an `ollama` healthcheck (`ollama list`).
- **Rationale**: Ensures Compose starts the `api` container only after Ollama is actually ready to serve requests, not just after the container process starts.
- **Alternatives considered**: `depends_on` without condition (just checks container started) — insufficient; `restart: always` on api — treats symptoms not root cause; rejected.

## Decision: `wget` over `curl` in entrypoint

- **Decision**: Use `wget` in `entrypoint.sh`.
- **Rationale**: `wget` is pre-installed in `python:3.11-slim`; `curl` is not. Avoids an extra `RUN apt-get install curl` layer that increases image size.
- **Alternatives considered**: `curl` with explicit install — adds ~3 MB; rejected. Python one-liner via `python -c "import urllib..."` — verbose; rejected.
