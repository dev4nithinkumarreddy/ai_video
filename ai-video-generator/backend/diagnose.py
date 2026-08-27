import asyncio
import logging
from services.openai_service import get_openai_service
from services.audio_service import get_audio_service
from services.image_service import get_image_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("diagnose")

async def diagnose_all():
    print("\n--- DIAGNOSING OPENAI SERVICE ---")
    try:
        openai_svc = get_openai_service()
        script = await openai_svc.generate_script(topic="test", description="a simple test", num_scenes=1)
        print("OpenAI SUCCESS:", script.get("title"))
    except Exception as e:
        print("OpenAI FAILED:", str(e))
        if hasattr(e, "response"):
            print("Response:", e.response.text)

    print("\n--- DIAGNOSING AUDIO SERVICE ---")
    try:
        audio_svc = get_audio_service()
        audio = await audio_svc.generate_audio(text="Hello world", output_filename="test_audio.mp3")
        print("Audio SUCCESS:", audio)
    except Exception as e:
        print("Audio FAILED:", str(e))
        if hasattr(e, "response"):
            print("Response:", e.response.text)

    print("\n--- DIAGNOSING IMAGE SERVICE ---")
    try:
        image_svc = get_image_service()
        image = await image_svc.generate_image(prompt="A beautiful landscape", output_filename="test_image.png")
        print("Image SUCCESS:", image)
    except Exception as e:
        print("Image FAILED:", str(e))
        if hasattr(e, "response"):
            print("Response:", e.response.text)

if __name__ == "__main__":
    asyncio.run(diagnose_all())
