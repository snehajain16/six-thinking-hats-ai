# Tasks: Core Hardening — Multi-Agent Pipeline, API & Ollama Integration

**Input**: Design documents from `specs/001-core-hardening/`
**Branch**: `feature/issue-1-2-3-core-hardening`
**Closes**: #1, #2, #3

**Prerequisites used**: spec.md, plan.md, research.md, data-model.md, contracts/api.md, quickstart.md

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no shared dependencies)
- **[Story]**: User story this task belongs to (US1–US4)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Ensure project dependencies and configuration scaffolding are in place before any feature work begins.

- [x] T001 Add `python-dotenv` to `requirements.txt` if not already present
- [x] T002 [P] Add `pytest`, `pytest-asyncio`, `pytest-cov` to `requirements-dev.txt`
- [x] T003 [P] Create `logging_config.py` at project root with `dictConfig` JSON-friendly stdout logger

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core changes that all user stories depend on. Must complete before any story work begins.

⚠️ **CRITICAL**: No user story work can begin until this phase is complete.

- [x] T004 Add `error: bool = False` field to `HatAnalysis` in `models.py`
- [x] T005 Add `@field_validator("problem")` to `ProblemInput` in `models.py` — strip whitespace, raise `ValueError` if empty
- [x] T006 Update `agents/base.py` — split `httpx.Timeout` to `connect=5.0, read=120.0, write=5.0, pool=5.0`
- [x] T007 Wrap `_call_ollama` body in `agents/base.py` with try/except; re-raise so `analyze()` can catch it
- [x] T008 Update `analyze()` in `agents/base.py` — catch all exceptions, return `HatAnalysis(error=True, response=str(exc))` instead of raising
- [x] T009 Update `controller.py` — use `asyncio.gather(*tasks, return_exceptions=True)`; convert `Exception` results to `HatAnalysis(error=True, response=str(exc))`

**Checkpoint**: Foundational data model and error-handling layer ready. User story work can now begin.

---

## Phase 3: User Story 1 — Submit Problem, Receive Full Six-Hat Analysis (Priority: P1) 🎯 MVP

**Goal**: A valid problem submission returns a complete `SixHatsResponse` with 6 hat analyses and a summary. Partial failures return gracefully with `error=True` on the affected hat.

**Independent Test**: `POST /analyze` with a real problem string returns HTTP 200 with exactly 6 `HatAnalysis` items; `analyses[5].response` equals `summary`.

### Implementation

- [x] T010 [US1] Load `.env` via `python-dotenv` at top of `main.py` (before app creation)
- [x] T011 [US1] Import and apply `logging_config.py` in `main.py` before `FastAPI()` instantiation
- [x] T012 [US1] Add structured log calls in `agents/base.py` — `hat_call_start` (hat name, model) and `hat_call_done` (hat name, model, duration_ms, error) around `_call_ollama`
- [x] T013 [US1] Add request logging middleware to `main.py` — log `method`, `path`, `duration_ms`, `status_code` on each request
- [x] T014 [US1] Update `controller.py` — build `aggregated` context string from non-error hat analyses; pass to Blue Hat with a note about any failures
- [x] T015 [US1] Verify `POST /analyze` route in `main.py` returns `SixHatsResponse` with correct `summary` = Blue Hat `response`

**Checkpoint**: `POST /analyze` happy path fully functional and observable via logs.

---

## Phase 4: User Story 2 — Health Check Endpoint (Priority: P2)

**Goal**: `GET /health` returns `{"status": "ok"}` with HTTP 200 regardless of Ollama state.

**Independent Test**: `curl http://localhost:8000/health` returns 200 with `{"status":"ok"}` even when `OLLAMA_URL` points at a dead host.

### Implementation

- [x] T016 [US2] Confirm `GET /health` route in `main.py` returns `{"status": "ok"}` with no Ollama dependency
- [x] T017 [US2] Add log entry in health route — `INFO` with `path=/health` and `status=ok`

**Checkpoint**: Health endpoint independently verified via `curl`.

---

## Phase 5: User Story 3 — Startup Connectivity Warning (Priority: P3)

**Goal**: On startup, a `GET /api/tags` probe is sent to Ollama. A `WARNING` log is emitted if unreachable; the app starts either way.

**Independent Test**: Start with `OLLAMA_URL=http://localhost:19999 uvicorn main:app` — app starts, logs contain `WARNING` with Ollama URL, `GET /health` still returns 200.

### Implementation

- [x] T018 [US3] Replace bare `app = FastAPI(...)` in `main.py` with a `lifespan` async context manager
- [x] T019 [US3] Inside `lifespan` startup: send `GET {OLLAMA_URL}/api/tags` with 5s timeout; log `INFO` on success, `WARNING` with URL on failure; never raise

