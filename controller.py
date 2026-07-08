import asyncio
from agents.hats import (
    WhiteHatAgent,
    RedHatAgent,
    BlackHatAgent,
    YellowHatAgent,
    GreenHatAgent,
    BlueHatAgent,
)
from models import HatAnalysis, SixHatsResponse

_PARALLEL_HATS = [
    WhiteHatAgent(),
    RedHatAgent(),
    BlackHatAgent(),
    YellowHatAgent(),
    GreenHatAgent(),
]

_BLUE_HAT = BlueHatAgent()


async def run_analysis(problem: str, context: str = "") -> SixHatsResponse:
    # Run the first five hats in parallel
    analyses: list[HatAnalysis] = await asyncio.gather(
        *[agent.analyze(problem, context) for agent in _PARALLEL_HATS]
    )

    # Build a summary prompt for the Blue Hat from the other five
    aggregated = "\n\n".join(
        f"[{a.hat}]\n{a.response}" for a in analyses
    )
    blue_prompt_context = (
        f"Here are the perspectives from the other five hats:\n\n{aggregated}"
    )
    blue_analysis = await _BLUE_HAT.analyze(problem, blue_prompt_context)

    return SixHatsResponse(
        problem=problem,
        analyses=list(analyses) + [blue_analysis],
        summary=blue_analysis.response,
    )
