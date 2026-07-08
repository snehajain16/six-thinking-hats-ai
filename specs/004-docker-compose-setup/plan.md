# Implementation Plan: Docker & Docker Compose Setup

**Branch**: `feature/issue-6-docker` | **Date**: 2026-07-08 | **Spec**: [spec.md](spec.md)

**Closes**: #6

## Summary

Add `Dockerfile` (multi-stage), `docker-compose.yml`, `entrypoint.sh`, and `.dockerignore` so the full stack — FastAPI API + Ollama — starts with `docker compose up`. The API image is kept minimal (runtime deps only); model name is configurable via env var; pulled models persist in a named volume.

## Technical Context

**Language/Version**: Python 3.11 (matches existing codebase)

**Primary Dependencies**: Docker Engine 24+, Compose V2 plugin — no new Python packages

**Storage**: Named Docker volume `ollama_data` for model persistence

**Testing**: Manual validation per quickstart.md — `GET /health` within 30 s; existing pytest suite run inside CI (no Docker required for unit tests)

**Target Platform**: Linux (amd64); Docker Desktop on Mac/Windows also supported

**Project Type**: DevOps / containerisation — no production source code changes

**Performance Goals**: API health check green within 30 s of `docker compose up --build`

**Constraints**: Image must contain no build tools or dev artifacts; no secrets baked in

## Constitution Check

| Principle | Status | Notes |
|---|---|---|
| I. Spec-First | ✅ | spec.md written and validated |
| II. Agent Isolation | ✅ | No agent code changes |
| III. Local-First Inference | ✅ | Ollama still runs locally, now in a container |
| IV. Async-First Concurrency | ✅ | No concurrency changes |
| V. Typed Contracts | ✅ | No model changes |
| VI. Test-Driven Quality Gate | ✅ | Existing 32-test suite unchanged; quickstart.md is the validation guide |

## Project Structure

### New Files

```text
Dockerfile          ← multi-stage build (builder + runtime)
docker-compose.yml  ← api + ollama services, volume, health check
entrypoint.sh       ← pull model then exec uvicorn
.dockerignore       ← exclude .git, __pycache__, .venv, specs/, tests/, etc.
```

No changes to: `main.py`, `controller.py`, `agents/`, `models.py`, `tests/`, `pytest.ini`.

## Implementation Design

### `Dockerfile` — multi-stage

```dockerfile
# Stage 1: builder — install deps into a venv
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# Stage 2: runtime — copy app + venv only
FROM python:3.11-slim AS runtime
ENV PATH="/opt/venv/bin:$PATH"
WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
COPY . .
RUN chmod +x entrypoint.sh
EXPOSE 8000
ENTRYPOINT ["./entrypoint.sh"]
```

### `entrypoint.sh`

```sh
#!/bin/sh
set -e
MODEL="${OLLAMA_MODEL:-llama3}"
echo "Pulling model: $MODEL"
ollama pull "$MODEL" || { echo "Failed to pull model $MODEL"; exit 1; }
exec uvicorn main:app --host 0.0.0.0 --port 8000
```

Wait — `ollama` CLI is not in the API container; Ollama runs as a separate service. The entrypoint should use the HTTP API to trigger a pull on the Ollama service, or simply wait for Ollama to be ready and rely on the first `/api/chat` call (Ollama auto-downloads on first use when `OLLAMA_ORIGINS=*`).

**Revised approach**: The entrypoint waits for Ollama to be reachable (health probe loop), then issues a pull via `curl` or `wget` against the Ollama HTTP API, then starts uvicorn.

```sh
#!/bin/sh
set -e
OLLAMA_URL="${OLLAMA_URL:-http://localhost:11434}"
MODEL="${OLLAMA_MODEL:-llama3}"

echo "Waiting for Ollama at $OLLAMA_URL..."
until wget -qO- "$OLLAMA_URL/api/tags" > /dev/null 2>&1; do
  sleep 2
done

echo "Pulling model: $MODEL"
wget -qO- --post-data="{\"name\":\"$MODEL\"}" \
  --header="Content-Type: application/json" \
  "$OLLAMA_URL/api/pull" > /dev/null

echo "Starting API..."
exec uvicorn main:app --host 0.0.0.0 --port 8000
```

### `docker-compose.yml`

```yaml
services:
  ollama:
    image: ollama/ollama
    volumes:
      - ollama_data:/root/.ollama
    ports:
      - "11434:11434"
    healthcheck:
      test: ["CMD", "ollama", "list"]
      interval: 10s
      timeout: 5s
      retries: 5

  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      OLLAMA_URL: http://ollama:11434
      OLLAMA_MODEL: ${OLLAMA_MODEL:-llama3}
    depends_on:
      ollama:
        condition: service_healthy

volumes:
  ollama_data:
```

### `.dockerignore`

```
.git/
.venv/
venv/
__pycache__/
*.pyc
*.pyo
.env
.env.*
specs/
tests/
*.md
.specify/
.dockerignore
docker-compose.yml
```
