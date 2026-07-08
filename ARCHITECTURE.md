# Architecture

## Overview

Six Thinking Hats AI is a **multi-agent pipeline** where each agent is a stateless async function. The system has three layers:

```
┌─────────────────────────────────┐
│         FastAPI (main.py)       │  ← HTTP interface
└────────────────┬────────────────┘
                 │
┌────────────────▼────────────────┐
│       Controller (controller.py)│  ← Orchestration
└────────────────┬────────────────┘
                 │
┌────────────────▼────────────────┐
│    Hat Agents (agents/)         │  ← LLM reasoning
└────────────────┬────────────────┘
                 │
┌────────────────▼────────────────┐
│          Ollama (local LLM)     │  ← Inference
└─────────────────────────────────┘
```

---

## Layer Details

### 1. API Layer (`main.py`)

- FastAPI application with two routes: `POST /analyze` and `GET /health`.
- Validates input with Pydantic; delegates to the controller.
- Returns a fully-typed `SixHatsResponse` JSON object.

### 2. Controller (`controller.py`)

Responsible for:
1. Launching White, Red, Black, Yellow, and Green hat agents **concurrently** using `asyncio.gather`.
2. Collecting all five `HatAnalysis` results.
3. Feeding the aggregated text to the Blue Hat agent as context.
4. Assembling and returning `SixHatsResponse`.

The controller is the only place that knows about execution order. Agents know nothing about each other.

### 3. Agent Layer (`agents/`)

`BaseHatAgent` (abstract):
- Holds `hat`, `color`, `perspective`, and `system_prompt` class attributes.
- Exposes a single async method: `analyze(problem, context) -> HatAnalysis`.
- Calls Ollama's `/api/chat` endpoint via `httpx.AsyncClient`.

Each concrete hat class (`WhiteHatAgent`, etc.) only overrides the class-level attributes — no custom logic.

### 4. Data Models (`models.py`)

```
ProblemInput
  problem: str
  context: str | None

HatAnalysis
  hat: str          # "White Hat"
  color: str        # "white"
  perspective: str  # "Facts & Information"
  response: str     # LLM output

SixHatsResponse
  problem: str
  analyses: list[HatAnalysis]   # always 6 items
  summary: str                  # Blue Hat's response
```

---

## Concurrency Model

```
t=0  ──► White Hat ──────────────────────────────► done ─┐
t=0  ──► Red Hat   ───────────────────────────► done ─────┤
t=0  ──► Black Hat ──────────────────────────────► done ──┤ asyncio.gather
t=0  ──► Yellow Hat ─────────────────────────────► done ──┤
t=0  ──► Green Hat ───────────────────────────────► done ─┘
                                                          │
                                                          ▼
                                                    Blue Hat ──► SixHatsResponse
```

The slowest of the five parallel agents determines the wall-clock time before Blue Hat starts.

---

## External Dependency: Ollama

- All inference is local; no external API keys required.
- Configured via `OLLAMA_URL` and `OLLAMA_MODEL` environment variables.
- The `BaseHatAgent._call_ollama` method is the single integration point — swap it out to support any OpenAI-compatible endpoint.

---

## Future: Streaming (Issue #4)

The `POST /analyze/stream` endpoint will use Server-Sent Events. Blue Hat still waits for all other hats; individual hat results are streamed to the client as they complete rather than waiting for all six.

---

## Decisions Log

| Decision | Rationale |
|---|---|
| `asyncio.gather` over threads | Agents are I/O-bound (HTTP to Ollama); async is lighter than thread-per-agent |
| Blue Hat runs last, sequentially | It needs the other five outputs as context to synthesise meaningfully |
| `httpx.AsyncClient` per request | Avoids shared connection-pool state across concurrent requests |
| Pydantic v2 models | Automatic validation + OpenAPI schema generation via FastAPI |
