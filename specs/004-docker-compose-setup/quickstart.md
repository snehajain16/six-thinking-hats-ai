# Quickstart Validation Guide: Docker & Docker Compose Setup

**Feature**: specs/004-docker-compose-setup
**Date**: 2026-07-08

---

## Prerequisites

- Docker Engine 24+ with Compose V2 plugin installed
- Internet access (to pull `ollama/ollama` image and the LLM model)
- Ports 8000 and 11434 free on the host

---

## Scenario 1: First-Time Startup

```bash
docker compose up --build
```

**Expected**:
- Ollama container starts and passes its health check
- API container starts, waits for Ollama, pulls `llama3`, then starts uvicorn
- Within ~30 seconds (after model is pulled): `GET http://localhost:8000/health` returns `{"status":"ok"}`

Verify health:
```bash
curl http://localhost:8000/health
```

---

## Scenario 2: Model Persists on Restart

```bash
docker compose down
docker compose up
```

**Expected**: Ollama does not re-download `llama3` — second startup is significantly faster than the first.

---

## Scenario 3: Custom Model via Environment Variable

```bash
OLLAMA_MODEL=mistral docker compose up --build
```

**Expected**: API logs show `Pulling model: mistral`; analysis requests use Mistral.

---

## Scenario 4: No Secrets in Image

```bash
docker compose build api
docker run --rm six-thinking-hats-ai-api find / -name ".env" 2>/dev/null
```

**Expected**: No `.env` files found inside the image.

---

## Scenario 5: Full Analysis Still Works

```bash
curl -s -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"problem": "Should we adopt a four-day work week?"}' | python -m json.tool
```

**Expected**: JSON response with 6 `analyses` and a `summary`.

---

## Scenario 6: Existing Tests Still Pass (No Docker Required)

```bash
python -m pytest tests/ -v
```

**Expected**: 32/32 tests pass — Docker changes do not affect the unit test suite.
