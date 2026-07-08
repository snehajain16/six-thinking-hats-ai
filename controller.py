import asyncio
import logging
from agents.hats import (
    WhiteHatAgent,
    RedHatAgent,
    BlackHatAgent,
    YellowHatAgent,
    GreenHatAgent,
    BlueHatAgent,
)
from models import HatAnalysis, SixHatsResponse

logger = logging.getLogger(__name__)

_PARALLEL_HATS = [
    WhiteHatAgent(),
    RedHatAgent(),
    BlackHatAgent(),
    YellowHatAgent(),
    GreenHatAgent(),
]

_BLUE_HAT = BlueHatAgent()


async def run_analysis(problem: str, context: str = "") -> SixHatsResponse:
    results = await asyncio.gather(
        *[agent.analyze(problem, context) for agent in _PARALLEL_HATS],
        return_exceptions=True,
    )

    analyses: list[HatAnalysis] = []
    for agent, result in zip(_PARALLEL_HATS, results):
        if isinstance(result, Exception):
            logger.error("hat_exception hat=%r exc=%s", agent.hat, result)
            analyses.append(
                HatAnalysis(
                    hat=agent.hat,
                    color=agent.color,
                    perspective=agent.perspective,
                    response=f"[Error: {result}]",
                    error=True,
                )
            )
        else:
            analyses.append(result)

    failed = [a for a in analyses if a.error]
    successful = [a for a in analyses if not a.error]

    aggregated_parts = [f"[{a.hat}]\n{a.response}" for a in successful]
    if failed:
        failed_names = ", ".join(a.hat for a in failed)
        aggregated_parts.append(
            f"[Note: The following hats encountered errors: {failed_names}]"
        )
    aggregated = "\n\n".join(aggregated_parts)

    blue_context = (
        f"Here are the perspectives from the other five hats:\n\n{aggregated}"
    )
    blue_analysis = await _BLUE_HAT.analyze(problem, blue_context)

    all_analyses = analyses + [blue_analysis]
    return SixHatsResponse(
        problem=problem,
        analyses=all_analyses,
        summary=blue_analysis.response,
    )
