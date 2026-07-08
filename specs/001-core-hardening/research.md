# Research: Core Hardening — Multi-Agent Pipeline, API & Ollama Integration

**Feature**: specs/001-core-hardening
**Date**: 2026-07-08

---

## Decision 1: Graceful Degradation Strategy for Failed Hat Agents

**Decision**: Per-hat try/except in `BaseHatAgent.analyze()`. On any exception, return a `HatAnalysis` with `error=True` and the exception message as `response`. The controller collects results regardless.

**Rationale**: `asyncio.gather(return_exceptions=True)` returns exceptions as values rather than raising. Each exception is then converted to an error `HatAnalysis` in the controller, keeping the pipeline intact.

**Alternatives considered**:
- Fail-fast (raise on first error) — rejected: loses all other hats' valid output
- Retry with backoff — rejected: out of scope for this hardening pass; adds latency unpredictably

---

## Decision 2: Startup Ollama Connectivity Check

**Decision**: Use a FastAPI `lifespan` context manager (not deprecated `@app.on_event`). On startup, send a lightweight `GET /api/tags` probe to Ollama. Log `INFO` on success, `WARNING` on failure. Never raise; let the app start.

**Rationale**: `GET /api/tags` is Ollama's model-list endpoint — a cheap, side-effect-free probe. `lifespan` is the FastAPI-recommended approach since v0.93.

**Alternatives considered**:
- `GET /` on Ollama — returns HTML, harder to detect failure cleanly
- Probe on first `/analyze` call — defers the warning until first real use, too late for operator awareness

---

## Decision 3: Structured Logging

**Decision**: Python's stdlib `logging` with a `JSONFormatter`-style output using `logging.config.dictConfig`. Log at `INFO` for normal requests and Ollama calls; `WARNING` for connectivity issues; `ERROR` for unhandled exceptions.

**Rationale**: Zero additional dependencies; structured JSON on stdout integrates with any log aggregator (Datadog, CloudWatch, GCP Logging). Each log record includes: `timestamp`, `level`, `hat` (where applicable), `model`, `duration_ms`, `status`.

**Alternatives considered**:
- `loguru` — cleaner API but adds a dependency; stdlib is sufficient here
- `structlog` — excellent for production but adds complexity; can migrate later

---

## Decision 4: Input Validation for Empty/Whitespace `problem`

**Decision**: Add a Pydantic `field_validator` on `ProblemInput.problem` that strips whitespace and raises `ValueError` if the result is empty. FastAPI converts `ValueError` from validators to HTTP 422 automatically.

**Rationale**: Pydantic v2 validators are the canonical FastAPI input validation mechanism. No custom exception handlers needed.

**Alternatives considered**:
- `min_length=1` constraint — doesn't catch whitespace-only strings like `"   "`
- Manual check in route handler — bypasses FastAPI's validation layer, duplicates logic

---

## Decision 5: Ollama HTTP Timeout

**Decision**: 120-second timeout on `httpx.AsyncClient`, set at the `connect` and `read` level separately: `httpx.Timeout(connect=5.0, read=120.0, write=5.0, pool=5.0)`.

**Rationale**: Connect timeout of 5s catches a down Ollama quickly. Read timeout of 120s allows large models time to generate. Separating these prevents a slow generation from being confused with a connection failure.

**Alternatives considered**:
- Single unified 120s timeout — masks slow connections as generation delays
- No timeout — risks indefinitely hung requests
