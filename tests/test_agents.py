import pytest
from agents.hats import (
    WhiteHatAgent,
    RedHatAgent,
    BlackHatAgent,
    YellowHatAgent,
    GreenHatAgent,
    BlueHatAgent,
)


ALL_AGENTS = [
    WhiteHatAgent(),
    RedHatAgent(),
    BlackHatAgent(),
    YellowHatAgent(),
    GreenHatAgent(),
    BlueHatAgent(),
]

EXPECTED = [
    ("White Hat", "white", "Facts"),
    ("Red Hat", "red", "Emotion"),
    ("Black Hat", "black", "Critical"),
    ("Yellow Hat", "yellow", "Optimism"),
    ("Green Hat", "green", "Creativit"),
    ("Blue Hat", "blue", "Process"),
]


@pytest.mark.parametrize("agent,expected", zip(ALL_AGENTS, EXPECTED))
def test_agent_attributes(agent, expected):
    name, color, perspective_prefix = expected
    assert agent.hat == name
    assert agent.color == color
    assert agent.perspective.startswith(perspective_prefix)
    assert agent.system_prompt.strip(), f"{name} system_prompt must not be empty"
    assert (
        name.lower() in agent.system_prompt.lower()
    ), f"{name} must appear in its own system_prompt"


@pytest.mark.asyncio
async def test_analyze_success(mock_ollama):
    agent = WhiteHatAgent()
    result = await agent.analyze("Test problem")
    assert result.hat == "White Hat"
    assert result.error is False
    assert result.response == "Mocked LLM response."


@pytest.mark.asyncio
async def test_analyze_returns_error_on_exception(failing_ollama):
    agent = WhiteHatAgent()
    result = await agent.analyze("Test problem")
    assert result.error is True
    assert "Connection refused" in result.response
    assert result.hat == "White Hat"
