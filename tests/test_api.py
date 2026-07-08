from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from main import app

client = TestClient(app)


def test_health_returns_200():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_does_not_depend_on_ollama():
    with patch(
        "agents.base.BaseHatAgent._call_ollama",
        new_callable=AsyncMock,
        side_effect=Exception("Ollama down"),
    ):
        response = client.get("/health")
    assert response.status_code == 200


def test_analyze_valid_request_returns_200(mock_ollama):
    response = client.post(
        "/analyze", json={"problem": "Should we adopt microservices?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["problem"] == "Should we adopt microservices?"
    assert len(data["analyses"]) == 6
    assert isinstance(data["summary"], str)
    assert data["summary"]


def test_analyze_with_context(mock_ollama):
    response = client.post(
        "/analyze",
        json={
            "problem": "Expand to new market?",
            "context": "10 engineers, Series A startup.",
        },
    )
    assert response.status_code == 200
    assert len(response.json()["analyses"]) == 6


def test_analyze_empty_problem_returns_422():
    response = client.post("/analyze", json={"problem": ""})
    assert response.status_code == 422


def test_analyze_whitespace_problem_returns_422():
    response = client.post("/analyze", json={"problem": "   "})
    assert response.status_code == 422


def test_analyze_missing_problem_returns_422():
    response = client.post("/analyze", json={})
    assert response.status_code == 422


def test_analyze_ollama_error_returns_500():
    """A hard controller-level exception (not per-hat failure) returns 500."""
    with patch(
        "main.run_analysis",
        new_callable=AsyncMock,
        side_effect=Exception("Ollama connection failed"),
    ):
        response = client.post("/analyze", json={"problem": "Valid problem"})
    assert response.status_code == 500
    assert "detail" in response.json()


def test_analyze_all_hats_fail_returns_200_with_errors(failing_ollama):
    """When all Ollama calls fail (graceful degradation), returns 200 with error=True on all analyses."""
    response = client.post("/analyze", json={"problem": "Valid problem"})
    assert response.status_code == 200
    data = response.json()
    assert len(data["analyses"]) == 6
    assert all(a["error"] is True for a in data["analyses"])


def test_analyze_response_has_error_field(mock_ollama):
    response = client.post("/analyze", json={"problem": "Test"})
    data = response.json()
    for analysis in data["analyses"]:
        assert "error" in analysis
        assert analysis["error"] is False