**Checkpoint**: Startup log visible for both reachable and unreachable Ollama.

---

## Phase 6: User Story 4 — Configure LLM Backend via Environment Variables (Priority: P2)

**Goal**: Setting `OLLAMA_URL` and `OLLAMA_MODEL` in `.env` or the shell changes all Ollama calls with zero code changes.

**Independent Test**: `OLLAMA_MODEL=mistral uvicorn main:app` — Ollama logs show `mistral` being called when `/analyze` is hit.

### Implementation

- [x] T020 [US4] Confirm `OLLAMA_URL` and `OLLAMA_MODEL` are read from `os.getenv` in `agents/base.py` at module level
- [x] T021 [US4] Update `.env.example` to document `OLLAMA_URL`, `OLLAMA_MODEL` with defaults and descriptions

**Checkpoint**: Switching model requires only `.env` change, confirmed manually.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Test suite, validation, and cleanup across all stories.

- [x] T022 [P] Write `tests/conftest.py` — `AsyncMock` fixture patching `BaseHatAgent._call_ollama` to return canned `HatAnalysis`
- [x] T023 [P] Write `tests/test_agents.py` — assert each hat's `system_prompt` is non-empty and contains the hat name; assert `error=True` path works
- [x] T024 [P] Write `tests/test_controller.py` — assert 6 results returned; assert partial failure (one mock raises) returns `error=True` on that hat only; assert Blue Hat always runs
- [x] T025 [P] Write `tests/test_api.py` — `GET /health` → 200; `POST /analyze` valid → 200 `SixHatsResponse`; `POST /analyze` empty problem → 422; `POST /analyze` Ollama down → 500
- [x] T026 Run `pytest` — all tests green
- [x] T027 [P] Run `black .` and `ruff check .` — zero errors
- [x] T028 Validate all 6 quickstart.md scenarios manually (or via test suite where applicable)
- [x] T029 [P] Confirm `/docs` shows accurate schemas for `ProblemInput`, `HatAnalysis`, `SixHatsResponse`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Foundational)**: Requires Phase 1 — blocks all user story phases
- **Phase 3 (US1)**: Requires Phase 2 — core pipeline + API
- **Phase 4 (US2)**: Requires Phase 2 — independent of US1
- **Phase 5 (US3)**: Requires Phase 2, and T010/T011 from Phase 3 (needs `lifespan` + logging in place)
- **Phase 6 (US4)**: Requires T001 (python-dotenv) from Phase 1
- **Phase 7 (Polish)**: Requires all story phases complete

### Within-Phase Dependencies

- T005 depends on T004 (need `error` field before validator makes sense)
- T008 depends on T007 (catch needs the re-raise)
- T009 depends on T008 (controller catches what agent re-raises)
- T014 depends on T009 (aggregation uses the new gather result)
- T019 depends on T018 (lifespan probe goes inside lifespan context)

### Parallel Opportunities

All Phase 1 tasks (T001–T003) run in parallel.
Phase 2 tasks T004–T005 can run in parallel (different fields in `models.py`).
Phase 2 tasks T006–T008 are sequential (each builds on the previous).
Phase 7 test tasks T022–T025 all run in parallel (different test files).

---

## Parallel Example: Phase 7 (Polish)

```
Launch in parallel:
  T022 → tests/conftest.py
  T023 → tests/test_agents.py
  T024 → tests/test_controller.py
  T025 → tests/test_api.py
  T027 → black + ruff
  T029 → docs validation

Sequential after T022–T025:
  T026 → pytest (depends on all test files existing)
  T028 → quickstart manual validation
```

---

## Implementation Strategy

### MVP (P1 only — Phases 1–3)

1. Phase 1: Setup (T001–T003)
2. Phase 2: Foundational (T004–T009)
3. Phase 3: US1 core pipeline + API (T010–T015)
4. **Validate**: `POST /analyze` returns full `SixHatsResponse`; logs visible

### Full Delivery (All Stories)

1. MVP above
2. Phase 4: US2 health check (T016–T017)
3. Phase 5: US3 startup probe (T018–T019)
4. Phase 6: US4 env config (T020–T021)
5. Phase 7: Polish — tests, lint, docs (T022–T029)

---

## Notes

- `[P]` = safe to run in parallel (different files, no shared write targets)
- `[US#]` = maps to user story in `spec.md` for traceability
- Commit after each phase checkpoint to keep git history clean
- Run `GET /health` after every commit to confirm the app still starts
