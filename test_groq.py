import openai
import asyncio

async def test_groq():
    client = openai.AsyncOpenAI(
        api_key="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",
        base_url="https://api.groq.com/openai/v1"
    )

    try:
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "Hello, can you respond with a simple greeting?"}],
            max_tokens=50
        )
        print("Success:", response.choices[0].message.content)
    except Exception as e:
        print("Error:", str(e))

if __name__ == "__main__":
    asyncio.run(test_groq())