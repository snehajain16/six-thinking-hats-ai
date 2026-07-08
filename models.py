from pydantic import BaseModel, field_validator
from typing import Optional


class HatAnalysis(BaseModel):
    hat: str
    color: str
    perspective: str
    response: str
    error: bool = False


class ProblemInput(BaseModel):
    problem: str
    context: Optional[str] = None

    @field_validator("problem")
    @classmethod
    def problem_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("problem must not be empty")
        return v


class SixHatsResponse(BaseModel):
    problem: str
    analyses: list[HatAnalysis]
    summary: str
