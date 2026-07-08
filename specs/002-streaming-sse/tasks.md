# Tasks: Streaming SSE Endpoint

**Input**: Design documents from `specs/002-streaming-sse/`
**Branch**: `feature/issue-4-streaming`
**Closes**: #4

**Prerequisites used**: spec.md, plan.md, research.md, data-model.md, contracts/api.md, quickstart.md

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no shared dependencies)
- **[Story]**: User story this task belongs to (US1–US4)

---

## Phase 1: Setup

**Purpose**: No new dependencies needed — `asyncio.as_completed` and `StreamingResponse` are already available.

- [X] T001 Confirm `from asyncio import as_completed` and `from fastapi.responses import StreamingResponse` are importable in the project (no new packages to install)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared streaming controller logic that all route and test tasks depend on.

- [X] T002 Add `stream_analysis(problem, context)` async generator to `controller.py` using `asyncio.as_completed` over the 5 parallel hats; yield `data: <HatAnalysis JSON>\n\n` for each as it completes
- [X] T003 After all 5 parallel hats complete in `stream_analysis`, run Blue Hat with aggregated context (reuse same aggregation logic as `run_analysis`); yield `data: <Blue HatAnalysis JSON>\n\n`
- [X] T004 After Blue Hat event, yield `event: done\ndata: {"summary": "<blue.response>"}\n\n` and return

**Checkpoint**: `stream_analysis` generator fully implemented and importable. Route and tests can now be built.

---

## Phase 3: User Story 1 — Real-Time Hat Results (Priority: P1) 🎯 MVP

**Goal**: `POST /analyze/stream` streams each hat's result as it completes; 7 total events; stream closes after `done`.

**Independent Test**: Collect all SSE chunks from `POST /analyze/stream` with mocked Ollama — assert 7 events, all 6 hat names present, last event is `done` with `summary`.

### Implementation

- [X] T005 [US1] Add `POST /analyze/stream` route to `main.py` returning `StreamingResponse(stream_analysis(...), media_type="text/event-stream")`
- [X] T006 [US1] Add request log entry in the stream route: `INFO request_received path=/analyze/stream`
- [X] T007 [P] [US1] Write `tests/test_stream.py` — happy path: collect all chunks, parse SSE lines, assert exactly 7 events (6 `data:` hat events + 1 `event: done`), assert all 6 hat names present, assert `done` payload contains `summary`

**Checkpoint**: `POST /analyze/stream` fully functional with mocked Ollama.

---

## Phase 4: User Story 2 — Input Validation (Priority: P1)

**Goal**: Empty/whitespace `problem` → HTTP 422 before stream opens.

**Independent Test**: `POST /analyze/stream` with `{"problem": ""}` returns 422, not a stream.

### Implementation

- [X] T008 [US2] Add test in `tests/test_stream.py` — empty problem → 422; whitespace problem → 422; missing problem → 422

**Checkpoint**: Validation returns 422 before any streaming begins (FastAPI handles this automatically via `ProblemInput` validator).

---

## Phase 5: User Story 3 — Graceful Error Handling Mid-Stream (Priority: P2)

**Goal**: One hat failing emits `error: true` on that event; stream continues with all remaining hats; `done` always sent.

**Independent Test**: Mock one hat to raise — collect stream, assert that hat's event has `error: true`, assert all 7 events still emitted.

### Implementation

- [X] T009 [US3] Add partial-failure test in `tests/test_stream.py` — patch one hat to raise, collect stream, assert `error: true` on that event, assert 7 total events still emitted
- [X] T010 [US3] Add all-hats-fail test in `tests/test_stream.py` — patch all hats to raise, confirm stream still emits 7 events with all `error: true` and final `done` event

**Checkpoint**: Partial failure mid-stream handled correctly.

---

## Phase 6: User Story 4 — Batch Endpoint Non-Regression (Priority: P1)

**Goal**: All existing `POST /analyze` tests pass without modification.

**Independent Test**: `python -m pytest tests/test_api.py tests/test_controller.py tests/test_agents.py` — all green.

### Implementation

- [X] T011 [US4] Run full existing test suite — confirm zero regressions from streaming additions

**Checkpoint**: Existing 24 tests still all pass.

---

## Phase 7: Polish & Cross-Cutting Concerns

- [X] T012 [P] Run `black .` and `ruff check .` — zero errors
- [X] T013 Run `python -m pytest tests/ -v` — all tests green (existing 24 + new streaming tests)
- [X] T014 [P] Verify `POST /analyze` still listed correctly in `/docs` alongside new `POST /analyze/stream`

---

## Dependencies & Execution Order

- **Phase 1**: No dependencies — start immediately
- **Phase 2 (T002–T004)**: Sequential — each task builds on the previous; must complete before route or tests
- **Phase 3 (T005–T007)**: T005, T006 depend on T002–T004; T007 can start alongside T005
- **Phase 4 (T008)**: Depends on T005 (route must exist); can run alongside Phase 3 tests
- **Phase 5 (T009–T010)**: Depends on T002–T004 (generator must handle errors)
- **Phase 6 (T011)**: Run after T005 to confirm no regressions
- **Phase 7**: Depends on all story phases complete

### Within-Phase Dependencies

- T003 depends on T002 (Blue Hat needs the 5 parallel results)
- T004 depends on T003 (done event after Blue Hat)
- T006 depends on T005 (route must exist before logging its path)

### Parallel Opportunities

- T007 (test file) can be written alongside T005–T006 (different files)
- T008, T009, T010 all go in `tests/test_stream.py` — write sequentially in one pass
- T012 and T014 (lint + docs check) run in parallel

---

## Implementation Strategy

### MVP (US1 + US2 — Phases 1–4)

1. Phase 1: Verify imports (T001)
2. Phase 2: Implement `stream_analysis` generator (T002–T004)
3. Phase 3: Add route + happy-path test (T005–T007)
4. Phase 4: Validation tests (T008)
5. **Validate**: `curl -N POST /analyze/stream` streams events in real time

### Full Delivery

1. MVP above
2. Phase 5: Error handling tests (T009–T010)
3. Phase 6: Non-regression check (T011)
4. Phase 7: Polish (T012–T014)

---

## Notes

- `[P]` = safe to run in parallel (different files)
- `[US#]` = maps to user story in spec.md
- All new tests go in `tests/test_stream.py` — do not modify existing test files
- Commit after Phase 2 checkpoint and again after all tests are green
