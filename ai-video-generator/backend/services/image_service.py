import asyncio
import logging
import aiofiles
import os
from pathlib import Path
from typing import Optional, Dict, Any, List
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import httpx

from utils.config import get_settings

logger = logging.getLogger(__name__)


class ImageService:
    """Service for AI image generation using Replicate API"""
    
    def __init__(self):
        self.settings = get_settings()
        self._validate_configuration()
        self.api_url = "https://api.replicate.com/v1/predictions"
        self.api_token = self.settings.REPLICATE_API_TOKEN
        self.image_dir = Path("generated/images")
        self._ensure_image_directory()
        self.client = httpx.AsyncClient(
            headers={"Authorization": f"Token {self.api_token}"}
        )
    
    def _validate_configuration(self):
        """Validate Replicate configuration"""
        if not self.settings.REPLICATE_API_TOKEN:
            raise ValueError("REPLICATE_API_TOKEN is not configured in environment variables")
        logger.info("Replicate API token configured")
    
    def _ensure_image_directory(self):
        """Ensure image directory exists"""
        self.image_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Image directory ready: {self.image_dir}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.TimeoutException)),
        reraise=True
    )
    async def generate_image(
        self,
        prompt: str,
        model: str = "stability-ai/sdxl",
        width: int = 1920,
        height: int = 1080,
        output_filename: Optional[str] = None,
        num_inference_steps: int = 50,
        guidance_scale: float = 7.5,
        negative_prompt: Optional[str] = None
    ) -> str:
        """
        Generate a cinematic image using Replicate API
        
        Args:
            prompt: Text description for image generation
            model: Replicate model ID (default: stability-ai/sdxl)
            width: Image width (default: 1920 for HD)
            height: Image height (default: 1080 for HD)
            output_filename: Optional custom filename
            num_inference_steps: Number of inference steps (higher = better quality)
            guidance_scale: How closely to follow the prompt
            negative_prompt: What to avoid in the image
        
        Returns:
            Path to generated image file
        
        Raises:
            Exception: If image generation fails after retries
        """
        try:
            logger.info(f"Generating image with prompt length: {len(prompt)}")
            
            # Generate output filename if not provided
            if not output_filename:
                output_filename = f"image_{asyncio.get_event_loop().time()}.png"
            
            output_path = self.image_dir / output_filename
            
            # Create prediction request
            input_data = {
                "prompt": prompt,
                "width": width,
                "height": height,
                "num_inference_steps": num_inference_steps,
                "guidance_scale": guidance_scale
            }
            
            if negative_prompt:
                input_data["negative_prompt"] = negative_prompt
            
            # Start prediction
            response = await self.client.post(
                self.api_url,
                json={
                    "version": self._get_model_version(model),
                    "input": input_data
                }
            )
            response.raise_for_status()
            prediction = response.json()
            
            # Poll for result
            image_url = await self._poll_prediction(prediction["urls"]["get"])
            
            # Download image
            await self._download_image(image_url, output_path)
            
            logger.info(f"Image generated successfully: {output_path}")
            return str(output_path)
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Replicate HTTP error: {e.response.status_code}")
            if e.response.status_code == 401:
                raise Exception("Invalid Replicate API token")
            elif e.response.status_code == 429:
                raise Exception("Replicate rate limit exceeded")
            elif e.response.status_code == 402:
                raise Exception("Insufficient Replicate credits")
            else:
                raise Exception(f"Replicate API error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Error generating image: {str(e)}")
            raise Exception(f"Failed to generate image: {str(e)}")
    
    def _get_model_version(self, model: str) -> str:
        """Get model version hash"""
        model_versions = {
            "stability-ai/sdxl": "39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
            "stability-ai/stable-diffusion": "21c35431c21e4e3a8a5f67e05e1e8f9d6d6c9c9a9a9a9a9a9a9a9a9a9a9a",
            "midjourney": "a9758cb8d458518d8c3c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c"
        }
        return model_versions.get(model, model_versions["stability-ai/sdxl"])
    
    async def _poll_prediction(self, get_url: str, max_wait: int = 300) -> str:
        """
        Poll prediction until completion
        
        Args:
            get_url: URL to poll for prediction status
            max_wait: Maximum wait time in seconds
        
        Returns:
            Image URL from prediction result
        """
        start_time = asyncio.get_event_loop().time()
        
        while True:
            if asyncio.get_event_loop().time() - start_time > max_wait:
                raise Exception("Image generation timeout")
            
            response = await self.client.get(get_url)
            response.raise_for_status()
            prediction = response.json()
            
            if prediction["status"] == "succeeded":
                return prediction["output"][0]
            elif prediction["status"] == "failed":
                raise Exception(f"Image generation failed: {prediction.get('error', 'Unknown error')}")
            elif prediction["status"] in ["starting", "processing"]:
                await asyncio.sleep(2)
            else:
                raise Exception(f"Unknown prediction status: {prediction['status']}")
    
    async def _download_image(self, url: str, output_path: Path):
        """
        Download image from URL to local file
        
        Args:
            url: Image URL
            output_path: Local file path
        """
        async with self.client.stream("GET", url) as response:
            response.raise_for_status()
            async with aiofiles.open(output_path, 'wb') as file:
                async for chunk in response.aiter_bytes():
                    await file.write(chunk)
    
    async def generate_scene_images(
        self,
        scenes: List[Dict[str, Any]],
        model: str = "stability-ai/sdxl",
        width: int = 1920,
        height: int = 1080,
        negative_prompt: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Generate images for multiple scenes
        
        Args:
            scenes: List of scene dictionaries with visual prompts
            model: Replicate model ID
            width: Image width
            height: Image height
            negative_prompt: Optional negative prompt
        
        Returns:
            Dictionary mapping scene IDs to image file paths
        """
        try:
            logger.info(f"Generating images for {len(scenes)} scenes")
            
            image_files = {}
            
            for scene in scenes:
                scene_id = scene.get('id', scene.get('scene_number'))
                visual_prompt = scene.get('visualPrompt', scene.get('visual_prompt', ''))
                
                if not visual_prompt:
                    logger.warning(f"Scene {scene_id} has no visual prompt, skipping")
                    continue
                
                try:
                    output_filename = f"scene_{scene_id}_{asyncio.get_event_loop().time()}.png"
                    image_path = await self.generate_image(
                        prompt=visual_prompt,
                        model=model,
                        width=width,
                        height=height,
                        output_filename=output_filename,
                        negative_prompt=negative_prompt
                    )
                    image_files[str(scene_id)] = image_path
                    
                    # Small delay to avoid rate limiting
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Failed to generate image for scene {scene_id}: {str(e)}")
                    image_files[str(scene_id)] = None
            
            logger.info(f"Generated {len([f for f in image_files.values() if f])}/{len(scenes)} images")
            return image_files
            
        except Exception as e:
            logger.error(f"Error generating scene images: {str(e)}")
            raise Exception(f"Failed to generate scene images: {str(e)}")
    
    async def delete_image_file(self, file_path: str) -> bool:
        """
        Delete an image file
        
        Args:
            file_path: Path to image file to delete
        
        Returns:
            True if deleted successfully
        """
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                logger.info(f"Deleted image file: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting image file: {str(e)}")
            return False
    
    async def cleanup_old_images(self, max_age_hours: int = 24) -> int:
        """
        Clean up old image files
        
        Args:
            max_age_hours: Maximum age of files to keep (in hours)
        
        Returns:
            Number of files deleted
        """
        try:
            import time
            
            deleted_count = 0
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            
            for file_path in self.image_dir.glob("*.png"):
                file_age = current_time - file_path.stat().st_mtime
                if file_age > max_age_seconds:
                    file_path.unlink()
                    deleted_count += 1
                    logger.info(f"Deleted old image file: {file_path.name}")
            
            logger.info(f"Cleaned up {deleted_count} old image files")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up image files: {str(e)}")
            return 0
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check if the Replicate service is properly configured
        
        Returns:
            Health check status
        """
        try:
            # Try a simple API call to verify token
            response = await self.client.get("https://api.replicate.com/v1/collections")
            response.raise_for_status()
            
            return {
                "status": "healthy",
                "api_token_configured": True,
                "service_accessible": True,
                "image_directory": str(self.image_dir)
            }
        except Exception as e:
            logger.error(f"Replicate health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "api_token_configured": bool(self.settings.REPLICATE_API_TOKEN),
                "service_accessible": False,
                "error": str(e)
            }
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


# Singleton instance
_image_service: Optional[ImageService] = None


def get_image_service() -> ImageService:
    """Get or create image service instance"""
    global _image_service
    if _image_service is None:
        _image_service = ImageService()
    return _image_service
