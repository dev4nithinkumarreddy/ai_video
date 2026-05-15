import openai
import logging
from typing import List, Dict, Any, Optional
import asyncio
import json
import time
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from utils.config import get_settings

logger = logging.getLogger(__name__)


class PromptTemplates:
    """Reusable prompt templates for different script styles"""
    
    SYSTEM_PROMPTS = {
        "cinematic": "You are an expert cinematic video script writer. Create visually stunning, emotionally engaging scripts with detailed scene descriptions perfect for AI video generation.",
        "professional": "You are an expert corporate video script writer. Generate professional, clear, and engaging scripts suitable for business presentations.",
        "educational": "You are an expert educational content creator. Write clear, informative, and engaging scripts that effectively teach complex concepts.",
        "marketing": "You are an expert marketing copywriter. Create compelling, persuasive video scripts that drive action and engagement.",
        "storytelling": "You are a master storyteller. Craft engaging narrative-driven video scripts that captivate audiences from start to finish."
    }
    
    SCRIPT_TEMPLATE = """Generate a video script with the following details:

Topic: {topic}
Description: {description}
Number of scenes: {num_scenes}
Style: {style}

Please generate a structured JSON response with the following format:
{{
    "title": "Engaging video title",
    "introduction": "Brief introduction text (2-3 sentences)",
    "scenes": [
        {{
            "scene_number": 1,
            "narration": "Scene narration text (clear, engaging voiceover)",
            "visual_prompt": "Detailed visual description for AI video generation (include lighting, camera angles, colors, mood, and specific visual elements)",
            "duration": 5,
            "camera_movement": "pan/zoom/static/tilt/track",
            "mood": "dramatic/calm/energetic/inspiring"
        }}
    ],
    "conclusion": "Brief conclusion text (1-2 sentences)",
    "estimated_duration": 30
}}

Make the script engaging and suitable for video production. The visual prompts should be highly detailed with specific camera angles, lighting descriptions, color palettes, and atmospheric details to ensure high-quality AI video generation.

IMPORTANT: Return ONLY the JSON object, no additional text or formatting."""
    
    SCENE_VARIATION_TEMPLATE = """Generate {variations} creative variations for this video scene:

Original Narration: {narration}
Original Visual Prompt: {visual_prompt}

Generate variations in JSON format:
{{
    "variations": [
        {{
            "narration": "Variation 1 narration (different tone or perspective)",
            "visual_prompt": "Variation 1 visual prompt (different composition, lighting, or mood)",
            "duration": 5,
            "camera_movement": "pan/zoom/static/tilt/track",
            "mood": "dramatic/calm/energetic/inspiring"
        }}
    ]
}}

Make each variation distinct and creative while maintaining the core message."""
    
    ENHANCE_PROMPT_TEMPLATE = """Enhance this visual prompt for AI video generation. Make it significantly more detailed and include technical terms for better AI understanding.

Original prompt: {visual_prompt}
Style: {style}

Add details about:
- Camera angles and movements
- Lighting conditions and color temperature
- Composition and framing
- Atmospheric elements and mood
- Specific objects, textures, and details
- Motion and animation suggestions

Provide only the enhanced prompt, no additional text."""


