# Research: Test Suite Hardening

**Feature**: specs/003-test-suite-hardening
**Date**: 2026-07-08

## Decision: Call Count Assertion

- **Decision**: Assert `mock_ollama.call_count == 6` after a single `run_analysis` call.
- **Rationale**: `AsyncMock` from `unittest.mock` exposes `call_count` automatically. The existing `mock_ollama` fixture in `conftest.py` already patches `BaseHatAgent._call_ollama`, so no new fixture is needed.
- **Alternatives considered**: Inspecting `mock_ollama.call_args_list` — more verbose, not needed here.

## Decision: Integration Marker Infrastructure

- **Decision**: Register `integration` in `pytest.ini` + `pytest_collection_modifyitems` hook in `conftest.py`.
- **Rationale**: `pytest.ini` is the lightest-weight config file for a pure-pytest project with no `pyproject.toml`. The hook is the standard pytest pattern for conditional skipping based on environment state.
- **Alternatives considered**: `@pytest.fixture(autouse=True)` skip — less idiomatic than the hook; `conftest.py` `pytest_configure` — works but `modifyitems` is cleaner for marker-based gating.

## Decision: asyncio_mode in pytest.ini

- **Decision**: Move `asyncio_mode = strict` from any implicit default into `pytest.ini` explicitly.
- **Rationale**: Avoids the `PytestUnraisableExceptionWarning` that appears when asyncio mode is not declared. The project already uses `Mode.STRICT` (visible in test output).
- **Alternatives considered**: `pyproject.toml [tool.pytest.ini_options]` — overkill for this project size.
