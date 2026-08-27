import asyncio
import time
import psutil
import json
from services.openai_service import get_openai_service
from services.audio_service import get_audio_service
from services.image_service import get_image_service
from services.video_rendering_service import get_video_rendering_service

def print_memory(stage=""):
    mem = psutil.virtual_memory()
    print(f"[MEMORY] {stage} - RAM Available: {mem.available / (1024**3):.2f} GB ({mem.percent}% used)")

async def main():
    print("=== E2E TEST: STARTING ===")
    print_memory("Initial")
    
    # 1. Script
    print("\n--- 1. SCRIPT GENERATION ---")
    t0 = time.time()
    openai_service = get_openai_service()
    try:
        script = await openai_service.generate_script(
            topic="A cute dog running in a park",
            description="A short video of a dog",
            num_scenes=1,
            style="cinematic"
        )
    except Exception as e:
        print("Script failed:", str(e))
        script = {}
        
    t1 = time.time()
    print(f"Script generated in {t1-t0:.2f}s")
    print("Script raw output:", json.dumps(script, indent=2))
    print_memory("After Script")
    
    # Extract scene
    scenes = script.get("scenes", [])
    if not scenes:
        print("No scenes generated! Exiting.")
        return
        
    scene = scenes[0]
    
    # 2. Audio
    print("\n--- 2. AUDIO GENERATION ---")
    t2 = time.time()
    audio_service = get_audio_service()
    try:
        audio_files = await audio_service.generate_scene_audio(scenes)
    except Exception as e:
        print("Audio failed:", str(e))
        audio_files = {}
        
    t3 = time.time()
    print(f"Audio generated in {t3-t2:.2f}s")
    print("Audio output:", audio_files)
    print_memory("After Audio")
    
    # 3. Image
    print("\n--- 3. IMAGE GENERATION ---")
    t4 = time.time()
    image_service = get_image_service()
    try:
        image_files = await image_service.generate_scene_images(scenes)
    except Exception as e:
        print("Image failed:", str(e))
        image_files = {}
        
    t5 = time.time()
    print(f"Image generated in {t5-t4:.2f}s")
    print("Image output:", image_files)
    print_memory("After Image")
    
    # 4. Video Rendering
    print("\n--- 4. VIDEO RENDERING ---")
    project_id = "test_project_1"
    
    scene_id = str(scene.get('scene_number', 1))
    audio_path = audio_files.get(scene_id) or audio_files.get(1) or audio_files.get('1')
    image_path = image_files.get(scene_id) or image_files.get(1) or image_files.get('1')
    
    if not audio_path or not image_path:
        print("Missing audio or image! Cannot render video.")
        print(f"Audio path: {audio_path}, Image path: {image_path}")
        return
        
    scene['audio_path'] = audio_path
    scene['image_path'] = image_path
    
    t6 = time.time()
    video_service = get_video_rendering_service()
    
    class MockWebsocket:
        async def send_json(self, data):
            print(f"Progress: {data}")
            
    try:
        final_video = await video_service.render_project(
            project_id=project_id,
            script_data={"scenes": [scene]},
            websocket=MockWebsocket()
        )
    except Exception as e:
        print("Video rendering failed:", str(e))
        final_video = None
        
    t7 = time.time()
    
    print(f"\nVideo rendered in {t7-t6:.2f}s")
    print(f"Final video path: {final_video}")
    print_memory("After Video")
    print(f"\n=== E2E TEST: COMPLETE in {t7-t0:.2f}s ===")

if __name__ == "__main__":
    asyncio.run(main())
