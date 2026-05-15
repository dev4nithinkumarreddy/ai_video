import asyncio
import logging
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any, List
import json
import time

from utils.config import get_settings

logger = logging.getLogger(__name__)


class VideoRenderingService:
    """Service for video rendering using FFmpeg"""
    
    def __init__(self):
        self.settings = get_settings()
        self.video_dir = Path("generated/videos")
        self.temp_dir = Path("temp/video_rendering")
        self._ensure_directories()
        self._check_ffmpeg_availability()
    
    def _ensure_directories(self):
        """Ensure necessary directories exist"""
        self.video_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Video directories ready: {self.video_dir}, {self.temp_dir}")
    
    def _check_ffmpeg_availability(self):
        """Check if FFmpeg is available"""
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                logger.info("FFmpeg is available")
            else:
                raise Exception("FFmpeg not found")
        except subprocess.TimeoutExpired:
            raise Exception("FFmpeg command timed out")
        except FileNotFoundError:
            raise Exception("FFmpeg not found. Please install FFmpeg.")
    
    async def render_video(
        self,
        scenes: List[Dict[str, Any]],
        output_filename: Optional[str] = None,
        fps: int = 30,
        resolution: str = "1920x1080",
        transition_type: str = "fade",
        transition_duration: float = 0.5,
        add_subtitles: bool = True,
        background_music: Optional[str] = None
    ) -> str:
        """
        Render a complete video from scenes using FFmpeg
        
        Args:
            scenes: List of scene dictionaries with image, audio, narration, duration
            output_filename: Optional custom output filename
            fps: Frames per second
            resolution: Video resolution (width x height)
            transition_type: Type of transition between scenes
            transition_duration: Duration of transitions in seconds
            add_subtitles: Whether to add subtitles
            background_music: Optional background music file path
        
        Returns:
            Path to rendered video file
        
        Raises:
            Exception: If video rendering fails
        """
        try:
            logger.info(f"Starting video rendering for {len(scenes)} scenes")
            
            # Generate output filename if not provided
            if not output_filename:
                output_filename = f"video_{int(time.time())}.mp4"
            
            output_path = self.video_dir / output_filename
            
            # Create temporary directory for this render
            render_id = f"render_{int(time.time())}"
            temp_render_dir = self.temp_dir / render_id
            temp_render_dir.mkdir(exist_ok=True)
            
            # Step 1: Prepare scene videos
            scene_videos = await self._prepare_scene_videos(
                scenes, temp_render_dir, fps, resolution
            )
            
            # Step 2: Create video concatenation list
            concat_list = await self._create_concatenation_list(
                scene_videos, temp_render_dir, transition_type, transition_duration
            )
            
            # Step 3: Concatenate scenes
            temp_video_path = temp_render_dir / "concatenated_video.mp4"
            await self._concatenate_videos(concat_list, temp_video_path)
            
            # Step 4: Add audio
            temp_audio_path = temp_render_dir / "with_audio.mp4"
            await self._add_audio_to_video(
                temp_video_path, scenes, temp_audio_path, background_music
            )
            
            # Step 5: Add subtitles if requested
            temp_with_subtitles_path = temp_render_dir / "with_subtitles.mp4"
            if add_subtitles:
                await self._add_subtitles_to_video(
                    temp_audio_path, scenes, temp_with_subtitles_path
                )
                final_temp_path = temp_with_subtitles_path
            else:
                final_temp_path = temp_audio_path
            
            # Step 6: Move to final location
            final_path = output_path
            os.rename(final_temp_path, final_path)
            
            # Cleanup temporary files
            await self._cleanup_temp_files(temp_render_dir)
            
            logger.info(f"Video rendering completed: {final_path}")
            return str(final_path)
            
        except Exception as e:
            logger.error(f"Error rendering video: {str(e)}")
            raise Exception(f"Failed to render video: {str(e)}")
    
    async def _prepare_scene_videos(
        self,
        scenes: List[Dict[str, Any]],
        temp_dir: Path,
        fps: int,
        resolution: str
    ) -> List[str]:
        """Prepare individual scene videos from images"""
        scene_videos = []
        
        for i, scene in enumerate(scenes):
            try:
                scene_id = scene.get('id', f"scene_{i}")
                image_path = scene.get('image_path')
                duration = scene.get('duration', 5)
                
                if not image_path or not os.path.exists(image_path):
                    logger.warning(f"Image not found for scene {scene_id}: {image_path}")
                    continue
                
                # Create scene video from image
                scene_video_path = temp_dir / f"scene_{i}.mp4"
                await self._create_scene_video(
                    image_path, scene_video_path, duration, fps, resolution
                )
                
                scene_videos.append(str(scene_video_path))
                logger.info(f"Created scene video: {scene_video_path}")
                
            except Exception as e:
                logger.error(f"Error preparing scene video {i}: {str(e)}")
                continue
        
        return scene_videos
    
    async def _create_scene_video(
        self,
        image_path: str,
        output_path: Path,
        duration: float,
        fps: int,
        resolution: str
    ):
        """Create a video from a single image"""
        cmd = [
            "ffmpeg",
            "-y",  # Overwrite output file
            "-loop", "1",
            "-i", image_path,
            "-t", str(duration),
            "-vf", f"scale={resolution},fps={fps}",
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "23",
            str(output_path)
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise Exception(f"FFmpeg scene video creation failed: {stderr.decode()}")
    
    async def _create_concatenation_list(
        self,
        scene_videos: List[str],
        temp_dir: Path,
        transition_type: str,
        transition_duration: float
    ) -> str:
        """Create FFmpeg concatenation list with transitions"""
        concat_file = temp_dir / "concat_list.txt"
        
        with open(concat_file, 'w') as f:
            for i, video_path in enumerate(scene_videos):
                f.write(f"file '{video_path}'\n")
                f.write(f"duration {transition_duration}\n")
        
        return str(concat_file)
    
    async def _concatenate_videos(self, concat_list: str, output_path: Path):
        """Concatenate videos using FFmpeg concat demuxer"""
        cmd = [
            "ffmpeg",
            "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_list,
            "-c", "copy",
            str(output_path)
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise Exception(f"FFmpeg concatenation failed: {stderr.decode()}")
    
    async def _add_audio_to_video(
        self,
        video_path: Path,
        scenes: List[Dict[str, Any]],
        output_path: Path,
        background_music: Optional[str] = None
    ):
        """Add narration audio and optional background music to video"""
        # Create temporary audio file
        temp_audio_path = video_path.parent / "combined_audio.mp3"
        
        # Combine all scene audio files
        await self._combine_scene_audio(scenes, temp_audio_path, background_music)
        
        # Add audio to video
        cmd = [
            "ffmpeg",
            "-y",
            "-i", str(video_path),
            "-i", str(temp_audio_path),
            "-c:v", "copy",
            "-c:a", "aac",
            "-shortest",
            str(output_path)
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        # Cleanup temporary audio file
        if temp_audio_path.exists():
            temp_audio_path.unlink()
        
        if process.returncode != 0:
            raise Exception(f"FFmpeg audio addition failed: {stderr.decode()}")
    
    async def _combine_scene_audio(
        self,
        scenes: List[Dict[str, Any]],
        output_path: Path,
        background_music: Optional[str] = None
    ):
        """Combine scene audio files with optional background music"""
        audio_files = []
        
        # Collect all scene audio files
        for scene in scenes:
            audio_path = scene.get('audio_path')
            if audio_path and os.path.exists(audio_path):
                audio_files.append(audio_path)
        
        if not audio_files:
            # Create silent audio if no narration
            total_duration = sum(scene.get('duration', 5) for scene in scenes)
            await self._create_silent_audio(total_duration, output_path)
            return
        
        # Concatenate audio files
        if len(audio_files) == 1:
            os.rename(audio_files[0], output_path)
        else:
            await self._concatenate_audio_files(audio_files, output_path)
        
        # Add background music if provided
        if background_music and os.path.exists(background_music):
            temp_with_music = output_path.parent / "with_music.mp3"
            await self._add_background_music(output_path, background_music, temp_with_music)
            os.rename(temp_with_music, output_path)
    
    async def _create_silent_audio(self, duration: float, output_path: Path):
        """Create silent audio of specified duration"""
        cmd = [
            "ffmpeg",
            "-y",
            "-f", "lavfi",
            "-i", "anullsrc=r=44100:cl=mono",
            "-t", str(duration),
            str(output_path)
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise Exception(f"FFmpeg silent audio creation failed: {stderr.decode()}")
    
    async def _concatenate_audio_files(self, audio_files: List[str], output_path: Path):
        """Concatenate multiple audio files"""
        # Create concat list
        concat_file = output_path.parent / "audio_concat.txt"
        with open(concat_file, 'w') as f:
            for audio_file in audio_files:
                f.write(f"file '{audio_file}'\n")
        
        cmd = [
            "ffmpeg",
            "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_file),
            "-c", "copy",
            str(output_path)
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        # Cleanup concat file
        if concat_file.exists():
            concat_file.unlink()
        
        if process.returncode != 0:
            raise Exception(f"FFmpeg audio concatenation failed: {stderr.decode()}")
    
    async def _add_background_music(
        self,
        narration_path: Path,
        music_path: str,
        output_path: Path
    ):
        """Add background music to narration audio"""
        cmd = [
            "ffmpeg",
            "-y",
            "-i", str(narration_path),
            "-i", music_path,
            "-filter_complex", "[0:a][1:a]amix=inputs=2:weights=1 0.3",
            str(output_path)
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise Exception(f"FFmpeg background music addition failed: {stderr.decode()}")
    
    async def _add_subtitles_to_video(
        self,
        video_path: Path,
        scenes: List[Dict[str, Any]],
        output_path: Path
    ):
        """Add subtitles to video"""
        # Create subtitle file
        subtitle_file = video_path.parent / "subtitles.srt"
        await self._create_subtitle_file(scenes, subtitle_file)
        
        # Add subtitles to video
        cmd = [
            "ffmpeg",
            "-y",
            "-i", str(video_path),
            "-vf", f"subtitles={subtitle_file}",
            "-c:a", "copy",
            str(output_path)
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        # Cleanup subtitle file
        if subtitle_file.exists():
            subtitle_file.unlink()
        
        if process.returncode != 0:
            raise Exception(f"FFmpeg subtitle addition failed: {stderr.decode()}")
    
    async def _create_subtitle_file(self, scenes: List[Dict[str, Any]], output_path: Path):
        """Create SRT subtitle file from scenes"""
        current_time = 0
        subtitle_content = []
        
        for i, scene in enumerate(scenes):
            narration = scene.get('narration', '')
            duration = scene.get('duration', 5)
            
            if not narration:
                continue
            
            start_time = self._format_time(current_time)
            end_time = self._format_time(current_time + duration)
            
            subtitle_content.append(f"{i + 1}")
            subtitle_content.append(f"{start_time} --> {end_time}")
            subtitle_content.append(narration)
            subtitle_content.append("")
            
            current_time += duration
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(subtitle_content))
    
    def _format_time(self, seconds: float) -> str:
        """Format time in seconds to SRT time format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milliseconds = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"
    
    async def _cleanup_temp_files(self, temp_dir: Path):
        """Clean up temporary files"""
        try:
            for file_path in temp_dir.glob("*"):
                file_path.unlink()
            temp_dir.rmdir()
        except Exception as e:
            logger.warning(f"Error cleaning up temp files: {str(e)}")
    
    async def get_video_info(self, video_path: str) -> Dict[str, Any]:
        """Get video information using FFprobe"""
        cmd = [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            video_path
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise Exception(f"FFprobe failed: {stderr.decode()}")
        
        return json.loads(stdout.decode())
    
    async def health_check(self) -> Dict[str, Any]:
        """Check if FFmpeg is available and working"""
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return {
                    "status": "healthy",
                    "ffmpeg_available": True,
                    "video_directory": str(self.video_dir),
                    "temp_directory": str(self.temp_dir)
                }
            else:
                return {
                    "status": "unhealthy",
                    "ffmpeg_available": False,
                    "error": "FFmpeg command failed"
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "ffmpeg_available": False,
                "error": str(e)
            }


# Singleton instance
_video_rendering_service: Optional[VideoRenderingService] = None


def get_video_rendering_service() -> VideoRenderingService:
    """Get or create video rendering service instance"""
    global _video_rendering_service
    if _video_rendering_service is None:
        _video_rendering_service = VideoRenderingService()
    return _video_rendering_service
