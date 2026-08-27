import asyncio
import os
from huggingface_hub import AsyncInferenceClient

token = os.environ.get("HUGGINGFACE_API_KEY")
if not token:
    raise RuntimeError("HUGGINGFACE_API_KEY is required")
client = AsyncInferenceClient(token=token)

async def test():
    print("Testing text_generation...")
    try:
        res = await client.text_generation(
            "Hello, what is your name?",
            model="mistralai/Mistral-7B-Instruct-v0.3",
            max_new_tokens=10
        )
        print("SUCCESS:", res)
    except Exception as e:
        print("FAILED:", str(e))

if __name__ == "__main__":
    asyncio.run(test())
