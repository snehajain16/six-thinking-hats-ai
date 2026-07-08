# Data Model: Core Hardening

**Feature**: specs/001-core-hardening
**Date**: 2026-07-08

---

## Entities

### `ProblemInput` (API request body)

| Field | Type | Required | Validation | Notes |
|---|---|---|---|---|
| `problem` | `str` | Yes | Non-empty, non-whitespace-only | Stripped before validation |
| `context` | `str \| None` | No | — | Defaults to `""` when absent |

### `HatAnalysis` (per-agent result)

| Field | Type | Required | Notes |
|---|---|---|---|
| `hat` | `str` | Yes | e.g. `"White Hat"` |
| `color` | `str` | Yes | e.g. `"white"` |
| `perspective` | `str` | Yes | e.g. `"Facts & Information"` |
| `response` | `str` | Yes | LLM text or error message |
| `error` | `bool` | Yes | `True` if this hat's Ollama call failed |

### `SixHatsResponse` (API response body)

| Field | Type | Required | Notes |
|---|---|---|---|
| `problem` | `str` | Yes | Echo of input `problem` |
| `analyses` | `list[HatAnalysis]` | Yes | Always exactly 6 items |
| `summary` | `str` | Yes | Blue Hat's `response` value |

---

## State / Flow

```
ProblemInput
    │
    ▼ (validate: non-empty problem)
Controller.run_analysis(problem, context)
    │
    ├── asyncio.gather([White, Red, Black, Yellow, Green])
    │       │
    │       └── each: BaseHatAgent.analyze()
    │               ├── success → HatAnalysis(error=False)
    │               └── exception → HatAnalysis(error=True, response=str(exc))
    │
    └── BlueHatAgent.analyze(problem, aggregated_context)
            └── HatAnalysis(error=False|True)
    │
    ▼
SixHatsResponse(problem, analyses=[6 × HatAnalysis], summary=blue.response)
```

---

## Validation Rules

- `ProblemInput.problem`: strip whitespace → if empty, raise `ValueError("problem must not be empty")`
- `HatAnalysis.error`: defaults to `False`; set to `True` only on caught exceptions in `analyze()`
- `SixHatsResponse.analyses`: invariant — always 6 items (enforced by controller logic, not Pydantic)
