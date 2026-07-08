# Feature Specification: Streaming SSE Endpoint

**Feature Branch**: `feature/issue-4-streaming`

**Created**: 2026-07-08

**Status**: Draft

**Closes**: #4

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Receive Hat Results as They Arrive, Not All at Once (Priority: P1)

A developer or client application submits a problem to the streaming endpoint and sees each hat's perspective appear in real time as it completes, rather than waiting for all six to finish. This dramatically reduces perceived latency, especially with slower models.

**Why this priority**: Core value of this feature. Without real-time delivery, the endpoint has no advantage over `POST /analyze`.

**Independent Test**: Open a streaming connection to `POST /analyze/stream` with a valid problem. Confirm events arrive incrementally — one per hat — before the final `done` event closes the stream.

**Acceptance Scenarios**:

1. **Given** a valid problem is submitted to `POST /analyze/stream`, **When** the first hat completes, **Then** that hat's result is immediately sent as an SSE event — without waiting for the other hats.
2. **Given** five hats run concurrently, **When** each finishes at different times, **Then** each result is streamed the moment it completes (order may vary).
3. **Given** all five parallel hats have completed, **When** the Blue Hat finishes, **Then** two events are emitted: the Blue Hat analysis event, followed by a final `done` event containing only the `summary`.
4. **Given** a streaming connection is open, **When** all events have been sent, **Then** the stream closes cleanly and the client can detect the end via the `done` event.

---

### User Story 2 — Input Validation on Streaming Endpoint (Priority: P1)

The streaming endpoint enforces the same input rules as the batch endpoint — empty or whitespace-only problems are rejected immediately, before any LLM calls are made.

**Why this priority**: Without validation, a bad request would open a stream and immediately close it in a confusing way. Rejection must be immediate and clear.

**Independent Test**: Submit `POST /analyze/stream` with an empty `problem`. Confirm HTTP 422 is returned before any streaming begins.

**Acceptance Scenarios**:

1. **Given** a request with an empty `problem`, **When** `POST /analyze/stream` is called, **Then** HTTP 422 is returned with a validation error — no stream is opened.
2. **Given** a request with a whitespace-only `problem`, **When** `POST /analyze/stream` is called, **Then** HTTP 422 is returned.

---

### User Story 3 — Graceful Error Handling Mid-Stream (Priority: P2)

If one or more hat agents fail during a streaming session, the stream continues — the failed hat's result is emitted with an error flag and the remaining hats proceed normally.

**Why this priority**: Matches the graceful degradation guarantee already established in `POST /analyze`. The streaming contract must be consistent.

**Independent Test**: With a mocked agent that raises an error, confirm the stream still emits all 6 events, with the failed hat's event having `error: true`.

**Acceptance Scenarios**:

1. **Given** one hat agent fails mid-stream, **When** the event for that hat is emitted, **Then** it contains `"error": true` and a description of the failure.
2. **Given** a hat fails, **When** the stream continues, **Then** all remaining hats and the Blue Hat still emit their events normally.
3. **Given** all 5 parallel hats fail, **When** Blue Hat runs, **Then** Blue Hat still emits an event (using whatever error context is available), followed by the `done` event.

---

### User Story 4 — Existing Batch Endpoint Unchanged (Priority: P1)

`POST /analyze` continues to work exactly as before — same input, same output, same behaviour — after the streaming endpoint is added.

**Why this priority**: Non-regression. Any breakage here is a critical bug.

**Independent Test**: Run the existing test suite for `POST /analyze`. All tests pass without modification.

**Acceptance Scenarios**:

1. **Given** the streaming endpoint has been added, **When** `POST /analyze` is called with a valid problem, **Then** it returns the same `SixHatsResponse` as before — all 6 analyses, a summary, HTTP 200.
2. **Given** `POST /analyze` is called with an empty problem, **Then** HTTP 422 is returned as before.

---

### Edge Cases

- What if the client disconnects mid-stream? → The server detects the disconnected client and stops generating events; no error is raised server-side.
- What if Blue Hat fails? → Its event is emitted with `error: true`; the `done` event is still sent with `summary` set to the error message.
- What if `context` is omitted? → Defaults to empty string, same as batch endpoint.
- What if the stream produces events out of order for the parallel hats? → Order of the first 5 events is not guaranteed; only Blue Hat and `done` are guaranteed to be last (in that order).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose a `POST /analyze/stream` endpoint accepting the same `ProblemInput` as `POST /analyze`.
- **FR-002**: `POST /analyze/stream` MUST reject empty or whitespace-only `problem` with HTTP 422 before opening the stream.
- **FR-003**: The response MUST use `Content-Type: text/event-stream`.
- **FR-004**: Each of the six hat analyses MUST be emitted as a separate SSE event in the format `data: <JSON>\n\n`.
- **FR-005**: The five parallel hats (White, Red, Black, Yellow, Green) MUST run concurrently; each result MUST be emitted immediately upon completion without waiting for the others.
- **FR-006**: The Blue Hat MUST only run after all five parallel hats have completed; its result MUST be emitted as the sixth event.
- **FR-007**: After the Blue Hat event, a final `event: done\ndata: {"summary": "<blue hat response>"}\n\n` MUST be emitted to signal stream completion.
- **FR-008**: If a hat agent fails, its event MUST be emitted with `"error": true` and the stream MUST continue with remaining hats.
- **FR-009**: `POST /analyze` (batch endpoint) MUST remain completely unchanged in behaviour and contract.
- **FR-010**: The stream MUST close cleanly after the `done` event.

### Key Entities

- **`StreamEvent`**: A single SSE message. Contains either a `HatAnalysis` payload (for hat events) or a `{"summary": "..."}` payload (for the `done` event).
- **`ProblemInput`**: Reused from existing models — no changes.
- **`HatAnalysis`**: Reused from existing models — no changes.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The first hat result is received by the client before all 6 hats have completed — confirmed in streaming tests.
- **SC-002**: Exactly 7 SSE events are emitted per valid request: 6 hat events + 1 `done` event.
- **SC-003**: An invalid problem is rejected in 100% of cases before any streaming begins.
- **SC-004**: A single hat failure never prevents the remaining 5 hats' results from being streamed.
- **SC-005**: All existing `POST /analyze` tests continue to pass without modification after this feature is added.
- **SC-006**: The stream closes within 1 second of the Blue Hat completing.

## Assumptions

- Clients are responsible for parsing SSE events; no client-side library is provided.
- Authentication/authorisation is out of scope (same as the batch endpoint).
- The `done` event's `summary` field duplicates the Blue Hat's `response` — no additional aggregation is performed.
- Event ordering for the 5 parallel hats is non-deterministic; clients must not rely on a fixed order for those events.
- No reconnection / `Last-Event-ID` support is required in this version.
- The streaming endpoint shares the same Ollama configuration (`OLLAMA_URL`, `OLLAMA_MODEL`) as the batch endpoint.
