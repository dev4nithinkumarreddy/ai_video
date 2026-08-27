import logging
from typing import List, Dict, Any, Optional
import asyncio
import json
import time
import gc
import psutil
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from huggingface_hub import AsyncInferenceClient
from huggingface_hub.errors import HfHubHTTPError
from utils.config import get_settings

logger = logging.getLogger(__name__)

def log_memory(stage: str):
    mem = psutil.virtual_memory()
    logger.info(f"[MEMORY] {stage} - RAM Available: {mem.available / (1024**3):.2f} GB ({mem.percent}% used)")

class PromptTemplates:
    SYSTEM_PROMPTS = {
        "cinematic": "You are an expert cinematic video script writer.",
        "professional": "You are an expert corporate video script writer.",
        "educational": "You are an expert educational content creator.",
        "marketing": "You are an expert marketing copywriter.",
        "storytelling": "You are a master storyteller."
    }
    SCRIPT_TEMPLATE = """Topic: {topic}
Description: {description}
Number of scenes: {num_scenes}

Respond with ONLY a JSON object:
{{
    "title": "Title",
    "introduction": "Intro",
    "scenes": [
        {{
            "scene_number": 1,
            "narration": "Narration text",
            "visual_prompt": "Visual description",
            "duration": 5,
            "camera_movement": "static",
            "mood": "calm"
        }}
    ],
    "conclusion": "Conclusion text",
    "estimated_duration": 30
}}"""

    SCENE_VARIATION_TEMPLATE = """Original Narration: {narration}
Original Visual Prompt: {visual_prompt}

Generate {variations} variations in JSON format:
{{
    "variations": [
        {{
            "narration": "...",
            "visual_prompt": "...",
            "duration": 5,
            "camera_movement": "static",
            "mood": "calm"
        }}
    ]
}}"""

    ENHANCE_PROMPT_TEMPLATE = """Enhance this visual prompt: {visual_prompt}
Style: {style}
Respond with only the enhanced prompt."""

class OpenAIService:
    def __init__(self):
        self.settings = get_settings()
        self.inference_mode = getattr(self.settings, 'INFERENCE_MODE', 'hosted')
        
        if self.inference_mode == "hosted":
            self._validate_configuration()
            self.client = AsyncInferenceClient(token=self.settings.HUGGINGFACE_API_KEY)
            self.model = "meta-llama/Llama-3.1-8B-Instruct"
        else:
            logger.info("OpenAIService running in LOCAL mode")
            
        self.templates = PromptTemplates()
    
    def _validate_configuration(self):
        if not self.settings.HUGGINGFACE_API_KEY:
            raise ValueError("HUGGINGFACE_API_KEY is not configured")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(HfHubHTTPError),
        reraise=True
    )
    async def generate_script(
        self,
        topic: str,
        description: str,
        num_scenes: int = 3,
        style: str = "professional"
    ) -> Dict[str, Any]:
        try:
            logger.info(f"Generating script for topic: {topic}")
            user_prompt = self.templates.SCRIPT_TEMPLATE.format(
                topic=topic,
                description=description,
                num_scenes=num_scenes,
                style=style
            )
            system_prompt = self.templates.SYSTEM_PROMPTS.get(style, self.templates.SYSTEM_PROMPTS["professional"])
            
            start_time = time.time()
            if self.inference_mode == "local":
                log_memory("Before Text Model Load")
                
                def run_local_text():
                    from transformers import pipeline
                    pipe = pipeline("text-generation", model="Qwen/Qwen2.5-0.5B-Instruct", device="cpu")
                    messages = [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ]
                    res = pipe(messages, max_new_tokens=1000, temperature=0.7, return_full_text=False)
                    script_res = res[0]['generated_text']
                    
                    # Cleanup
                    log_memory("Before Text Model Cleanup")
                    del pipe
                    gc.collect()
                    log_memory("After Text Model Cleanup")
                    
                    return script_res
                
                script_content = await asyncio.to_thread(run_local_text)
                model_used = "local/Qwen2.5-0.5B-Instruct"
            else:
                response = await self.client.chat_completion(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.7,
                    max_tokens=2000
                )
                script_content = response.choices[0].message.content
                model_used = self.model
                
            elapsed_time = time.time() - start_time
            parsed_script = self._parse_script_response(script_content)
            
            parsed_script['style'] = style
            parsed_script['generation_time'] = elapsed_time
            parsed_script['model_used'] = model_used
            
            return parsed_script
            
        except Exception as e:
            logger.error(f"Error generating script: {str(e)}")
            raise Exception(f"Failed to generate script: {str(e)}")
    
    def _parse_script_response(self, response: str) -> Dict[str, Any]:
        try:
            if response.strip().startswith('{'):
                return json.loads(response)
            if '```json' in response:
                json_start = response.find('```json') + 7
                json_end = response.find('```', json_start)
                return json.loads(response[json_start:json_end].strip())
            start_idx = response.find('{')
            end_idx = response.rfind('}')
            if start_idx != -1 and end_idx != -1:
                return json.loads(response[start_idx:end_idx + 1])
            return self._create_fallback_structure(response)
        except Exception as e:
            logger.warning(f"Failed to parse JSON response: {e}")
            return self._create_fallback_structure(response)
    
    def _create_fallback_structure(self, response: str) -> Dict[str, Any]:
        return {
            "title": "AI Generated Script",
            "introduction": response[:200] if len(response) > 200 else response,
            "scenes": [
                {
                    "scene_number": i + 1,
                    "narration": f"Scene {i + 1} narration",
                    "visual_prompt": f"Scene {i + 1} visual",
                    "duration": 5,
                    "camera_movement": "static",
                    "mood": "professional"
                }
                for i in range(3)
            ],
            "conclusion": "Thank you for watching",
            "estimated_duration": 15,
            "raw_response": response,
            "parsing_fallback": True
        }
    
    async def generate_scene_variations(self, scene: Dict[str, Any], variations: int = 3) -> List[Dict[str, Any]]:
        return []
    
    async def enhance_visual_prompt(self, visual_prompt: str, style: str = "cinematic") -> str:
        return visual_prompt
    
    async def health_check(self) -> Dict[str, Any]:
        return {"status": "healthy"}

_openai_service: Optional[OpenAIService] = None

def get_openai_service() -> OpenAIService:
    global _openai_service
    if _openai_service is None:
        _openai_service = OpenAIService()
    return _openai_service
