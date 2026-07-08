# Quickstart Validation Guide: Core Hardening

**Feature**: specs/001-core-hardening
**Date**: 2026-07-08

Use this guide to validate the hardened implementation end-to-end.

---

## Prerequisites

- Python 3.11+
- Ollama running with `llama3` model pulled (`ollama pull llama3`)
- Dependencies installed: `pip install -r requirements.txt`

---

## Scenario 1: Happy Path — Full Six-Hat Analysis

```bash
uvicorn main:app --reload
```

```bash
curl -s -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"problem": "Should we adopt a four-day work week?", "context": "50-person tech company."}' \
  | python -m json.tool
```

**Expected**: HTTP 200, `analyses` array with 6 items, all `"error": false`, non-empty `summary`.

---

## Scenario 2: Input Validation — Empty Problem

```bash
curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"problem": ""}'
```

**Expected**: `422`

```bash
curl -s -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"problem": "   "}'
```

**Expected**: HTTP 422 with `"msg"` describing the empty problem error.

---

## Scenario 3: Health Check

```bash
curl -s http://localhost:8000/health
```

**Expected**: `{"status":"ok"}` with HTTP 200.

---

## Scenario 4: Startup Warning When Ollama Is Down

```bash
OLLAMA_URL=http://localhost:19999 uvicorn main:app
```

**Expected**: App starts. Logs contain a `WARNING` line mentioning Ollama connectivity. `GET /health` still returns 200.

---

## Scenario 5: Graceful Degradation — One Hat Fails

*(Requires mocking or a test; use the test suite for this scenario.)*

Run:
```bash
pytest tests/test_controller.py -k "partial_failure" -v
```

**Expected**: Test passes — `SixHatsResponse` returned with one `HatAnalysis` having `error=True`.

---

## Scenario 6: Custom Model via Env Var

```bash
OLLAMA_MODEL=mistral uvicorn main:app --reload
```

Then run Scenario 1 and check Ollama logs — should show `mistral` model being called.

---

## Log Output Validation

For any scenario above, logs should include structured entries like:

```
INFO  request_received  method=POST path=/analyze
INFO  hat_call_start    hat="White Hat" model=llama3
INFO  hat_call_done     hat="White Hat" model=llama3 duration_ms=3421 error=false
...
INFO  request_done      path=/analyze duration_ms=8732 hats_failed=0
```

---

## API Docs

Open [http://localhost:8000/docs](http://localhost:8000/docs) — all endpoints, schemas, and examples should be accurately documented.
