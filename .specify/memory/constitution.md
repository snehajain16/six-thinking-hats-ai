# Six Thinking Hats AI — Constitution

## Core Principles

### I. Spec-First (NON-NEGOTIABLE)
Every feature begins as a GitHub Issue using the Spec template. No code is written until the spec exists, acceptance criteria are defined, and the issue is open. The spec is the single source of truth.

### II. Agent Isolation
Each hat agent (`WhiteHatAgent`, `RedHatAgent`, etc.) is a self-contained, independently testable unit. Agents know nothing about each other — only the controller orchestrates them. No agent may import another agent.

### III. Local-First Inference
All LLM inference runs locally through Ollama. No external API keys, no cloud LLM calls. Configuration is exclusively via `OLLAMA_URL` and `OLLAMA_MODEL` environment variables. Defaults must work out-of-the-box with `ollama pull llama3`.

### IV. Async-First Concurrency
The five non-Blue hats always run concurrently via `asyncio.gather`. Blocking calls inside agents are forbidden. Blue Hat always runs last, after all other hats complete.

### V. Typed Contracts
All data crossing a layer boundary must be a Pydantic model. No raw dicts passed between controller, agents, and API. FastAPI response models are always explicitly declared.

### VI. Test-Driven Quality Gate
Every feature branch must include tests before it can merge. Unit tests mock `_call_ollama`. Integration tests are marked `@pytest.mark.integration` and require a live Ollama instance. CI runs unit tests only.

## Branch & Workflow Strategy

- `main` — stable, always deployable, protected
- `feature/issue-<N>-<description>` — one branch per spec issue
- Branch off `main`, implement all acceptance criteria, open PR with `Closes #N`
- Merge only when: all checklist items ticked, tests pass, no unresolved review comments

## Technology Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11+ |
| API framework | FastAPI |
| HTTP client | httpx (async) |
| Data models | Pydantic v2 |
| LLM runtime | Ollama (local) |
| Test framework | pytest + pytest-asyncio |
| Formatter | black |
| Linter | ruff |
| Container | Docker + Compose |

## Quality Gates

- `black .` — zero formatting errors
- `ruff check .` — zero lint errors
- `pytest` — all unit tests green
- `GET /health` — returns 200 before any PR merges

## Governance

This constitution supersedes all other development practices. Amendments require an updated version number, ratification date, and a note in the PR description. All PRs must verify compliance with these principles.

**Version**: 1.0.0 | **Ratified**: 2026-07-08 | **Last Amended**: 2026-07-08
