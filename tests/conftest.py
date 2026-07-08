import os

import pytest
from unittest.mock import AsyncMock, patch


def pytest_collection_modifyitems(config, items):
    if os.getenv("OLLAMA_URL", "").strip():
        return
    skip = pytest.mark.skip(reason="OLLAMA_URL not set — live Ollama required")
    for item in items:
        if item.get_closest_marker("integration"):
            item.add_marker(skip)


@pytest.fixture
def mock_ollama():
    """Patch BaseHatAgent._call_ollama to return a canned response."""
    with patch(
        "agents.base.BaseHatAgent._call_ollama",
        new_callable=AsyncMock,
        return_value="Mocked LLM response.",
    ) as mock:
        yield mock


@pytest.fixture
def failing_ollama():
    """Patch BaseHatAgent._call_ollama to raise a connection error."""
    with patch(
        "agents.base.BaseHatAgent._call_ollama",
        new_callable=AsyncMock,
        side_effect=Exception("Connection refused"),
    ) as mock:
        yield mock
