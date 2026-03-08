import os
import aiohttp
import logging
import json
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("OllamaAPI")

class OllamaClient:
    def __init__(self, base_url: str = None):
        self.base_url = base_url or os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate")
        self.model_name = os.environ.get("OLLAMA_MODEL", "llama3")
        # Limit concurrent requests (2 is more stable for local hardware)
        self.semaphore = asyncio.Semaphore(2) 
        self._session = None

    async def get_session(self):
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60))
        return self._session

    async def generate(self, prompt: str, model: str = None) -> str:
        model_name = model or self.model_name
        payload = {"model": model_name, "prompt": prompt, "stream": False}
        
        max_retries = 5
        retry_delay = 2.0
        
        for attempt in range(max_retries):
            try:
                async with self.semaphore:
                    session = await self.get_session()
                    async with session.post(self.base_url, json=payload) as response:
                        if response.status != 200:
                            error_text = await response.text()
                            logger.warning(f"Ollama Error [{response.status}] (Attempt {attempt+1})")
                            if attempt < max_retries - 1:
                                await asyncio.sleep(retry_delay * (2 ** attempt))
                                continue
                            return f"[OLLAMA ERROR] status {response.status}"
                        
                        data = await response.json()
                        return data.get("response", "[OLLAMA ERROR] No response field")
            except Exception as e:
                err_type = type(e).__name__
                logger.warning(f"Ollama Request Exception: {err_type} (Attempt {attempt+1})")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay * (2 ** attempt))
                    continue
                return f"[SYSTEM ERROR] {err_type}: {str(e)}"
        
        return "[SYSTEM ERROR] Max retries reached"

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()
