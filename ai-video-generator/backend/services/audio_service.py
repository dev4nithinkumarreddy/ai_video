import asyncio
import logging
import os
import io
import gc
import psutil
from pathlib import Path
from typing import Optional, Dict, Any
from huggingface_hub import AsyncInferenceClient
from huggingface_hub.errors import HfHubHTTPError
import scipy.io.wavfile as wavfile

from utils.config import get_settings
from services.storage_service import get_storage_service

logger = logging.getLogger(__name__)

def log_memory(stage: str):
    mem = psutil.virtual_memory()
    logger.info(f"[MEMORY] {stage} - RAM Available: {mem.available / (1024**3):.2f} GB ({mem.percent}% used)")

class AudioService:
    def __init__(self):
        self.settings = get_settings()
        self.inference_mode = getattr(self.settings, 'INFERENCE_MODE', 'hosted')
        
        if self.inference_mode == "hosted":
            self._validate_configuration()
            self.client = AsyncInferenceClient(token=self.settings.HUGGINGFACE_API_KEY)
            
        self.storage_service = get_storage_service()
        self.audio_dir = Path("generated/audio")
        self.audio_dir.mkdir(parents=True, exist_ok=True)
        self.default_model = "facebook/mms-tts-eng"
    
    def _validate_configuration(self):
        if not self.settings.HUGGINGFACE_API_KEY:
            raise ValueError("HUGGINGFACE_API_KEY is not configured")
    
    async def get_available_voices(self) -> list[Dict[str, Any]]:
        return [{"voice_id": "facebook/mms-tts-eng", "name": "MMS English", "category": "Standard", "labels": {}}]
    
    async def generate_audio(
        self,
        text: str,
        voice_id: str = "facebook/mms-tts-eng",
        model_id: str = "default",
        output_filename: Optional[str] = None,
        project_id: str = "default",
        scene_id: str = "default"
    ) -> str:
        try:
            logger.info(f"Generating audio for text length: {len(text)}")
            if self.inference_mode == "local":
                log_memory("Before Audio Model Load")
                
                def run_local_audio():
                    from transformers import VitsModel, AutoTokenizer
                    import torch
                    tokenizer = AutoTokenizer.from_pretrained("facebook/mms-tts-eng")
                    model = VitsModel.from_pretrained("facebook/mms-tts-eng")
                    
                    inputs = tokenizer(text, return_tensors="pt")
                    with torch.no_grad():
                        output = model(**inputs).waveform
                    
                    # Convert to wav bytes
                    import scipy.io.wavfile as wavfile
                    import io
                    wav_io = io.BytesIO()
                    wavfile.write(wav_io, model.config.sampling_rate, output.squeeze().numpy())
                    audio_res = wav_io.getvalue()
                    
                    log_memory("Before Audio Model Cleanup")
                    del model
                    del tokenizer
                    del inputs
                    del output
                    gc.collect()
                    log_memory("After Audio Model Cleanup")
                    
                    return audio_res

                audio_bytes = await asyncio.to_thread(run_local_audio)
                
                if not output_filename:
                    output_filename = f"audio_{asyncio.get_event_loop().time()}.wav"
                else:
                    output_filename = output_filename.replace('.mp3', '.wav')
            else:
                model_name = voice_id if voice_id.startswith("facebook") else self.default_model
                audio_bytes = await self.client.text_to_speech(text, model=model_name)
            
            file_path = await self.storage_service.save_audio(
                audio_bytes, project_id, scene_id, output_filename
            )
            return file_path
            
        except Exception as e:
            logger.error(f"Error generating audio: {str(e)}")
            raise Exception(f"Failed to generate audio: {str(e)}")
    
    async def generate_audio_with_settings(self, text: str, **kwargs) -> str:
        return await self.generate_audio(text=text, output_filename=kwargs.get('output_filename'))
    
    async def generate_scene_audio(self, scenes: list[Dict[str, Any]], **kwargs) -> Dict[str, str]:
        audio_files = {}
        for scene in scenes:
            scene_id = scene.get('id', scene.get('scene_number'))
            narration = scene.get('narration', '')
            if not narration:
                continue
            try:
                ext = ".wav" if self.inference_mode == "local" else ".mp3"
                output_filename = f"scene_{scene_id}_{asyncio.get_event_loop().time()}{ext}"
                audio_path = await self.generate_audio(text=narration, output_filename=output_filename)
                audio_files[str(scene_id)] = audio_path
                await asyncio.sleep(0.1)
            except Exception as e:
                logger.error(f"Failed to generate audio for scene {scene_id}: {str(e)}")
                audio_files[str(scene_id)] = None
        return audio_files
    
    async def delete_audio_file(self, file_path: str) -> bool:
        return False
    
    async def cleanup_old_audio_files(self, max_age_hours: int = 24) -> int:
        return 0
    
    async def health_check(self) -> Dict[str, Any]:
        return {"status": "healthy"}

_audio_service: Optional[AudioService] = None

def get_audio_service() -> AudioService:
    global _audio_service
    if _audio_service is None:
        _audio_service = AudioService()
    return _audio_service
