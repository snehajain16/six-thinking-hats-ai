# Six Thinking Hats AI

A multi-agent reasoning system based on Edward de Bono's **Six Thinking Hats** framework, powered by local LLMs via [Ollama](https://ollama.com) and exposed through a **FastAPI** REST API.

## Architecture

```
POST /analyze
     │
     ▼
 Controller
     │
     ├── WhiteHatAgent  (facts)        ─┐
     ├── RedHatAgent    (emotions)      │  parallel
     ├── BlackHatAgent  (risks)         │  Ollama calls
     ├── YellowHatAgent (optimism)      │
     └── GreenHatAgent  (creativity)   ─┘
                                        │
                                        ▼
                                  BlueHatAgent
                              (synthesis & summary)
```

## Quickstart

```bash
# 1. Start Ollama and pull a model
ollama pull llama3

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the API
uvicorn main:app --reload
```

## API

### `POST /analyze`

```json
{
  "problem": "Should we migrate our monolith to microservices?",
  "context": "We have 10 engineers and 50k daily active users."
}
```

Returns a `SixHatsResponse` with individual hat analyses and a Blue Hat summary.

## Configuration

| Env var | Default | Description |
|---|---|---|
| `OLLAMA_URL` | `http://localhost:11434` | Ollama base URL |
| `OLLAMA_MODEL` | `llama3` | Model to use |
