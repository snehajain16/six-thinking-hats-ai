# Quickstart Validation Guide: Test Suite Hardening

**Feature**: specs/003-test-suite-hardening
**Date**: 2026-07-08

---

## Scenario 1: All Unit Tests Pass (No Ollama Required)

```bash
python -m pytest tests/ -v
```

**Expected**: All tests pass (30 existing + new tests). No `PytestUnknownMarkWarning` for `integration`.

---

## Scenario 2: Integration Tests Skip When OLLAMA_URL Unset

```bash
unset OLLAMA_URL
python -m pytest tests/ -v -m integration
```

**Expected**: All integration-marked tests show `SKIPPED` with reason "OLLAMA_URL not set".

---

## Scenario 3: Integration Marker Is Registered

```bash
python -m pytest --markers | grep integration
```

**Expected**: Output contains `integration: marks tests as requiring a live Ollama instance`.

---

## Scenario 4: Lint Clean

```bash
python -m black . && python -m ruff check .
```

**Expected**: Zero errors.
