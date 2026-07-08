# Contributing

## Development Philosophy

This project uses **GitHub SpecKit**: every feature begins as a GitHub Issue spec before any code is written. The spec defines acceptance criteria, API contracts, and technical notes. Implementation happens on a dedicated branch and merges back to `main` via PR.

---

## Branch Strategy

```
main                   ← stable, always deployable
  └── feature/issue-1-core-pipeline
  └── feature/issue-2-fastapi-endpoint
  └── feature/issue-3-ollama-config
  └── feature/issue-4-streaming
  └── feature/issue-5-tests
  └── feature/issue-6-docker
```

**Rules:**
- Branch off `main` for every feature.
- Name branches `feature/issue-<N>-<short-description>`.
- Never commit directly to `main`.
- Each PR must close exactly one spec issue (use `Closes #N` in the PR body).

---

## Workflow

```
1. Pick a spec issue (start with lowest open number)
2. git checkout main && git pull origin main
3. git checkout -b feature/issue-N-description
4. Implement until all acceptance criteria are checked off
5. Run tests: pytest
6. Push and open PR → main
7. PR is reviewed, CI passes, then merged
```

---

## Commit Convention

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add Blue Hat agent system prompt
fix: handle Ollama connection timeout gracefully
test: add controller unit tests with mocked Ollama
docs: update README quickstart section
chore: add Dockerfile
```

---

## Running Tests

```bash
pip install -r requirements-dev.txt
pytest                          # unit tests only
pytest -m integration           # requires live Ollama
pytest --cov=. --cov-report=term-missing
```

---

## Environment Setup

```bash
cp .env.example .env
# Edit .env: set OLLAMA_URL and OLLAMA_MODEL
pip install -r requirements.txt
uvicorn main:app --reload
```

---

## Code Style

- **Formatter:** `black`
- **Linter:** `ruff`
- **Type hints:** required on all public functions
- No comments unless the *why* is non-obvious

```bash
black .
ruff check .
```

---

## Opening a New Spec Issue

Use the **Spec** issue template. Fill in:
- Overview
- Acceptance Criteria (checkboxes)
- Technical Notes
- Dependencies (blocked by / blocks)
