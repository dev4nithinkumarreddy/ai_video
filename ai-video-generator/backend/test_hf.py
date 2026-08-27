import asyncio
import httpx
import os

token = os.environ.get("HUGGINGFACE_API_KEY")
if not token:
    raise RuntimeError("HUGGINGFACE_API_KEY is required")
headers = {"Authorization": f"Bearer {token}"}

async def test():
    async with httpx.AsyncClient() as client:
        print("Testing Audio...")
        res2 = await client.post(
            "https://router.huggingface.co/models/facebook/mms-tts-eng",
            headers=headers,
            json={"inputs": "Hello world!"}
        )
        print("Audio status:", res2.status_code, res2.text[:100])

if __name__ == "__main__":
    asyncio.run(test())
