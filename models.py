from pydantic import BaseModel
from typing import Optional


class HatAnalysis(BaseModel):
    hat: str
    color: str
    perspective: str
    response: str


class ProblemInput(BaseModel):
    problem: str
    context: Optional[str] = None


class SixHatsResponse(BaseModel):
    problem: str
    analyses: list[HatAnalysis]
    summary: str
