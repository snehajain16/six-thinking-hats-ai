import httpx
import logging
import os
import time
from models import HatAnalysis

logger = logging.getLogger(__name__)

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

_TIMEOUT = httpx.Timeout(connect=5.0, read=120.0, write=5.0, pool=5.0)


class BaseHatAgent:
    hat: str
    color: str
    perspective: str
    system_prompt: str

    async def analyze(self, problem: str, context: str = "") -> HatAnalysis:
        start = time.monotonic()
        logger.info("hat_call_start hat=%r model=%s", self.hat, OLLAMA_MODEL)
        try:
            response = await self._call_ollama(self._build_prompt(problem, context))
            duration_ms = int((time.monotonic() - start) * 1000)
            logger.info(
                "hat_call_done hat=%r model=%s duration_ms=%d error=false",
                self.hat,
                OLLAMA_MODEL,
                duration_ms,
            )
            return HatAnalysis(
                hat=self.hat,
                color=self.color,
                perspective=self.perspective,
                response=response,
                error=False,
            )
        except Exception as exc:
            duration_ms = int((time.monotonic() - start) * 1000)
            logger.error(
                "hat_call_done hat=%r model=%s duration_ms=%d error=true exc=%s",
                self.hat,
                OLLAMA_MODEL,
                duration_ms,
                exc,
            )
            return HatAnalysis(
                hat=self.hat,
                color=self.color,
                perspective=self.perspective,
                response=f"[Error: {exc}]",
                error=True,
            )

    def _build_prompt(self, problem: str, context: str) -> str:
        base = f"Problem: {problem}"
        if context:
            base += f"\nContext: {context}"
        return base

    async def _call_ollama(self, prompt: str) -> str:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            payload = {
                "model": OLLAMA_MODEL,
                "messages": [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt},
                ],
                "stream": False,
            }
            r = await client.post(f"{OLLAMA_URL}/api/chat", json=payload)
            r.raise_for_status()
            data = r.json()
            return data["message"]["content"]
