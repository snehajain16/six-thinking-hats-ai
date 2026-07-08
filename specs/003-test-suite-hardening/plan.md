# Implementation Plan: Test Suite Hardening

**Branch**: `feature/issue-5-test-suite` | **Date**: 2026-07-08 | **Spec**: [spec.md](spec.md)

**Closes**: #5

## Summary

Add missing unit-test assertions (LLM call count, `ProblemInput` context default) and wire up the `@pytest.mark.integration` infrastructure so future live-model tests skip automatically in unit-only CI runs. Zero changes to existing passing tests.

## Technical Context

**Language/Version**: Python 3.11

**Primary Dependencies**: pytest, pytest-asyncio, unittest.mock (stdlib) — no new packages

**Storage**: N/A

**Testing**: pytest + pytest-asyncio; `AsyncMock` for mocking `_call_ollama`

**Target Platform**: Linux (CI + developer workstation)

**Project Type**: Test quality improvement — no production code changes

**Performance Goals**: N/A

**Constraints**: Must not break any of the 30 currently passing tests

**Scale/Scope**: 5 new test assertions + marker infrastructure across existing test files

## Constitution Check

| Principle | Status | Notes |
|---|---|---|
| I. Spec-First | ✅ | spec.md written and validated |
| II. Agent Isolation | ✅ | No agent code changes |
| III. Local-First Inference | ✅ | All tests mock Ollama |
| IV. Async-First Concurrency | ✅ | Async tests use pytest-asyncio |
| V. Typed Contracts | ✅ | ProblemInput model tested |
| VI. Test-Driven Quality Gate | ✅ | This feature IS the quality gate improvement |

## Project Structure

### Source Code Changes

```text
tests/
  conftest.py        ← add integration marker skip hook
  test_agents.py     ← verify system_prompt contains full hat name (already passing; confirm)
  test_controller.py ← add call-count assertion
  test_api.py        ← add ProblemInput context-default test
pytest.ini           ← register integration marker (new file)
```

No changes to: `models.py`, `agents/`, `controller.py`, `main.py`, `logging_config.py`.

## Implementation Design

### Phase 0: Research (resolved)

- **FR-001 (system_prompt)**: `test_agent_attributes` already checks `system_prompt.strip()` non-empty and that `name.split()[0]` appears (e.g. `"White"` in `"White Hat"`). The full hat name (e.g. `"White Hat"`) check is not yet explicit — add a parametrized assertion to be safe.
- **FR-002 (call count)**: Add `assert mock_ollama.call_count == 6` after `run_analysis`. The mock is set up in `conftest.py` with `AsyncMock`; `call_count` tracks invocations.
- **FR-003/FR-004**: Already covered by `test_run_analysis_returns_six_analyses` and `test_summary_equals_blue_hat_response`. No change needed.
- **FR-005 (context default)**: Add a model-level test: `ProblemInput(problem="x")` → `context is None`.
- **FR-006/FR-007 (integration marker)**: Register marker in `pytest.ini`; add `pytest_collection_modifyitems` hook in `conftest.py` that skips `integration`-marked tests when `os.getenv("OLLAMA_URL", "").strip()` is falsy.

### `pytest.ini`

```ini
[pytest]
asyncio_mode = strict
markers =
    integration: marks tests as requiring a live Ollama instance (deselect with -m "not integration")
```

### `conftest.py` addition

```python
import os

def pytest_collection_modifyitems(config, items):
    if os.getenv("OLLAMA_URL", "").strip():
        return
    skip = pytest.mark.skip(reason="OLLAMA_URL not set — live Ollama required")
    for item in items:
        if item.get_closest_marker("integration"):
            item.add_marker(skip)
```

### `test_controller.py` addition

```python
@pytest.mark.asyncio
async def test_run_analysis_calls_ollama_six_times(mock_ollama):
    await run_analysis("Any problem")
    assert mock_ollama.call_count == 6
```

### `test_api.py` addition

```python
def test_problem_input_context_defaults_to_none():
    from models import ProblemInput
    p = ProblemInput(problem="Test")
    assert p.context is None
```
