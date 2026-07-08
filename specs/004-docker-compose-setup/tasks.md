# Tasks: Docker & Docker Compose Setup

**Input**: Design documents from `specs/004-docker-compose-setup/`
**Branch**: `feature/issue-6-docker`
**Closes**: #6

**Prerequisites used**: spec.md, plan.md, research.md, quickstart.md

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story this task belongs to (US1–US3)

---

## Phase 1: Setup

**Purpose**: Exclude unnecessary files from the Docker build context before any image is defined.

- [X] T001 Create `.dockerignore` at repo root excluding `.git/`, `__pycache__/`, `.venv/`, `specs/`, `tests/`, `.env*`, `*.md`, `.specify/`, `docker-compose.yml`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The entrypoint script is required by both the Dockerfile and the Compose health-check flow; it must exist before either is authored.

- [X] T002 Create `entrypoint.sh` at repo root: poll `$OLLAMA_URL/api/tags` until reachable, then `POST /api/pull` for `$OLLAMA_MODEL`, then `exec uvicorn main:app --host 0.0.0.0 --port 8000`; set `chmod +x` in the same task
- [X] T003 Create `Dockerfile` with two stages: `builder` (python:3.11-slim, install requirements.txt into `/opt/venv`) and `runtime` (python:3.11-slim, copy venv + app, set `PATH`, `EXPOSE 8000`, `ENTRYPOINT ["./entrypoint.sh"]`)

**Checkpoint**: `docker build -t six-hats-test .` succeeds (Ollama not needed for the build itself).

---

## Phase 3: User Story 1 — One-Command Stack Startup (Priority: P1) 🎯 MVP

**Goal**: `docker compose up --build` starts both services; API health check returns 200 within 30 s.

**Independent Test**: `curl http://localhost:8000/health` → `{"status":"ok"}` after `docker compose up --build`.

- [X] T004 [US1] Create `docker-compose.yml` defining `ollama` service (`ollama/ollama` image, `ollama_data` volume, port 11434, healthcheck `ollama list`) and `api` service (build `.`, port 8000, `OLLAMA_URL: http://ollama:11434`, `OLLAMA_MODEL: ${OLLAMA_MODEL:-llama3}`, `depends_on: ollama: condition: service_healthy`) plus top-level `volumes: ollama_data:`

**Checkpoint**: `docker compose up --build` → `GET /health` returns 200.

---

## Phase 4: User Story 2 — Secure, Configurable Deployment (Priority: P2)

**Goal**: No secrets baked into the image; model name overridable via env var without rebuild.

**Independent Test**: `docker run --rm <image> find / -name ".env"` returns nothing; `OLLAMA_MODEL=mistral docker compose up` logs `Pulling model: mistral`.

- [X] T005 [US2] Verify `.dockerignore` excludes `.env` and `.env.*` — confirm with `docker build` that no `.env` file appears in the image filesystem (adjust `.dockerignore` if needed)
- [X] T006 [P] [US2] Add `OLLAMA_MODEL` variable reference in `docker-compose.yml` using `${OLLAMA_MODEL:-llama3}` syntax so operators can override without editing the file (already included in T004 — mark done if complete)

**Checkpoint**: Image contains no `.env`; model is configurable.

---

## Phase 5: User Story 3 — Minimal Production-Ready Image (Priority: P3)

**Goal**: Final image contains only runtime deps — no pip, compilers, or build caches.

**Independent Test**: `docker image inspect` shows image built from `python:3.11-slim` runtime stage only; `pip` is not on `PATH` inside the container.

- [X] T007 [US3] Confirm multi-stage build in `Dockerfile` copies only `/opt/venv` and app source into the runtime stage — verify `pip` is absent by running `docker run --rm <image> pip --version` and confirming it fails

**Checkpoint**: `pip --version` inside the runtime container exits non-zero.

---

## Phase 6: Polish & Validation

- [X] T008 [P] Run `python -m black .` and `python -m ruff check .` — zero errors (shell scripts are exempt from Python linters)
- [X] T009 [P] Run `python -m pytest tests/ -v` — all 32 existing tests still pass (Docker changes must not affect unit suite)
- [X] T010 [P] Confirm `docker build -t six-hats-test .` completes without errors

---

## Dependencies & Execution Order

- **T001** first — `.dockerignore` must exist before any `docker build`
- **T002** before T003 — `entrypoint.sh` is referenced in the `Dockerfile` `ENTRYPOINT`
- **T003** before T004 — `Dockerfile` must exist before `docker-compose.yml` tries to build it
- **T004** before T005/T006/T007 — Compose file must exist to validate security and image properties
- **T006** is effectively part of T004; mark complete once T004 is done
- **T008–T010** after all story phases

---

## Implementation Strategy

### MVP (US1 — Phases 1–3)

1. T001: `.dockerignore`
2. T002: `entrypoint.sh`
3. T003: `Dockerfile`
4. T004: `docker-compose.yml`
5. Validate: `docker compose up --build` → `curl /health`

### Full Delivery

1. MVP above
2. T005–T007: Security + image size validation
3. T008–T010: Lint, tests, build check
