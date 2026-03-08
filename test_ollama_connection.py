import asyncio
import os
from ollama_api import OllamaClient
from dotenv import load_dotenv

load_dotenv()

async def test_connection():
    client = OllamaClient()
    print(f"Testing Ollama connection to: {client.base_url}")
    print(f"Using model: {client.model_name}")
    
    prompt = "Why is the sky blue? Answer in one sentence."
    print(f"Prompt: {prompt}")
    
    response = await client.generate(prompt)
    print(f"\nResponse:\n{response}")
    
    if "[OLLAMA ERROR]" in response or "[SYSTEM ERROR]" in response:
        print("\n❌ Connection Failed!")
    else:
        print("\n✅ Connection Successful!")

if __name__ == "__main__":
    asyncio.run(test_connection())
