# Feature Specification: Test Suite Hardening

**Feature Branch**: `feature/issue-5-test-suite`

**Created**: 2026-07-08

**Status**: Draft

**Input**: User description: "Harden the existing pytest suite and add missing coverage per Issue #5 acceptance criteria"

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Complete Unit Coverage (Priority: P1)

A developer running the test suite should have confidence that every unit of the six-hat pipeline is verified: each agent's identity, the orchestrator's call count, the response shape, and the Blue Hat synthesis contract.

**Why this priority**: Closes the gaps called out in Issue #5's acceptance criteria. These are the core unit-level contracts the rest of the system depends on.

**Independent Test**: Run the unit suite with Ollama mocked — all assertions pass without a live model.

**Acceptance Scenarios**:

1. **Given** the test suite runs with a mocked LLM, **When** each hat agent is inspected, **Then** its identity prompt is non-empty and references the hat by name.
2. **Given** a single `run_analysis` call with a mocked LLM, **When** the call completes, **Then** the underlying LLM was invoked exactly 6 times (once per hat).
3. **Given** a valid problem submitted to the orchestrator, **When** the response is examined, **Then** it contains exactly 6 `HatAnalysis` objects.
4. **Given** a completed analysis, **When** the summary field is read, **Then** it equals the Blue Hat agent's response verbatim.
5. **Given** a `ProblemInput` created without a `context` field, **When** the model is inspected, **Then** `context` is `None` or an empty string.

---

### User Story 2 — Integration Test Infrastructure (Priority: P2)

A developer or CI system should be able to mark tests as integration tests so they are skipped in unit-only runs and opt-in when a live Ollama instance is available.

**Why this priority**: The constitution mandates `@pytest.mark.integration` for live-model tests. The infrastructure must exist so future integration tests can be written correctly.

**Independent Test**: Run `pytest` without `OLLAMA_URL` set — zero integration-marked tests execute. Run with `OLLAMA_URL` set — integration-marked tests are collected.

**Acceptance Scenarios**:

1. **Given** `OLLAMA_URL` is not set in the environment, **When** the suite runs, **Then** any test marked `@pytest.mark.integration` is skipped automatically.
2. **Given** `OLLAMA_URL` is set, **When** the suite runs, **Then** integration-marked tests are collected and executed.
3. **Given** the marker is registered, **When** `pytest --markers` is run, **Then** `integration` appears in the list with a description.

---

### Edge Cases

- What if a hat agent's `system_prompt` contains the hat name only in a different case? The check is case-insensitive.
- What if `OLLAMA_URL` is set but is an empty string? Treat as not set; skip integration tests.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The test suite MUST assert that each of the 6 hat agents has a non-empty `system_prompt` that contains the hat's name (case-insensitive).
- **FR-002**: The test suite MUST assert that `run_analysis` triggers exactly 6 LLM calls for a single problem input.
- **FR-003**: The test suite MUST assert that `SixHatsResponse.analyses` contains exactly 6 items.
- **FR-004**: The test suite MUST assert that `SixHatsResponse.summary` equals the Blue Hat agent's response verbatim.
- **FR-005**: The test suite MUST assert that `ProblemInput` defaults `context` to `None` or empty string when omitted.
- **FR-006**: The project MUST register an `integration` pytest marker so tests decorated with `@pytest.mark.integration` are recognised without unknown-mark warnings.
- **FR-007**: Tests marked `@pytest.mark.integration` MUST be automatically skipped when `OLLAMA_URL` is not set (or is empty) in the environment.
- **FR-008**: Existing passing tests MUST NOT be modified or broken.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All 5 new unit assertions (FR-001 through FR-005) pass with a mocked LLM — zero failures.
- **SC-002**: The `integration` marker is resolvable by the test runner with no unknown-mark warnings.
- **SC-003**: Running the full suite without `OLLAMA_URL` skips all integration-marked tests and passes 100% of the remaining tests.
- **SC-004**: No previously passing test is broken by these changes.

## Assumptions

- The existing `conftest.py` mock (`mock_ollama` fixture) is the correct place to count LLM calls via `call_count`.
- "Hat name" means the value of the agent's `hat` attribute (e.g., `"White Hat"`) — the system prompt must contain at least this string (case-insensitive).
- The `integration` marker skip logic belongs in `conftest.py` via a `pytest_collection_modifyitems` hook, with the marker registered in `pytest.ini` or `pyproject.toml`.
- No new test files are created; additions go into the existing `tests/` files.
