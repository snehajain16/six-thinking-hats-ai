# Implementation Plan: Streaming SSE Endpoint

**Branch**: `feature/issue-4-streaming` | **Date**: 2026-07-08 | **Spec**: [spec.md](spec.md)

**Closes**: #4

## Summary

Add `POST /analyze/stream` — a Server-Sent Events endpoint that streams each hat's result to the client as soon as it completes, using `asyncio.as_completed` for the five parallel hats. Blue Hat runs after all five and is the sixth event; a final `done` event closes the stream. Zero changes to the existing batch endpoint or any models.

## Technical Context

**Language/Version**: Python 3.11

**Primary Dependencies**: FastAPI `StreamingResponse`, `asyncio.as_completed` (stdlib) — no new packages

**Storage**: N/A

**Testing**: pytest + pytest-asyncio; `TestClient(stream=True)` to collect SSE chunks

**Target Platform**: Linux server

**Project Type**: Web service — new route on existing FastAPI app

**Performance Goals**: First event reaches client before all 6 hats complete

**Constraints**: Blue Hat always event 6; `done` always event 7; `POST /analyze` untouched

## Constitution Check

| Principle | Status | Notes |
|---|---|---|
| I. Spec-First | ✅ | spec.md written and validated |
| II. Agent Isolation | ✅ | No agent changes; `stream_analysis` is new in controller |
| III. Local-First Inference | ✅ | Same Ollama config reused |
| IV. Async-First Concurrency | ✅ | `asyncio.as_completed` for parallel hats |
| V. Typed Contracts | ✅ | Reuses `ProblemInput`, `HatAnalysis` |
| VI. Test-Driven Quality Gate | ✅ | `tests/test_stream.py` required before merge |

## Project Structure

### Documentation

```text
specs/002-streaming-sse/
├── plan.md, spec.md, research.md, data-model.md, quickstart.md
├── contracts/api.md
└── tasks.md
```

### Source Code Changes

```text
controller.py      ← add stream_analysis() async generator
main.py            ← add POST /analyze/stream route
tests/
└── test_stream.py ← new streaming test file
```

No changes to: `models.py`, `agents/`, `logging_config.py`, existing tests.

## Implementation Design

### `controller.py` — `stream_analysis()` async generator

- Use `asyncio.as_completed` over 5 parallel hat coroutines
- Yield each completed `HatAnalysis` as `data: <JSON>\n\n` immediately
- After all 5, run Blue Hat with aggregated context (reuse `build_aggregated_context` logic)
- Yield Blue Hat event, then yield `event: done\ndata: {"summary": "..."}\n\n`

### `main.py` — new route

- `POST /analyze/stream` returns `StreamingResponse(stream_analysis(...), media_type="text/event-stream")`
- FastAPI validates `ProblemInput` before generator starts — invalid input auto-422s

### `tests/test_stream.py`

- Happy path: collect all chunks, assert 7 events, all 6 hat names, `done` has `summary`
- Validation: empty problem → 422 (no stream)
- Partial failure: one hat raises → `error: true` on that event, stream completes normally
- Non-regression: existing `POST /analyze` tests still pass (run them as part of this branch)

**Note**: This template is filled in by the `/speckit-plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

[Extract from feature spec: primary requirement + technical approach from research]

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: [e.g., Python 3.11, Swift 5.9, Rust 1.75 or NEEDS CLARIFICATION]

**Primary Dependencies**: [e.g., FastAPI, UIKit, LLVM or NEEDS CLARIFICATION]

**Storage**: [if applicable, e.g., PostgreSQL, CoreData, files or N/A]

**Testing**: [e.g., pytest, XCTest, cargo test or NEEDS CLARIFICATION]

**Target Platform**: [e.g., Linux server, iOS 15+, WASM or NEEDS CLARIFICATION]

**Project Type**: [e.g., library/cli/web-service/mobile-app/compiler/desktop-app or NEEDS CLARIFICATION]

**Performance Goals**: [domain-specific, e.g., 1000 req/s, 10k lines/sec, 60 fps or NEEDS CLARIFICATION]

**Constraints**: [domain-specific, e.g., <200ms p95, <100MB memory, offline-capable or NEEDS CLARIFICATION]

**Scale/Scope**: [domain-specific, e.g., 10k users, 1M LOC, 50 screens or NEEDS CLARIFICATION]

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

[Gates determined based on constitution file]

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
# [REMOVE IF UNUSED] Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# [REMOVE IF UNUSED] Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# [REMOVE IF UNUSED] Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure: feature modules, UI flows, platform tests]
```

**Structure Decision**: [Document the selected structure and reference the real
directories captured above]

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
