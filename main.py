from fastapi import FastAPI, HTTPException
from models import ProblemInput, SixHatsResponse
from controller import run_analysis

app = FastAPI(
    title="Six Thinking Hats AI",
    description="Multi-agent reasoning system based on Edward de Bono's Six Thinking Hats.",
    version="0.1.0",
)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/analyze", response_model=SixHatsResponse)
async def analyze(body: ProblemInput):
    try:
        result = await run_analysis(body.problem, body.context or "")
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
