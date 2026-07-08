# Feature Specification: Docker & Docker Compose Setup

**Feature Branch**: `feature/issue-6-docker`

**Created**: 2026-07-08

**Status**: Draft

**Input**: User description: "Containerise the FastAPI app and wire it to Ollama via Docker Compose so the full stack runs with a single command."

## User Scenarios & Testing *(mandatory)*

### User Story 1 — One-Command Stack Startup (Priority: P1)

A developer clones the repository and runs a single command to start the full stack — both the API and the local AI model runtime. They don't need to install Python, configure a virtual environment, or manually start any service.

**Why this priority**: This is the primary value of containerisation. Without it, the project requires significant local setup that blocks contributors.

**Independent Test**: Run the startup command on a fresh machine with only the container runtime installed. The API health endpoint responds successfully within 30 seconds.

**Acceptance Scenarios**:

1. **Given** only a container runtime is installed, **When** the developer runs the single startup command, **Then** both the API and the AI model runtime start and the API health check returns a success response within 30 seconds.
2. **Given** the stack is already running, **When** the developer restarts it, **Then** previously downloaded AI models are still available without re-downloading (persisted across restarts).
3. **Given** the stack is running, **When** the developer calls the analysis endpoint, **Then** it returns a valid six-hat analysis response.

---

### User Story 2 — Secure, Configurable Deployment (Priority: P2)

An operator deploys the containerised stack and needs to configure the AI model and other settings without modifying any files or baking secrets into the image.

**Why this priority**: Hardcoded configuration prevents the app from being deployed to different environments or shared safely.

**Independent Test**: Pass a custom model name via environment variable; the container uses it without image rebuild.

**Acceptance Scenarios**:

1. **Given** the container image is built, **When** an operator sets the AI model name via environment variable, **Then** the API uses that model without rebuilding the image.
2. **Given** the container image is built, **When** it is inspected, **Then** no credentials, API keys, or `.env` files are present inside the image.
3. **Given** the API container starts, **When** the AI model runtime is not yet ready, **Then** the API waits and only begins accepting requests after the model runtime is available.

---

### User Story 3 — Minimal Production-Ready Image (Priority: P3)

A developer wants the container image to be as small as practical so it starts fast and uses minimal resources.

**Why this priority**: Smaller images reduce pull times, storage costs, and attack surface.

**Independent Test**: Build the image and check its size — it should contain only the runtime dependencies, not build tools.

**Acceptance Scenarios**:

1. **Given** the image is built, **When** its contents are inspected, **Then** only runtime dependencies are present (no compilers, dev headers, or build caches).
2. **Given** the image is built, **When** the container starts, **Then** the API is reachable and all 6 hat analyses are functional.

---

### Edge Cases

- What if the AI model runtime takes more than 30 seconds to start on a slow machine? The API container should retry, not crash immediately.
- What if `docker compose up` is run without `--build` and the image is stale? The stack should still start; users must explicitly rebuild when code changes.
- What if the model download fails mid-startup? The entrypoint should surface a clear error message and exit non-zero so Compose restarts or the operator knows to retry.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The project MUST provide a container definition that builds the API into a runnable image using a multi-stage approach (separate build and runtime stages).
- **FR-002**: The runtime image MUST contain only the dependencies needed to run the API — no build tools or development artifacts.
- **FR-003**: The project MUST provide a multi-service orchestration file defining an `api` service and an `ollama` service.
- **FR-004**: The `api` service MUST depend on the `ollama` service so it starts after the model runtime is available.
- **FR-005**: The AI model name MUST be configurable via environment variable with a sensible default; no model name may be hardcoded in the image.
- **FR-006**: No secrets, credentials, or `.env` files MUST be baked into the container image.
- **FR-007**: The `ollama` service MUST use a named volume so downloaded models persist across container restarts.
- **FR-008**: An entrypoint script MUST pull the configured AI model before starting the API, failing with a non-zero exit code if the pull fails.
- **FR-009**: After running the startup command, the API health check endpoint MUST return a success response within 30 seconds.
- **FR-010**: The API MUST be reachable on port 8000 of the host machine after startup.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A developer with no local Python installation can start the full stack and receive a successful health check response in under 30 seconds, using only a container runtime.
- **SC-002**: Restarting the stack does not re-download the AI model — startup time on second run is at least 50% faster than the first run.
- **SC-003**: The container image contains zero build-time artifacts (compilers, dev headers, package caches) when inspected post-build.
- **SC-004**: Changing the AI model name via environment variable takes effect without rebuilding the image — verified by inspecting startup logs.
- **SC-005**: The stack is fully operational (health check green, analysis endpoint responding) within 30 seconds of issuing the startup command on a machine where the model has already been pulled.

## Assumptions

- The container runtime available is Docker (or a compatible alternative) with Compose V2 plugin support (`docker compose` not `docker-compose`).
- The default AI model is `llama3` — operators can override via environment variable.
- Model persistence is scoped to a named Docker volume; host-path bind mounts are out of scope.
- The entrypoint script runs model pull synchronously before starting the API — it does not background the pull.
- A `.dockerignore` file will be created to exclude unnecessary files from the build context.
- Health check configuration (retries, interval, timeout) is set in the orchestration file, not the Dockerfile.
