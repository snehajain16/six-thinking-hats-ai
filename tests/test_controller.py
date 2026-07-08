import pytest
from controller import run_analysis


@pytest.mark.asyncio
async def test_run_analysis_returns_six_analyses(mock_ollama):
    result = await run_analysis("Should we adopt microservices?")
    assert len(result.analyses) == 6


@pytest.mark.asyncio
async def test_summary_equals_blue_hat_response(mock_ollama):
    result = await run_analysis("Should we adopt microservices?")
    blue = result.analyses[5]
    assert blue.hat == "Blue Hat"
    assert result.summary == blue.response


@pytest.mark.asyncio
async def test_problem_echoed_in_response(mock_ollama):
    problem = "Test problem statement"
    result = await run_analysis(problem)
    assert result.problem == problem


@pytest.mark.asyncio
async def test_partial_failure_still_returns_six_analyses(failing_ollama):
    """When all Ollama calls fail, still get 6 HatAnalysis items with error=True."""
    result = await run_analysis("Test problem")
    assert len(result.analyses) == 6
    for analysis in result.analyses:
        assert analysis.error is True


@pytest.mark.asyncio
async def test_partial_failure_one_hat(mock_ollama):
    """When one specific hat fails, only that hat has error=True."""
    call_count = 0

    async def selective_fail(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise Exception("Simulated failure on first hat")
        return "Mocked LLM response."

    mock_ollama.side_effect = selective_fail
    result = await run_analysis("Test problem")
    assert len(result.analyses) == 6
    error_count = sum(1 for a in result.analyses if a.error)
    assert error_count == 1


@pytest.mark.asyncio
async def test_blue_hat_always_runs(failing_ollama):
    """Blue Hat runs even when all parallel hats fail."""
    result = await run_analysis("Test problem")
    blue = result.analyses[5]
    assert blue.hat == "Blue Hat"
