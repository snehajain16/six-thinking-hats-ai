# Research: Streaming SSE Endpoint

**Feature**: specs/002-streaming-sse
**Date**: 2026-07-08

---

## Decision 1: SSE Implementation Pattern in FastAPI

**Decision**: Use `fastapi.responses.StreamingResponse` with `media_type="text/event-stream"` and an async generator function that yields formatted SSE strings.

**Rationale**: FastAPI's `StreamingResponse` is the canonical way to stream data. An async generator naturally models the "yield one event, pause, yield next" pattern without threads or queues. No additional libraries needed.

**Alternatives considered**:
- `sse-starlette` package — cleaner API but adds a dependency; stdlib approach is sufficient
- WebSockets — overkill for one-directional server push; SSE is simpler and HTTP-native

---

## Decision 2: Streaming the Five Parallel Hats as They Complete

**Decision**: Use `asyncio.as_completed()` over the five parallel hat coroutines. This yields each future as it resolves, so we can emit the SSE event immediately without waiting for all five.

**Rationale**: `asyncio.gather` waits for *all* tasks; `asyncio.as_completed` yields each one as it finishes — exactly the semantics we need. Each completed result is immediately formatted and yielded into the SSE stream.

**Alternatives considered**:
- `asyncio.Queue` with producers/consumer — more complex; `as_completed` is simpler and sufficient
- Sequential hat calls — defeats the purpose; latency would be 6× a single call

---

## Decision 3: SSE Event Format

**Decision**:
- Hat events: `data: <JSON HatAnalysis>\n\n`
- Done event: `event: done\ndata: {"summary": "<blue_response>"}\n\n`

**Rationale**: Standard SSE format. The `event:` field on the done event lets clients distinguish it from hat data events without parsing the JSON body. Named events are a core SSE feature.

**Alternatives considered**:
- Include `id:` field per event — not required; no reconnect support in scope
- Use `event: hat` on every hat event — unnecessary; unnamed `data:` events are the default

---

## Decision 4: Validation Before Stream Opens

**Decision**: Validate `ProblemInput` using the existing Pydantic model at the route level. FastAPI automatically returns HTTP 422 before the async generator is even called if validation fails.

**Rationale**: FastAPI runs model validation synchronously before entering the route handler. The streaming generator never starts if the body is invalid — clean separation, no special handling needed.

---

## Decision 5: Non-Regression — Batch Endpoint Unchanged

**Decision**: The streaming endpoint is a new route (`POST /analyze/stream`) added to `main.py`. It shares `ProblemInput`, `HatAnalysis`, and `SixHatsResponse` models but has its own streaming controller function `stream_analysis()` in `controller.py`. Zero changes to `run_analysis()` or the `/analyze` route.

**Rationale**: Keeps concerns separated; existing tests remain valid without modification.