class OpenAIService:
    """Service for Groq API interactions with retry handling (OpenAI-compatible)"""
    
    def __init__(self):
        self.settings = get_settings()
        self._validate_configuration()
        # Use Groq's OpenAI-compatible API
        self.client = openai.AsyncOpenAI(
            api_key=self.settings.GROQ_API_KEY,
            base_url=self.settings.GROQ_BASE_URL or "https://api.groq.com/openai/v1"
        )
        self.templates = PromptTemplates()
    
    def _validate_configuration(self):
        """Validate Groq configuration"""
        if not self.settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is not configured in environment variables")
        if not self.settings.GROQ_BASE_URL:
            logger.warning("GROQ_BASE_URL not configured, using default")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((openai.APIError, openai.APIConnectionError, openai.RateLimitError)),
        reraise=True
    )
    async def generate_script(
        self,
        topic: str,
        description: str,
        num_scenes: int = 3,
        style: str = "professional"
    ) -> Dict[str, Any]:
        """
        Generate a complete video script using OpenAI API with retry handling
        
        Args:
            topic: The main topic of the video
            description: Detailed description of the video content
            num_scenes: Number of scenes to generate (1-10)
            style: Style of the script (professional, cinematic, educational, marketing, storytelling)
        
        Returns:
            Dictionary containing generated script data
        
        Raises:
            Exception: If script generation fails after retries
        """
        try:
            logger.info(f"Generating script for topic: {topic}, style: {style}, scenes: {num_scenes}")
            
            # Validate inputs
            if not topic or not topic.strip():
                raise ValueError("Topic cannot be empty")
            if not description or not description.strip():
                raise ValueError("Description cannot be empty")
            if not 1 <= num_scenes <= 10:
                raise ValueError("Number of scenes must be between 1 and 10")
            
            # Build prompt
            system_prompt = self.templates.SYSTEM_PROMPTS.get(style, self.templates.SYSTEM_PROMPTS["professional"])
            user_prompt = self.templates.SCRIPT_TEMPLATE.format(
                topic=topic,
                description=description,
                num_scenes=num_scenes,
                style=style
            )
            
            # Call Groq API with retry handling
            start_time = time.time()
            response = await self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            elapsed_time = time.time() - start_time
            
            script_content = response.choices[0].message.content
            parsed_script = self._parse_script_response(script_content)
            
            # Add metadata
            parsed_script['style'] = style
            parsed_script['generation_time'] = elapsed_time
            parsed_script['model_used'] = "llama3-70b-8192"
            
            logger.info(f"Successfully generated script in {elapsed_time:.2f}s with {len(parsed_script.get('scenes', []))} scenes")
            return parsed_script
            
        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            raise
        except openai.RateLimitError as e:
            logger.error(f"Groq rate limit error: {str(e)}")
            raise Exception("Groq rate limit exceeded. Please wait a moment and try again.")
        except openai.AuthenticationError as e:
            logger.error(f"Groq authentication error: {str(e)}")
            raise Exception("Invalid Groq API key. Please check your configuration.")
        except openai.APIError as e:
            logger.error(f"Groq API error: {str(e)}")
            raise Exception(f"Groq API error: {str(e)}")
        except Exception as e:
            logger.error(f"Error generating script: {str(e)}")
            raise Exception(f"Failed to generate script: {str(e)}")
    
    def _parse_script_response(self, response: str) -> Dict[str, Any]:
        """Parse the OpenAI response into structured data with multiple fallback strategies"""
        try:
            # Strategy 1: Try direct JSON parse
            if response.strip().startswith('{'):
                return json.loads(response)
            
            # Strategy 2: Extract JSON from markdown code blocks
            if '```json' in response:
                json_start = response.find('```json') + 7
                json_end = response.find('```', json_start)
                json_str = response[json_start:json_end].strip()
                return json.loads(json_str)
            
            # Strategy 3: Try to find JSON object in the response
            start_idx = response.find('{')
            end_idx = response.rfind('}')
            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx:end_idx + 1]
                return json.loads(json_str)
            
            # Fallback: create structured response from text
            logger.warning("Could not parse JSON from response, creating fallback structure")
            return self._create_fallback_structure(response)
            
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON response: {e}")
            return self._create_fallback_structure(response)
    
    def _create_fallback_structure(self, response: str) -> Dict[str, Any]:
        """Create a structured response when JSON parsing fails"""
        return {
            "title": "AI Generated Script",
            "introduction": response[:200] if len(response) > 200 else response,
            "scenes": [
                {
                    "scene_number": i + 1,
                    "narration": f"Scene {i + 1} - AI generated content",
                    "visual_prompt": f"Cinematic scene {i + 1} with professional lighting and composition",
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
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((openai.APIError, openai.APIConnectionError, openai.RateLimitError)),
        reraise=True
    )
    async def generate_scene_variations(
        self,
        scene: Dict[str, Any],
        variations: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Generate variations for a specific scene with retry handling
        
        Args:
            scene: Original scene data
            variations: Number of variations to generate (1-5)
        
        Returns:
            List of scene variations
        
        Raises:
            Exception: If variation generation fails after retries
        """
        try:
            logger.info(f"Generating {variations} variations for scene {scene.get('scene_number', 'unknown')}")
            
            if not 1 <= variations <= 5:
                raise ValueError("Number of variations must be between 1 and 5")
            
            prompt = self.templates.SCENE_VARIATION_TEMPLATE.format(
                variations=variations,
                narration=scene.get('narration', ''),
                visual_prompt=scene.get('visual_prompt', '')
            )
            
            response = await self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a creative script writer. Generate engaging variations of video scenes."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.8,
                max_tokens=1500
            )
            
            content = response.choices[0].message.content
            parsed = json.loads(content)
            
            logger.info(f"Generated {len(parsed.get('variations', []))} scene variations")
            return parsed.get('variations', [])
            
        except Exception as e:
            logger.error(f"Error generating scene variations: {str(e)}")
            raise Exception(f"Failed to generate variations: {str(e)}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((openai.APIError, openai.APIConnectionError, openai.RateLimitError)),
        reraise=True
    )
    async def enhance_visual_prompt(
        self,
        visual_prompt: str,
        style: str = "cinematic"
    ) -> str:
        """
        Enhance a visual prompt with more detail and AI-specific terms with retry handling
        
        Args:
            visual_prompt: Original visual prompt
            style: Style enhancement (cinematic, realistic, artistic, etc.)
        
        Returns:
            Enhanced visual prompt
        
        Raises:
            Exception: If prompt enhancement fails after retries
        """
        try:
            logger.info(f"Enhancing visual prompt with style: {style}")
            
            prompt = self.templates.ENHANCE_PROMPT_TEMPLATE.format(
                visual_prompt=visual_prompt,
                style=style
            )
            
            response = await self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at creating detailed visual prompts for AI video generation tools."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            enhanced = response.choices[0].message.content.strip()
            logger.info("Successfully enhanced visual prompt")
            return enhanced
            
        except Exception as e:
            logger.error(f"Error enhancing visual prompt: {str(e)}")
            raise Exception(f"Failed to enhance prompt: {str(e)}")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check if the Groq service is properly configured and accessible
        
        Returns:
            Health check status
        """
        try:
            # Simple test call to verify API key is valid
            response = await self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            
            return {
                "status": "healthy",
                "api_key_configured": True,
                "model_accessible": True,
                "model_used": response.model
            }
        except Exception as e:
            logger.error(f"Groq health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "api_key_configured": bool(self.settings.GROQ_API_KEY),
                "model_accessible": False,
                "error": str(e)
            }


# Singleton instance
_openai_service: Optional[OpenAIService] = None


def get_openai_service() -> OpenAIService:
    """Get or create OpenAI service instance"""
    global _openai_service
    if _openai_service is None:
        _openai_service = OpenAIService()
    return _openai_service
