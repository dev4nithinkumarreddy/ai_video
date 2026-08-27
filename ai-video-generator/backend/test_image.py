import asyncio
import time
from services.image_service import get_image_service

async def main():
    print("=== SCOPED TEST: IMAGE GENERATION ===")
    
    t0 = time.time()
    image_service = get_image_service()
    try:
        path = await image_service.generate_image(
            prompt="A futuristic city in the style of cyberpunk",
            width=512,
            height=512
        )
        t1 = time.time()
        print(f"Image generated successfully in {t1-t0:.2f}s!")
        print(f"Path: {path}")
    except Exception as e:
        print("Image generation failed:", str(e))

if __name__ == "__main__":
    asyncio.run(main())
