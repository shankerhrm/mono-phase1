import os
import aiohttp
import logging
import json
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AnthropicAPI")

class AnthropicClient:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("ANTHROPIC")
        self.base_url = "https://api.anthropic.com/v1/messages"

    async def generate(self, prompt: str, model: str = None) -> str:
        """
        Sends an async request to the Anthropic API.
        Yields a fallback response if the API key is not set or an error occurs.
        """
        model_name = model or os.environ.get("ANTHROPICMODEL", "claude-3-5-sonnet-20241022")
        
        # If no key or placeholder, skip actual API call to keep system running
        if not self.api_key or self.api_key == "ertertret":
            return f"[MOCK GENERATION]\nModel: {model_name}\nPrompt length: {len(prompt)}\nSimulation OK."

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        payload = {
            "model": model_name,
            "max_tokens": 1024,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        for attempt in range(5):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(self.base_url, headers=headers, json=payload) as response:
                        
                        if response.status == 429:
                            delay = 5 * (2 ** attempt)
                            logger.warning(f"Anthropic API Rate Limit hit [429]. Retrying in {delay} seconds...")
                            if attempt < 4:
                                await asyncio.sleep(delay)
                                continue
                            else:
                                return "[API ERROR] Rate limit exhausted."
                                
                        if response.status != 200:
                            error_text = await response.text()
                            logger.error(f"Anthropic API Error [{response.status}]: {error_text}")
                            return "[API ERROR] Generation failed."
                            
                        data = await response.json()
                        
                        # Safely extract text
                        try:
                            return data['content'][0]['text']
                        except (KeyError, IndexError) as e:
                            logger.error(f"Failed to parse Anthropic response: {data}")
                            return "[API PARSE ERROR] Invalid format."
                            
            except Exception as e:
                logger.error(f"Exception during Anthropic request: {e}")
                
            # If we fall through due to a non-429 exception, wait and retry just in case it's a network blip
            if attempt < 4:
                await asyncio.sleep(2)
            else:
                return "[SYSTEM ERROR] Request failed fundamentally."
