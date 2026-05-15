from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from enum import Enum


class VoiceGender(str, Enum):
    """Voice gender options"""
    MALE = "male"
    FEMALE = "female"
    NEUTRAL = "neutral"


class VoiceAccent(str, Enum):
    """Voice accent options"""
    AMERICAN = "american"
    BRITISH = "british"
    AUSTRALIAN = "australian"
    INDIAN = "indian"
    CANADIAN = "canadian"


class AudioModel(str, Enum):
    """ElevenLabs model options"""
    ELEVEN_MONOLINGUAL_V1 = "eleven_monolingual_v1"
    ELEVEN_MULTILINGUAL_V1 = "eleven_multilingual_v1"
    ELEVEN_MULTILINGUAL_V2 = "eleven_multilingual_v2"
    ELEVEN_TURBO_V2 = "eleven_turbo_v2"


class GenerateAudioRequest(BaseModel):
    """Request model for audio generation"""
    text: str = Field(..., min_length=1, max_length=5000, description="Text to convert to speech")
    voice_id: str = Field(default="21m00Tcm4TlvDq8ikWAM", description="ElevenLabs voice ID")
    model_id: AudioModel = Field(default=AudioModel.ELEVEN_MULTILINGUAL_V2, description="ElevenLabs model ID")
    output_filename: Optional[str] = Field(None, description="Custom output filename")
    
    @field_validator('text')
    @classmethod
    def validate_text(cls, v):
        if not v.strip():
            raise ValueError('Text cannot be empty or whitespace only')
        return v.strip()
    
    @field_validator('output_filename')
    @classmethod
    def validate_filename(cls, v):
        if v and not v.endswith('.mp3'):
            return f"{v}.mp3"
        return v


class VoiceSettings(BaseModel):
    """Voice settings for audio generation"""
    stability: float = Field(default=0.5, ge=0.0, le=1.0, description="Voice stability (0.0-1.0)")
    similarity_boost: float = Field(default=0.75, ge=0.0, le=1.0, description="Similarity boost (0.0-1.0)")
    style: float = Field(default=0.0, ge=0.0, le=1.0, description="Style enhancement (0.0-1.0)")
    use_speaker_boost: bool = Field(default=False, description="Enable speaker boost")


class GenerateAudioWithSettingsRequest(BaseModel):
    """Request model for audio generation with custom settings"""
    text: str = Field(..., min_length=1, max_length=5000, description="Text to convert to speech")
    voice_id: str = Field(default="21m00Tcm4TlvDq8ikWAM", description="ElevenLabs voice ID")
    model_id: AudioModel = Field(default=AudioModel.ELEVEN_MULTILINGUAL_V2, description="ElevenLabs model ID")
    settings: VoiceSettings = Field(default_factory=VoiceSettings, description="Voice settings")
    output_filename: Optional[str] = Field(None, description="Custom output filename")
    
    @field_validator('text')
    @classmethod
    def validate_text(cls, v):
        if not v.strip():
            raise ValueError('Text cannot be empty or whitespace only')
        return v.strip()


class Scene(BaseModel):
    """Scene model for batch audio generation"""
    id: str = Field(..., description="Scene ID")
    narration: str = Field(..., min_length=1, description="Scene narration text")
    
    @field_validator('narration')
    @classmethod
    def validate_narration(cls, v):
        if not v.strip():
            raise ValueError('Narration cannot be empty or whitespace only')
        return v.strip()


class GenerateSceneAudioRequest(BaseModel):
    """Request model for batch scene audio generation"""
    scenes: List[Scene] = Field(..., description="List of scenes")
    voice_id: str = Field(default="21m00Tcm4TlvDq8ikWAM", description="ElevenLabs voice ID")
    model_id: AudioModel = Field(default=AudioModel.ELEVEN_MULTILINGUAL_V2, description="ElevenLabs model ID")
    
    @field_validator('scenes')
    @classmethod
    def validate_scenes(cls, v):
        if not v or len(v) < 1:
            raise ValueError('At least one scene is required')
        return v


class GenerateAudioResponse(BaseModel):
    """Response model for audio generation"""
    success: bool = Field(..., description="Generation success status")
    audio_file_path: str = Field(..., description="Path to generated audio file")
    voice_id: str = Field(..., description="Voice ID used")
    model_id: str = Field(..., description="Model ID used")
    text_length: int = Field(..., description="Length of input text")
    file_size: Optional[int] = Field(None, description="Size of generated file in bytes")


class GenerateSceneAudioResponse(BaseModel):
    """Response model for batch scene audio generation"""
    success: bool = Field(..., description="Overall success status")
    audio_files: Dict[str, Optional[str]] = Field(..., description="Scene ID to audio file path mapping")
    total_scenes: int = Field(..., description="Total number of scenes")
    successful_generations: int = Field(..., description="Number of successful generations")
    failed_generations: int = Field(..., description="Number of failed generations")


class VoiceInfo(BaseModel):
    """Voice information model"""
    voice_id: str = Field(..., description="Voice ID")
    name: str = Field(..., description="Voice name")
    category: Optional[str] = Field(None, description="Voice category")
    labels: Optional[Dict[str, Any]] = Field(None, description="Voice labels")


class VoicesResponse(BaseModel):
    """Response model for available voices"""
    voices: List[VoiceInfo] = Field(..., description="List of available voices")
    total_count: int = Field(..., description="Total number of voices")


class DeleteAudioRequest(BaseModel):
    """Request model for deleting audio files"""
    file_path: str = Field(..., description="Path to audio file to delete")


class DeleteAudioResponse(BaseModel):
    """Response model for audio deletion"""
    success: bool = Field(..., description="Deletion success status")
    file_path: str = Field(..., description="Path to deleted file")
    message: str = Field(..., description="Deletion message")


class CleanupRequest(BaseModel):
    """Request model for cleanup operation"""
    max_age_hours: int = Field(default=24, ge=1, description="Maximum age of files to keep in hours")


class CleanupResponse(BaseModel):
    """Response model for cleanup operation"""
    success: bool = Field(..., description="Cleanup success status")
    files_deleted: int = Field(..., description="Number of files deleted")
    max_age_hours: int = Field(..., description="Maximum age used for cleanup")
