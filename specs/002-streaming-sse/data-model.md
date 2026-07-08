# Data Model: Streaming SSE Endpoint

**Feature**: specs/002-streaming-sse
**Date**: 2026-07-08

---

## Reused Entities (no changes)

- **`ProblemInput`** — same validation as batch endpoint
- **`HatAnalysis`** — same fields including `error: bool`

## New Entity

### `DoneEvent` (SSE terminal payload)

| Field | Type | Notes |
|---|---|---|
| `summary` | `str` | Blue Hat's `response` value |

Not a Pydantic model — serialised inline as `{"summary": "..."}`.

---

## SSE Stream Structure

```
POST /analyze/stream
        │
        ▼ (validate ProblemInput — 422 if invalid)
  stream_analysis(problem, context)  [async generator]
        │
        ├── asyncio.as_completed([White, Red, Black, Yellow, Green])
        │       │
        │       └── as each completes →  yield  "data: <HatAnalysis JSON>\n\n"
        │
        ├── BlueHatAgent.analyze(problem, aggregated_context)
        │       └──  yield  "data: <HatAnalysis JSON>\n\n"
        │
        └──  yield  "event: done\ndata: {\"summary\": \"...\"}\n\n"
             (stream closes)
```

---

## SSE Event Schemas

### Hat Event (×6)

```
data: {"hat":"White Hat","color":"white","perspective":"Facts & Information","response":"...","error":false}

```

### Done Event (×1, always last)

```
event: done
data: {"summary":"..."}

```

Total events per request: **7** (6 hat + 1 done)

---

## Event Ordering Guarantee

| Position | Event | Guaranteed? |
|---|---|---|
| 1–5 | White/Red/Black/Yellow/Green | Order not guaranteed (first-to-finish) |
| 6 | Blue Hat | Always 6th |
| 7 | `done` | Always last |
