# Quickstart Validation Guide: Streaming SSE Endpoint

**Feature**: specs/002-streaming-sse
**Date**: 2026-07-08

---

## Prerequisites

- API running: `uvicorn main:app --reload`
- Ollama running with `llama3` pulled (or use mock for tests)

---

## Scenario 1: Happy Path — See Events Arrive in Real Time

```bash
curl -N -X POST http://localhost:8000/analyze/stream \
  -H "Content-Type: application/json" \
  -d '{"problem": "Should we move to a remote-first culture?", "context": "200-person company."}'
```

**Expected**: Events appear one by one as each hat finishes. The stream ends with:
```
event: done
data: {"summary":"..."}
```
Total: 7 events.

---

## Scenario 2: Input Validation — Empty Problem

```bash
curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:8000/analyze/stream \
  -H "Content-Type: application/json" \
  -d '{"problem": ""}'
```

**Expected**: `422` — no stream is opened.

---

## Scenario 3: Batch Endpoint Still Works

```bash
curl -s -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"problem": "Should we adopt microservices?"}' | python -m json.tool
```

**Expected**: Same `SixHatsResponse` as before — 6 analyses, `summary`, HTTP 200.

---

## Scenario 4: Graceful Degradation Mid-Stream (via test)

```bash
python -m pytest tests/test_stream.py -v
```

**Expected**: All streaming tests pass including partial-failure scenario.

---

## Scenario 5: Verify Event Count

```bash
curl -N -s -X POST http://localhost:8000/analyze/stream \
  -H "Content-Type: application/json" \
  -d '{"problem": "Test problem"}' | grep -c "^data:"
```

**Expected**: `7` (6 hat data lines + 1 done data line).
