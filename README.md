# 🎩 Six Thinking Hats AI

A **multi-agent reasoning system** based on Edward de Bono's [Six Thinking Hats](https://en.wikipedia.org/wiki/Six_Thinking_Hats) framework. Each "hat" is an independent LLM agent that analyses a problem from a distinct cognitive perspective. Results are synthesised by the Blue Hat into a unified decision output.

Powered by **local LLMs via [Ollama](https://ollama.com)** and exposed through a **FastAPI** REST API.

---

## Architecture

```
POST /analyze
      │
      ▼
  Controller
      │
      ├── ⚪ WhiteHatAgent  (Facts & Data)          ─┐
      ├── 🔴 RedHatAgent    (Emotions & Intuition)   │  parallel
      ├── ⚫ BlackHatAgent  (Risks & Caution)         │  Ollama calls
      ├── 🟡 YellowHatAgent (Optimism & Benefits)     │
      └── 🟢 GreenHatAgent  (Creativity & Ideas)     ─┘
                                                      │
                                                      ▼
                                              🔵 BlueHatAgent
                                          (Synthesis & Next Steps)
```

| Hat | Colour | Mode |
|-----|--------|------|
| White | ⚪ | Neutral facts, data, information gaps |
| Red | 🔴 | Gut feelings, emotions, hunches |
| Black | ⚫ | Risks, problems, critical judgment |
| Yellow | 🟡 | Optimism, value, benefits |
| Green | 🟢 | Creative ideas, lateral thinking |
| Blue | 🔵 | Process control, synthesis, conclusions |

---

## Project Layout

```
six-thinking-hats-ai/
├── agents/
│   ├── __init__.py
│   ├── base.py          # BaseHatAgent — Ollama HTTP client
│   └── hats.py          # Six concrete hat agent classes
├── tests/
│   ├── conftest.py      # Shared fixtures & Ollama mock
│   ├── test_agents.py
│   ├── test_controller.py
│   └── test_api.py
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── spec.md
│   │   └── bug_report.md
│   └── pull_request_template.md
├── controller.py        # Orchestrates parallel hat execution
├── main.py              # FastAPI app & routes
├── models.py            # Pydantic schemas
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── ARCHITECTURE.md
├── CONTRIBUTING.md
└── README.md
```

---

## Quickstart

### Prerequisites
- Python 3.11+
- [Ollama](https://ollama.com) running locally

```bash
# Pull a model (first time only)
ollama pull llama3
```

### Run locally

```bash
git clone https://github.com/snehajain16/six-thinking-hats-ai.git
cd six-thinking-hats-ai

pip install -r requirements.txt

uvicorn main:app --reload
# API available at http://localhost:8000
# Docs at        http://localhost:8000/docs
```

### Run with Docker Compose

```bash
docker compose up --build
```

---

## API Reference

### `POST /analyze`

Submit a problem for six-hat analysis.

**Request**
```json
{
  "problem": "Should we migrate our monolith to microservices?",
  "context": "10 engineers, 50k DAU, Python stack."
}
```

**Response** — `SixHatsResponse`
```json
{
  "problem": "Should we migrate our monolith to microservices?",
  "analyses": [
    {
      "hat": "White Hat",
      "color": "white",
      "perspective": "Facts & Information",
      "response": "Current system handles 50k DAU..."
    },
    ...
  ],
  "summary": "Blue Hat synthesis and recommended next steps..."
}
```

### `POST /analyze/stream` _(planned — Issue #4)_

Same input; returns Server-Sent Events, one per hat as it completes.

### `GET /health`

```json
{ "status": "ok" }
```

---

## Configuration

| Variable | Default | Description |
|---|---|---|
| `OLLAMA_URL` | `http://localhost:11434` | Ollama base URL |
| `OLLAMA_MODEL` | `llama3` | Model name |

Copy `.env.example` to `.env` to override locally.

---

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for branch strategy, commit conventions, and how to run the test suite.

---

## Roadmap

| Issue | Feature | Status |
|-------|---------|--------|
| [#1](https://github.com/snehajain16/six-thinking-hats-ai/issues/1) | Core multi-agent pipeline | ✅ Scaffolded |
| [#2](https://github.com/snehajain16/six-thinking-hats-ai/issues/2) | FastAPI `/analyze` endpoint | ✅ Scaffolded |
| [#3](https://github.com/snehajain16/six-thinking-hats-ai/issues/3) | Ollama integration & config | ✅ Scaffolded |
| [#4](https://github.com/snehajain16/six-thinking-hats-ai/issues/4) | Streaming SSE endpoint | 🔲 Planned |
| [#5](https://github.com/snehajain16/six-thinking-hats-ai/issues/5) | Test suite | 🔲 Planned |
| [#6](https://github.com/snehajain16/six-thinking-hats-ai/issues/6) | Docker & Compose | 🔲 Planned |

---

## License

MIT
