import json
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def collect_sse_events(response) -> list[dict]:
    """Parse SSE stream into a list of event dicts with keys 'event' and 'data'."""
    events = []
    current: dict = {}
    for line in response.iter_lines():
        if line.startswith("event:"):
            current["event"] = line[len("event:") :].strip()
        elif line.startswith("data:"):
            current["data"] = line[len("data:") :].strip()
        elif line == "" and current:
            events.append(current)
            current = {}
    if current:
        events.append(current)
    return events


# ---------------------------------------------------------------------------
# T007: Happy path
# ---------------------------------------------------------------------------


def test_stream_happy_path_seven_events(mock_ollama):
    with client.stream(
        "POST",
        "/analyze/stream",
        json={"problem": "Should we adopt a four-day work week?"},
    ) as response:
        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]
        events = collect_sse_events(response)

    assert len(events) == 7, f"Expected 7 events, got {len(events)}: {events}"

    hat_names = set()
    for ev in events[:6]:
        assert "data" in ev
        payload = json.loads(ev["data"])
        hat_names.add(payload["hat"])

    expected_hats = {
        "White Hat",
        "Red Hat",
        "Black Hat",
        "Yellow Hat",
        "Green Hat",
        "Blue Hat",
    }
    assert hat_names == expected_hats

    done_ev = events[6]
    assert done_ev.get("event") == "done"
    done_payload = json.loads(done_ev["data"])
    assert "summary" in done_payload
    assert done_payload["summary"]


# ---------------------------------------------------------------------------
# T008: Input validation
# ---------------------------------------------------------------------------


def test_stream_empty_problem_returns_422():
    response = client.post("/analyze/stream", json={"problem": ""})
    assert response.status_code == 422


def test_stream_whitespace_problem_returns_422():
    response = client.post("/analyze/stream", json={"problem": "   "})
    assert response.status_code == 422


def test_stream_missing_problem_returns_422():
    response = client.post("/analyze/stream", json={})
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# T009: Partial failure — one hat raises
# ---------------------------------------------------------------------------


def test_stream_partial_failure_seven_events_with_error():
    call_count = 0

    async def sometimes_fail(prompt: str) -> str:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise Exception("Simulated hat failure")
        return "Mocked LLM response."

    with patch(
        "agents.base.BaseHatAgent._call_ollama",
        new_callable=AsyncMock,
        side_effect=sometimes_fail,
    ):
        with client.stream(
            "POST",
            "/analyze/stream",
            json={"problem": "Test partial failure"},
        ) as response:
            assert response.status_code == 200
            events = collect_sse_events(response)

    assert len(events) == 7, f"Expected 7 events, got {len(events)}"

    hat_events = [json.loads(ev["data"]) for ev in events[:6]]
    error_events = [e for e in hat_events if e["error"]]
    assert len(error_events) == 1, "Expected exactly one error event"

    done_ev = events[6]
    assert done_ev.get("event") == "done"


# ---------------------------------------------------------------------------
# T010: All hats fail
# ---------------------------------------------------------------------------


def test_stream_all_hats_fail_seven_events():
    with patch(
        "agents.base.BaseHatAgent._call_ollama",
        new_callable=AsyncMock,
        side_effect=Exception("All hats down"),
    ):
        with client.stream(
            "POST",
            "/analyze/stream",
            json={"problem": "Test all hats fail"},
        ) as response:
            assert response.status_code == 200
            events = collect_sse_events(response)

    assert len(events) == 7, f"Expected 7 events, got {len(events)}"

    hat_events = [json.loads(ev["data"]) for ev in events[:6]]
    assert all(e["error"] for e in hat_events), "All hat events should have error=true"

    done_ev = events[6]
    assert done_ev.get("event") == "done"
