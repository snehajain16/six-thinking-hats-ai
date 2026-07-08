# API Contracts: Six Thinking Hats AI

**Feature**: specs/001-core-hardening
**Date**: 2026-07-08

---

## `POST /analyze`

**Purpose**: Submit a problem for six-hat multi-agent analysis.

### Request

```
POST /analyze
Content-Type: application/json
```

```json
{
  "problem": "Should we migrate our monolith to microservices?",
  "context": "10 engineers, 50k DAU, Python stack."
}
```

| Field | Type | Required | Constraints |
|---|---|---|---|
| `problem` | string | Yes | Non-empty, non-whitespace |
| `context` | string | No | Free-form; defaults to `""` |

### Response — 200 OK

```json
{
  "problem": "Should we migrate our monolith to microservices?",
  "analyses": [
    {
      "hat": "White Hat",
      "color": "white",
      "perspective": "Facts & Information",
      "response": "Current architecture handles 50k DAU...",
      "error": false
    },
    {
      "hat": "Red Hat",
      "color": "red",
      "perspective": "Emotions & Intuition",
      "response": "The team feels overwhelmed by the idea...",
      "error": false
    },
    {
      "hat": "Black Hat",
      "color": "black",
      "perspective": "Critical Judgment",
      "response": "Risk of increased operational complexity...",
      "error": false
    },
    {
      "hat": "Yellow Hat",
      "color": "yellow",
      "perspective": "Optimism & Benefits",
      "response": "Independent deployments would speed up releases...",
      "error": false
    },
    {
      "hat": "Green Hat",
      "color": "green",
      "perspective": "Creativity & Ideas",
      "response": "Consider a strangler-fig pattern instead...",
      "error": false
    },
    {
      "hat": "Blue Hat",
      "color": "blue",
      "perspective": "Process Control",
      "response": "Based on all perspectives, a phased migration...",
      "error": false
    }
  ],
  "summary": "Based on all perspectives, a phased migration..."
}
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

### Response — 500 Internal Server Error (Ollama unavailable)

```json
{
  "detail": "Ollama connection failed: Connection refused"
}
```

---

## `GET /health`

**Purpose**: Liveness check — confirms the API process is running.

### Response — 200 OK

```json
{ "status": "ok" }
```

> Note: This endpoint always returns 200 as long as the API process is alive. It does NOT reflect Ollama availability.

---

## Hat Order Guarantee

The `analyses` array always contains exactly 6 items in this order:

| Index | Hat | Color |
|---|---|---|
| 0 | White Hat | white |
| 1 | Red Hat | red |
| 2 | Black Hat | black |
| 3 | Yellow Hat | yellow |
| 4 | Green Hat | green |
| 5 | Blue Hat | blue |

---

## Partial Failure Contract

If one or more hat agents fail (Ollama timeout, malformed response, etc.):

- The response still returns HTTP 200
- The failed hat's `HatAnalysis` has `"error": true` and `response` contains the error description
- All other hats' results are unaffected
- Blue Hat still runs using whatever context was successfully gathered
