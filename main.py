import logging
import os
import time
from contextlib import asynccontextmanager

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request

load_dotenv()

from logging_config import setup_logging  # noqa: E402

setup_logging()

from models import ProblemInput, SixHatsResponse  # noqa: E402
from controller import run_analysis  # noqa: E402

logger = logging.getLogger(__name__)

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: probe Ollama connectivity
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(f"{OLLAMA_URL}/api/tags")
            r.raise_for_status()
        logger.info("ollama_reachable url=%s", OLLAMA_URL)
    except Exception as exc:
        logger.warning(
            "ollama_unreachable url=%s reason=%s — API will start but /analyze calls will fail",
            OLLAMA_URL,
            exc,
        )
    yield


app = FastAPI(
    title="Six Thinking Hats AI",
    description="Multi-agent reasoning system based on Edward de Bono's Six Thinking Hats.",
    version="0.1.0",
    lifespan=lifespan,
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.monotonic()
    response = await call_next(request)
    duration_ms = int((time.monotonic() - start) * 1000)
    logger.info(
        "request_done method=%s path=%s status=%d duration_ms=%d",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


@app.get("/health")
async def health():
    logger.info("health_check status=ok")
    return {"status": "ok"}


@app.post("/analyze", response_model=SixHatsResponse)
async def analyze(body: ProblemInput):
    logger.info("request_received path=/analyze problem_len=%d", len(body.problem))
    try:
        result = await run_analysis(body.problem, body.context or "")
        failed = sum(1 for a in result.analyses if a.error)
        logger.info("analyze_done hats_failed=%d", failed)
        return result
    except Exception as exc:
        logger.error("analyze_error exc=%s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
