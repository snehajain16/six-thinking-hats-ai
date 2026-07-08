# Feature Specification: Core Hardening — Multi-Agent Pipeline, API & Ollama Integration

**Feature Branch**: `feature/issue-1-2-3-core-hardening`

**Created**: 2026-07-08

**Status**: Draft

**Closes**: #1, #2, #3

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Submit a Problem and Receive Six-Hat Analysis (Priority: P1)

A developer or decision-maker submits a problem statement to the system and receives a structured response containing all six hat perspectives and a synthesised conclusion, with no crashes or unhandled errors regardless of what Ollama does.

**Why this priority**: This is the core value proposition. Every other feature depends on this working reliably.

**Independent Test**: Send `POST /analyze` with a valid problem string. Verify a `SixHatsResponse` is returned containing exactly 6 `HatAnalysis` objects and a non-empty `summary`.

**Acceptance Scenarios**:

1. **Given** the API is running and Ollama is available, **When** a `POST /analyze` request is sent with a `problem` and optional `context`, **Then** the response contains 6 hat analyses and a Blue Hat `summary` within a reasonable time.
2. **Given** a `POST /analyze` request with an empty `problem` string, **When** the request is received, **Then** the system returns HTTP 422 with a descriptive validation error.
3. **Given** one hat agent encounters an Ollama error mid-run, **When** the pipeline completes, **Then** the response still returns all 6 analyses; the failed hat's `response` contains an error message and the `error` field is set to `true`.

---

### User Story 2 — Check System Health (Priority: P2)

An operator or CI pipeline polls the health endpoint to confirm the API is alive before routing traffic or running tests.

**Why this priority**: Required for container orchestration liveness probes and deployment smoke tests.

**Independent Test**: Send `GET /health` without any Ollama interaction. Verify `{"status": "ok"}` is returned with HTTP 200.

**Acceptance Scenarios**:

1. **Given** the API server is running, **When** `GET /health` is called, **Then** it returns HTTP 200 with `{"status": "ok"}`.
2. **Given** Ollama is unreachable, **When** `GET /health` is called, **Then** it still returns HTTP 200 (health reflects API liveness, not Ollama liveness).

---

### User Story 3 — Startup Connectivity Warning (Priority: P3)

On startup, the API checks whether Ollama is reachable and logs a clear warning if not, without refusing to start.

**Why this priority**: Prevents silent failures where the API starts but every `/analyze` call fails. Gives operators immediate feedback.

**Independent Test**: Start the API with `OLLAMA_URL` pointing at a non-existent host. Confirm the API starts successfully and a warning appears in logs.

**Acceptance Scenarios**:

1. **Given** Ollama is unreachable at startup, **When** the API starts, **Then** a `WARNING` log entry is emitted and the API is still reachable.
2. **Given** Ollama is reachable at startup, **When** the API starts, **Then** an `INFO` log entry confirms connectivity.

---

### User Story 4 — Configure LLM Backend Without Code Changes (Priority: P2)

A developer switches from `llama3` to `mistral` or points at a remote Ollama instance by setting environment variables, without touching any source file.

**Why this priority**: Essential for portability across environments (local dev, staging, Docker).

**Independent Test**: Set `OLLAMA_MODEL=mistral` in `.env`, start the API, call `/analyze`. Confirm the `mistral` model is used in Ollama requests.

**Acceptance Scenarios**:

1. **Given** `OLLAMA_URL` and `OLLAMA_MODEL` are set in `.env`, **When** the API starts, **Then** all Ollama calls use those values.
2. **Given** neither variable is set, **When** the API starts, **Then** `http://localhost:11434` and `llama3` are used as defaults.

---

### Edge Cases

- What happens when Ollama returns a malformed JSON response? → Caught, logged, and surfaced as a graceful error in that hat's `HatAnalysis`.
- What happens when the Ollama call times out (>120s)? → `httpx.TimeoutException` is caught; that hat's analysis contains a timeout error message.
- What happens when `problem` is whitespace-only? → Treated as empty; rejected with HTTP 422.
- What happens when all 5 parallel hats fail? → Blue Hat still runs but receives empty context; full `SixHatsResponse` returned with `error: true` on all failed analyses.
- What happens when `context` is omitted? → Defaults to empty string; no error.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose a `POST /analyze` endpoint accepting `problem` (required, non-empty string) and `context` (optional string).
- **FR-002**: The system MUST reject a `POST /analyze` request where `problem` is empty or whitespace-only with HTTP 422.
- **FR-003**: The system MUST run White, Red, Black, Yellow, and Green hat agents concurrently for each analysis request.
- **FR-004**: The system MUST run the Blue Hat agent after all other hats complete, passing their aggregated output as context.
- **FR-005**: The system MUST return a `SixHatsResponse` containing exactly 6 `HatAnalysis` objects and a `summary` string.
- **FR-006**: Each `HatAnalysis` MUST include `hat`, `color`, `perspective`, `response`, and `error` (boolean, default false) fields.
- **FR-007**: If a single hat agent fails (timeout, malformed response, connection error), the system MUST continue and return partial results with `error: true` on the affected analysis.
- **FR-008**: The system MUST expose a `GET /health` endpoint returning `{"status": "ok"}` with HTTP 200.
- **FR-009**: The system MUST read `OLLAMA_URL` and `OLLAMA_MODEL` from environment variables, with documented defaults.
- **FR-010**: The system MUST attempt to connect to Ollama at startup, logging a warning if unreachable (but not refusing to start).
- **FR-011**: The system MUST emit structured log entries for each incoming API request and each Ollama call (model, hat name, duration).
- **FR-012**: The system MUST surface Ollama connection errors as HTTP 500 with a descriptive `detail` field.
- **FR-013**: Auto-generated API documentation MUST be accurate and accessible at `/docs`.

### Key Entities

- **`ProblemInput`**: The user's submitted problem. Attributes: `problem` (required, non-blank string), `context` (optional string).
- **`HatAnalysis`**: One hat's perspective. Attributes: `hat` (name), `color`, `perspective` (mode label), `response` (LLM text), `error` (bool).
- **`SixHatsResponse`**: Complete analysis result. Attributes: `problem`, `analyses` (list of 6 `HatAnalysis`), `summary` (Blue Hat response).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A valid problem submission returns a complete six-hat response in all cases where Ollama is available, with no unhandled exceptions.
- **SC-002**: An empty or whitespace-only problem is rejected with a clear error in 100% of cases.
- **SC-003**: A single hat failure never causes the entire request to fail; partial results are always returned.
- **SC-004**: The system starts successfully in under 5 seconds regardless of Ollama availability.
- **SC-005**: Every Ollama call is observable in logs with hat name, model used, and outcome.
- **SC-006**: Switching the LLM model requires only an environment variable change — zero code changes.

## Assumptions

- Ollama is either running locally or accessible at a network URL; no authentication on the Ollama endpoint.
- A single Ollama model is used for all six hats (no per-hat model configuration in this version).
- Concurrent hat execution does not require rate-limiting against Ollama in this version.
- `context` is a free-form string; no schema or length validation beyond it being a string.
- Structured logging targets stdout in JSON-friendly format; no external log aggregator required.
- Mobile/browser clients are out of scope; this is a server-to-server API.
