# API Contract: Streaming SSE Endpoint

**Feature**: specs/002-streaming-sse
**Date**: 2026-07-08

---

## `POST /analyze/stream`

**Purpose**: Submit a problem for six-hat analysis; receive results as a real-time stream.

### Request

```
POST /analyze/stream
Content-Type: application/json
```

```json
{
  "problem": "Should we adopt a four-day work week?",
  "context": "50-person tech company."
}
```

| Field | Type | Required | Constraints |
|---|---|---|---|
| `problem` | string | Yes | Non-empty, non-whitespace |
| `context` | string | No | Free-form; defaults to `""` |

### Response — 200 OK (SSE stream)

```
Content-Type: text/event-stream
Transfer-Encoding: chunked
```

**Hat events** (6 total, first 5 in non-deterministic order):

```
data: {"hat":"White Hat","color":"white","perspective":"Facts & Information","response":"...","error":false}

data: {"hat":"Green Hat","color":"green","perspective":"Creativity & Ideas","response":"...","error":false}

data: {"hat":"Red Hat","color":"red","perspective":"Emotions & Intuition","response":"...","error":false}

data: {"hat":"Black Hat","color":"black","perspective":"Critical Judgment","response":"...","error":false}

data: {"hat":"Yellow Hat","color":"yellow","perspective":"Optimism & Benefits","response":"...","error":false}

data: {"hat":"Blue Hat","color":"blue","perspective":"Process Control","response":"...","error":false}

event: done
data: {"summary":"Based on all perspectives..."}

```

### Response — 422 Unprocessable Entity (invalid input)

```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "problem"],
      "msg": "Value error, problem must not be empty",
      "input": ""
    }
  ]
}
```

---

## Event Format Specification

### Hat Data Event

```
data: <JSON>\n\n
```

Where `<JSON>` is a serialised `HatAnalysis` object:

```json
{
  "hat": "White Hat",
  "color": "white",
  "perspective": "Facts & Information",
  "response": "...",
  "error": false
}
```

On failure, `error` is `true` and `response` contains the error description.

### Done Event

```
event: done\n
data: {"summary": "<blue hat response>"}\n\n
```

Signals end of stream. Clients should stop reading after this event.

---

## Ordering Contract

- Events 1–5: The five parallel hats in **non-deterministic** order (first-complete-first-out)
- Event 6: Always Blue Hat
- Event 7: Always `done`

---

## Unchanged Endpoint

`POST /analyze` remains identical. See `specs/001-core-hardening/contracts/api.md`.
