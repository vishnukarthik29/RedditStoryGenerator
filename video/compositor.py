"""
Updated compositor.py to properly initialize the BackgroundManager with a backgrounds_dir parameter
"""
import os
import logging
import tempfile
import uuid
from typing import List, Dict, Optional, Any
from moviepy.editor import VideoFileClip, ImageClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips

from .background import BackgroundManager
from .text_overlay import TextOverlayGenerator

class VideoCompositor:
    def __init__(self, 
                 width: int = 1080, 
                 height: int = 1920, 
                 fps: int = 30,
                 background_manager = None,
                 text_overlay = None):
        """
        Initialize the video compositor.
        
        Args:
            width: Width of the output video
            height: Height of the output video
            fps: Frames per second of the output video
            background_manager: BackgroundManager instance to use
            text_overlay: TextOverlayGenerator instance to use
        """
        self.width = width
        self.height = height
        self.fps = fps
        self.logger = logging.getLogger(__name__)
        
        # Define default backgrounds directory - needed for BackgroundManager initialization
        self.assets_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
        self.backgrounds_dir = os.path.join(self.assets_dir, "backgrounds")
        
        # Fix: Initialize BackgroundManager with backgrounds_dir parameter
        self.background_manager = background_manager or BackgroundManager(self.backgrounds_dir)
        self.text_overlay = text_overlay or TextOverlayGenerator()
        
        self.logger.info(f"Video compositor initialized ({width}x{height} at {fps} fps)")
    
    def generate_video(self, 
                       segments: List[Dict[str, Any]], 
                       background_manager: Optional[BackgroundManager] = None,
                       text_overlay: Optional[TextOverlayGenerator] = None,
                       output_file: str = None) -> str:
        """
        Generate a video from the given segments.
        
        Args:
            segments: List of segment dictionaries with 'text' and 'audio' keys
            background_manager: BackgroundManager instance to use
            text_overlay: TextOverlayGenerator instance to use
            output_file: Path to the output video file
            
        Returns:
            Path to the output video file
        """
        # Use provided instances or fall back to instance variables
        background_mgr = background_manager or self.background_manager
        text_overlay_gen = text_overlay or self.text_overlay
        
        # Create a temporary output file if none provided
        if not output_file:
            output_file = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4()}.mp4")
        
        # Create video clips for each segment
        self.logger.info(f"Creating {len(segments)} video segments")
        video_clips = []
        
        for i, segment in enumerate(segments):
            if 'audio' not in segment:
                self.logger.warning(f"Segment {i} has no audio, skipping")
                continue
            
            clip = self._create_segment_clip(
                segment, 
                background_mgr,
                text_overlay_gen
            )
            
            if clip:
                video_clips.append(clip)
        
        if not video_clips:
            self.logger.error("No valid video clips created")
            return None
        
        # Concatenate all clips
        self.logger.info("Concatenating video clips")
        final_clip = concatenate_videoclips(video_clips, method="compose")
        
        # Write the final video
        self.logger.info(f"Writing video to {output_file}")
        final_clip.write_videofile(output_file, fps=self.fps, codec="libx264")
        
        # Close all clips
        for clip in video_clips:
            clip.close()
        final_clip.close()
        
        return output_file
    
    def _create_segment_clip(self, 
                            segment: Dict[str, Any],
                            background_manager: BackgroundManager,
                            text_overlay: TextOverlayGenerator) -> Optional[CompositeVideoClip]:
        """
        Create a video clip for a single segment.
        
        Args:
            segment: Segment dictionary with 'text' and 'audio' keys
            background_manager: BackgroundManager instance to use
            text_overlay: TextOverlayGenerator instance to use
            
        Returns:
            CompositeVideoClip for the segment or None if failed
        """
        try:
            # Load audio
            audio_clip = AudioFileClip(segment['audio'])
            duration = audio_clip.duration
            
            # Get background
            bg_path = background_manager.get_random_background()
            
            if not bg_path or not os.path.exists(bg_path):
                self.logger.error(f"Background file not found: {bg_path}")
                return None
            
            # Create background clip
            bg_clip = None
            if bg_path.endswith(('.mp4', '.mov', '.avi')):
                bg_clip = VideoFileClip(bg_path).loop(duration=duration)
            elif bg_path.endswith(('.png', '.jpg', '.jpeg')):
                bg_clip = ImageClip(bg_path).set_duration(duration)
            else:
                self.logger.error(f"Unsupported background file format: {bg_path}")
                return None
            
            # Resize and crop background to fit dimensions
            bg_clip = bg_clip.resize(height=self.height)
            bg_clip = bg_clip.crop(x_center=bg_clip.w/2, y_center=bg_clip.h/2, 
                                  width=self.width, height=self.height)
            
            # Create text overlay
            text_img = text_overlay.create_text_overlay(segment['text'], self.width, self.height)
            text_clip = ImageClip(text_img).set_duration(duration)
            
            # Combine background and text
            composite_clip = CompositeVideoClip([bg_clip, text_clip])
            
            # Add audio
            composite_clip = composite_clip.set_audio(audio_clip)
            
            return composite_clip
            
        except Exception as e:
            self.logger.error(f"Error creating segment clip: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return None