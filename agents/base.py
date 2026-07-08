import httpx
import os
from models import HatAnalysis

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")


class BaseHatAgent:
    hat: str
    color: str
    perspective: str
    system_prompt: str

    async def analyze(self, problem: str, context: str = "") -> HatAnalysis:
        prompt = self._build_prompt(problem, context)
        response = await self._call_ollama(prompt)
        return HatAnalysis(
            hat=self.hat,
            color=self.color,
            perspective=self.perspective,
            response=response,
        )

    def _build_prompt(self, problem: str, context: str) -> str:
        base = f"Problem: {problem}"
        if context:
            base += f"\nContext: {context}"
        return base

    async def _call_ollama(self, prompt: str) -> str:
        async with httpx.AsyncClient(timeout=120.0) as client:
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
            return r.json()["message"]["content"]
