import asyncio
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
import gc
import psutil
import httpx
import urllib.parse
from huggingface_hub import AsyncInferenceClient
from utils.config import get_settings

logger = logging.getLogger(__name__)

def log_memory(stage: str):
    mem = psutil.virtual_memory()
    logger.info(f"[MEMORY] {stage} - RAM Available: {mem.available / (1024**3):.2f} GB ({mem.percent}% used)")

class ImageService:
    def __init__(self):
        self.settings = get_settings()
        self.inference_mode = getattr(self.settings, 'INFERENCE_MODE', 'hosted')
        self.image_provider = getattr(self.settings, 'IMAGE_PROVIDER', 'pollinations')
        
        if self.inference_mode == "hosted" and self.image_provider == "hosted":
            self._validate_configuration()
            self.client = AsyncInferenceClient(token=self.settings.HUGGINGFACE_API_KEY)
            
        self.image_dir = Path("generated/images")
        self.image_dir.mkdir(parents=True, exist_ok=True)
        self.default_model = "stabilityai/stable-diffusion-xl-base-1.0"
    
    def _validate_configuration(self):
        if not self.settings.HUGGINGFACE_API_KEY:
            raise ValueError("HUGGINGFACE_API_KEY is not configured")
    
    async def generate_image(
        self,
        prompt: str,
        model: str = "stabilityai/stable-diffusion-xl-base-1.0",
        width: int = 512,
        height: int = 512,
        output_filename: Optional[str] = None,
        num_inference_steps: int = 20,
        guidance_scale: float = 7.5,
        negative_prompt: Optional[str] = None
    ) -> str:
        try:
            logger.info(f"Generating image. Provider: {self.image_provider}")
            
            if not output_filename:
                output_filename = f"image_{asyncio.get_event_loop().time()}.png"
            
            output_path = self.image_dir / output_filename
            
            if self.image_provider == "pollinations":
                encoded_prompt = urllib.parse.quote(prompt)
                url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true"
                async with httpx.AsyncClient() as client:
                    response = await client.get(url, timeout=60.0)
                    response.raise_for_status()
                    
                with open(output_path, "wb") as f:
                    f.write(response.content)
            elif self.inference_mode == "local" or self.image_provider == "local":
                log_memory("Before Image Model Load")
                
                def run_local_image():
                    from diffusers import StableDiffusionPipeline
                    import torch
                    
                    tiny_sd_model = "segmind/tiny-sd"
                    
                    pipe = StableDiffusionPipeline.from_pretrained(
                        tiny_sd_model, 
                        torch_dtype=torch.float32,
                        low_cpu_mem_usage=True,
                        safety_checker=None
                    )
                    pipe = pipe.to("cpu")
                    pipe.enable_attention_slicing()
                    
                    res_width = width if width else 512
                    res_height = height if height else 512
                    steps = min(num_inference_steps, 20)
                    
                    img = pipe(
                        prompt, 
                        negative_prompt=negative_prompt, 
                        width=res_width, 
                        height=res_height, 
                        num_inference_steps=steps, 
                        guidance_scale=guidance_scale
                    ).images[0]
                    
                    log_memory("Before Image Model Cleanup")
                    del pipe
                    gc.collect()
                    log_memory("After Image Model Cleanup")
                    
                    return img
                    
                image = await asyncio.to_thread(run_local_image)
                image.save(output_path)
            else:
                active_model = self.default_model if "stability-ai" in model else model
                if negative_prompt:
                    image = await self.client.text_to_image(prompt, model=active_model, negative_prompt=negative_prompt)
                else:
                    image = await self.client.text_to_image(prompt, model=active_model)
                image.save(output_path)
                
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error generating image: {str(e)}")
            raise Exception(f"Failed to generate image: {str(e)}")
    
    async def generate_scene_images(
        self,
        scenes: List[Dict[str, Any]],
        **kwargs
    ) -> Dict[str, str]:
        image_files = {}
        for scene in scenes:
            scene_id = scene.get('id', scene.get('scene_number'))
            visual_prompt = scene.get('visualPrompt', scene.get('visual_prompt', ''))
            if not visual_prompt:
                continue
            try:
                output_filename = f"scene_{scene_id}_{asyncio.get_event_loop().time()}.png"
                image_path = await self.generate_image(
                    prompt=visual_prompt,
                    output_filename=output_filename,
                    **kwargs
                )
                image_files[str(scene_id)] = image_path
                await asyncio.sleep(0.5)
            except Exception as e:
                logger.error(f"Failed to generate image for scene {scene_id}: {str(e)}")
                image_files[str(scene_id)] = None
        return image_files
    
    async def delete_image_file(self, file_path: str) -> bool:
        return False
    
    async def cleanup_old_images(self, max_age_hours: int = 24) -> int:
        return 0
    
    async def health_check(self) -> Dict[str, Any]:
        return {"status": "healthy"}
    
    async def close(self):
        pass

_image_service: Optional[ImageService] = None

def get_image_service() -> ImageService:
    global _image_service
    if _image_service is None:
        _image_service = ImageService()
    return _image_service
