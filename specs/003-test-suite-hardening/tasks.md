# Tasks: Test Suite Hardening

**Input**: Design documents from `specs/003-test-suite-hardening/`
**Branch**: `feature/issue-5-test-suite`
**Closes**: #5

**Prerequisites used**: spec.md, plan.md, research.md, quickstart.md

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story this task belongs to (US1–US2)

---

## Phase 1: Setup

**Purpose**: Create `pytest.ini` so the `integration` marker is registered before any test changes.

- [X] T001 Create `pytest.ini` at repo root with `asyncio_mode = strict` and `integration` marker registration

---

## Phase 2: User Story 1 — Complete Unit Coverage (Priority: P1) 🎯 MVP

**Goal**: Every gap in Issue #5's unit acceptance criteria is covered — call count, context default, and full hat-name in system_prompt.

**Independent Test**: `python -m pytest tests/ -v` — all pass, no warnings.

- [X] T002 [P] [US1] Add `test_run_analysis_calls_ollama_six_times` to `tests/test_controller.py` — assert `mock_ollama.call_count == 6` after a single `run_analysis` call
- [X] T003 [P] [US1] Add `test_problem_input_context_defaults_to_none` to `tests/test_api.py` — assert `ProblemInput(problem="x").context is None`
- [X] T004 [P] [US1] Verify `test_agent_attributes` in `tests/test_agents.py` checks the full hat name (e.g. `"White Hat"`) in `system_prompt`, not just the first word — update the assertion if needed without breaking the existing test

**Checkpoint**: `python -m pytest tests/ -v` — 33+ tests pass, zero failures.

---

## Phase 3: User Story 2 — Integration Test Infrastructure (Priority: P2)

**Goal**: `@pytest.mark.integration` skips automatically when `OLLAMA_URL` is unset; no unknown-mark warnings.

**Independent Test**: `pytest --markers | grep integration` shows the marker; `unset OLLAMA_URL && pytest -m integration` shows all skipped.

- [X] T005 [US2] Add `pytest_collection_modifyitems` hook to `tests/conftest.py` — skip `integration`-marked items when `os.getenv("OLLAMA_URL", "").strip()` is falsy

**Checkpoint**: `python -m pytest tests/ -v` — all pass; `python -m pytest --markers` lists `integration`.

---

## Phase 4: Polish & Validation

- [X] T006 [P] Run `python -m black .` and `python -m ruff check .` — zero errors
- [X] T007 Run `python -m pytest tests/ -v` — all tests green (existing 30 + new tests)
- [X] T008 [P] Run `python -m pytest --markers | grep integration` — marker listed with description

---

## Dependencies & Execution Order

- **T001** first — `pytest.ini` must exist before tests are collected
- **T002, T003, T004** can run in parallel (different files)
- **T005** depends on T001 (`pytest.ini` marker registration must precede the skip hook)
- **T006–T008** after all story phases complete

---

## Implementation Strategy

### MVP (US1 — Phase 2)

1. T001: Create `pytest.ini`
2. T002–T004: Add the three missing assertions
3. Validate: `python -m pytest tests/ -v`

### Full Delivery

1. MVP above
2. T005: Add integration marker skip hook
3. T006–T008: Lint + full test run + marker check
