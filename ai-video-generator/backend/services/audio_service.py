import asyncio
import logging
import aiofiles
import os
from pathlib import Path
from typing import Optional, Dict, Any
from elevenlabs import Voice, VoiceSettings
from elevenlabs.client import AsyncElevenLabs
import httpx

from utils.config import get_settings
from services.storage_service import get_storage_service

logger = logging.getLogger(__name__)


class AudioService:
    """Service for audio generation using ElevenLabs API"""
    
    def __init__(self):
        self.settings = get_settings()
        self.api_url = "https://api.elevenlabs.io/v1/text-to-speech"
        self.api_token = self.settings.ELEVENLABS_API_KEY
        self.storage_service = get_storage_service()
        self.client = AsyncElevenLabs(api_key=self.api_token)
        self._validate_configuration()
    
    def _validate_configuration(self):
        """Validate ElevenLabs configuration"""
        if not self.settings.ELEVENLABS_API_KEY:
            raise ValueError("ELEVENLABS_API_KEY is not configured in environment variables")
        logger.info("ElevenLabs API key configured")
    
    async def get_available_voices(self) -> list[Dict[str, Any]]:
        """
        Get list of available voices from ElevenLabs
        
        Returns:
            List of voice dictionaries
        """
        try:
            voices = await self.client.voices.get_all()
            return [
                {
                    "voice_id": voice.voice_id,
                    "name": voice.name,
                    "category": voice.category,
                    "labels": voice.labels
                }
                for voice in voices.voices
            ]
        except Exception as e:
            logger.error(f"Error fetching voices: {str(e)}")
            raise Exception(f"Failed to fetch voices: {str(e)}")
    
    async def generate_audio(
        self,
        text: str,
        voice_id: str = "21m00Tcm4TlvDq8ikWAM",  # Default: Rachel
        model_id: str = "eleven_multilingual_v2",
        output_filename: Optional[str] = None,
        project_id: str = "default",
        scene_id: str = "default"
    ) -> str:
        """
        Generate audio from text using ElevenLabs API
        
        Args:
            text: Text to convert to speech
            voice_id: ElevenLabs voice ID
            model_id: ElevenLabs model ID
            output_filename: Optional custom filename
            project_id: Project ID for storage organization
            scene_id: Scene ID for storage organization
        
        Returns:
            Path to generated audio file
        
        Raises:
            Exception: If audio generation fails
        """
        try:
            logger.info(f"Generating audio for text length: {len(text)} characters")
            
            # Generate audio using ElevenLabs
            audio_generator = await self.client.generate(
                text=text,
                voice=Voice(voice_id=voice_id),
                model=model_id
            )
            
            # Collect audio data
            audio_data = b""
            async for chunk in audio_generator:
                audio_data += chunk
            
            # Save using storage service
            file_path = await self.storage_service.save_audio(
                audio_data, project_id, scene_id, output_filename
            )
            
            logger.info(f"Audio generated successfully: {file_path}")
            return file_path
            
        except httpx.HTTPStatusError as e:
            logger.error(f"ElevenLabs HTTP error: {e.response.status_code}")
            if e.response.status_code == 401:
                raise Exception("Invalid ElevenLabs API key")
            elif e.response.status_code == 429:
                raise Exception("ElevenLabs rate limit exceeded")
            else:
                raise Exception(f"ElevenLabs API error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Error generating audio: {str(e)}")
            raise Exception(f"Failed to generate audio: {str(e)}")
    
    async def generate_audio_with_settings(
        self,
        text: str,
        voice_id: str = "21m00Tcm4TlvDq8ikWAM",
        model_id: str = "eleven_multilingual_v2",
        stability: float = 0.5,
        similarity_boost: float = 0.75,
        style: float = 0.0,
        use_speaker_boost: bool = False,
        output_filename: Optional[str] = None
    ) -> str:
        """
        Generate audio with custom voice settings
        
        Args:
            text: Text to convert to speech
            voice_id: ElevenLabs voice ID
            model_id: ElevenLabs model ID
            stability: Voice stability (0.0-1.0)
            similarity_boost: Similarity boost (0.0-1.0)
            style: Style enhancement (0.0-1.0)
            use_speaker_boost: Enable speaker boost
            output_filename: Optional custom filename
        
        Returns:
            Path to generated audio file
        """
        try:
            logger.info(f"Generating audio with custom settings")
            
            if not output_filename:
                output_filename = f"audio_{asyncio.get_event_loop().time()}.mp3"
            
            output_path = self.audio_dir / output_filename
            
            # Create voice settings
            voice_settings = VoiceSettings(
                stability=stability,
                similarity_boost=similarity_boost,
                style=style,
                use_speaker_boost=use_speaker_boost
            )
            
            # Generate audio with settings
            audio_generator = await self.client.generate(
                text=text,
                voice=Voice(voice_id=voice_id, settings=voice_settings),
                model=model_id
            )
            
            # Save audio to file
            async with aiofiles.open(output_path, 'wb') as audio_file:
                async for chunk in audio_generator:
                    await audio_file.write(chunk)
            
            logger.info(f"Audio generated with settings: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error generating audio with settings: {str(e)}")
            raise Exception(f"Failed to generate audio with settings: {str(e)}")
    
    async def generate_scene_audio(
        self,
        scenes: list[Dict[str, Any]],
        voice_id: str = "21m00Tcm4TlvDq8ikWAM",
        model_id: str = "eleven_multilingual_v2"
    ) -> Dict[str, str]:
        """
        Generate audio for multiple scenes
        
        Args:
            scenes: List of scene dictionaries with narration
            voice_id: ElevenLabs voice ID
            model_id: ElevenLabs model ID
        
        Returns:
            Dictionary mapping scene IDs to audio file paths
        """
        try:
            logger.info(f"Generating audio for {len(scenes)} scenes")
            
            audio_files = {}
            
            for scene in scenes:
                scene_id = scene.get('id', scene.get('scene_number'))
                narration = scene.get('narration', '')
                
                if not narration:
                    logger.warning(f"Scene {scene_id} has no narration, skipping")
                    continue
                
                try:
                    output_filename = f"scene_{scene_id}_{asyncio.get_event_loop().time()}.mp3"
                    audio_path = await self.generate_audio(
                        text=narration,
                        voice_id=voice_id,
                        model_id=model_id,
                        output_filename=output_filename
                    )
                    audio_files[str(scene_id)] = audio_path
                    
                    # Small delay to avoid rate limiting
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"Failed to generate audio for scene {scene_id}: {str(e)}")
                    audio_files[str(scene_id)] = None
            
            logger.info(f"Generated {len([f for f in audio_files.values() if f])}/{len(scenes)} audio files")
            return audio_files
            
        except Exception as e:
            logger.error(f"Error generating scene audio: {str(e)}")
            raise Exception(f"Failed to generate scene audio: {str(e)}")
    
    async def delete_audio_file(self, file_path: str) -> bool:
        """
        Delete an audio file
        
        Args:
            file_path: Path to audio file to delete
        
        Returns:
            True if deleted successfully
        """
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                logger.info(f"Deleted audio file: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting audio file: {str(e)}")
            return False
    
    async def cleanup_old_audio_files(self, max_age_hours: int = 24) -> int:
        """
        Clean up old audio files
        
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
            
            for file_path in self.audio_dir.glob("*.mp3"):
                file_age = current_time - file_path.stat().st_mtime
                if file_age > max_age_seconds:
                    file_path.unlink()
                    deleted_count += 1
                    logger.info(f"Deleted old audio file: {file_path.name}")
            
            logger.info(f"Cleaned up {deleted_count} old audio files")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up audio files: {str(e)}")
            return 0
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check if the ElevenLabs service is properly configured
        
        Returns:
            Health check status
        """
        try:
            # Try to fetch voices to verify API key
            await self.client.voices.get_all()
            
            return {
                "status": "healthy",
                "api_key_configured": True,
                "service_accessible": True,
                "audio_directory": str(self.audio_dir)
            }
        except Exception as e:
            logger.error(f"ElevenLabs health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "api_key_configured": bool(self.settings.ELEVENLABS_API_KEY),
                "service_accessible": False,
                "error": str(e)
            }


# Singleton instance
_audio_service: Optional[AudioService] = None


def get_audio_service() -> AudioService:
    """Get or create audio service instance"""
    global _audio_service
    if _audio_service is None:
        _audio_service = AudioService()
    return _audio_service
