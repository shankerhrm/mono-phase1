import os
import aiohttp
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GeminiAPI")

class GeminiClient:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("GEMINI_KEY")
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"

    async def generate(self, prompt: str, model: str = None) -> str:
        """
        Sends an async request to the Gemini API.
        Yields a fallback response if the API key is not set or an error occurs.
        """
        model_name = model or os.environ.get("SMALL_PROMPT_MODELNAME", "gemini-flash-latest")
        
        # If no key, skip actual API call to keep system running
        if not self.api_key or self.api_key == "xsdfff":
            return f"[MOCK GENERATION]\nModel: {model_name}\nPrompt length: {len(prompt)}\nSimulation OK."

        url = f"{self.base_url}/{model_name}:generateContent?key={self.api_key}"
        headers = {
            "Content-Type": "application/json"
        }
        
        # Convert prompt to Gemini structure
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "safetySettings": [
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_NONE"
                }
            ]
        }
        
        import asyncio
        for attempt in range(5):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, headers=headers, json=payload) as response:
                        
                        if response.status == 429:
                            delay = 5 * (2 ** attempt)
                            logger.warning(f"Gemini API Rate Limit hit [429]. Retrying in {delay} seconds...")
                            if attempt < 4:
                                await asyncio.sleep(delay)
                                continue
                            else:
                                return "[API ERROR] Rate limit exhausted."
                                
                        if response.status != 200:
                            error_text = await response.text()
                            logger.error(f"Gemini API Error [{response.status}]: {error_text}")
                            return "[API ERROR] Generation failed."
                            
                        data = await response.json()
                        
                        # Safely extract text
                        try:
                            return data['candidates'][0]['content']['parts'][0]['text']
                        except (KeyError, IndexError) as e:
                            logger.error(f"Failed to parse Gemini response: {data}")
                            return "[API PARSE ERROR] Invalid format."
                            
            except Exception as e:
                logger.error(f"Exception during Gemini request: {e}")
                
            # If we fall through due to a non-429 exception, wait and retry just in case it's a network blip
            if attempt < 4:
                await asyncio.sleep(2)
            else:
                return "[SYSTEM ERROR] Request failed fundamentally."
