import os
import logging
from typing import List, Dict, Any, Optional
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips, CompositeVideoClip
from tqdm import tqdm
import tempfile

import config
from .background import BackgroundManager
from .text_overlay import TextOverlayGenerator

logger = logging.getLogger(__name__)

class VideoCompositor:
    """Compose the final video from background video and text overlays."""
    
    def __init__(self, 
                background_manager: BackgroundManager = None,
                text_overlay_generator: TextOverlayGenerator = None,
                width: int = config.VIDEO_WIDTH,
                height: int = config.VIDEO_HEIGHT,
                fps: int = config.VIDEO_FPS):
        """
        Initialize the video compositor.
        
        Args:
            background_manager: BackgroundManager instance
            text_overlay_generator: TextOverlayGenerator instance
            width: Width of the video
            height: Height of the video
            fps: Frames per second
        """
        self.width = width
        self.height = height
        self.fps = fps
        self.background_manager = background_manager or BackgroundManager()
        self.text_overlay_generator = text_overlay_generator or TextOverlayGenerator()
        
        logger.info(f"Video compositor initialized ({width}x{height} at {fps} fps)")
    
    def _create_segment_clip(self, 
                           segment: Dict[str, Any], 
                           audio_path: str, 
                           background_path: Optional[str] = None) -> VideoFileClip:
        """
        Create a video clip for a single segment.
        
        Args:
            segment: Segment data
            audio_path: Path to the audio file for this segment
            background_path: Path to background video (optional)
            
        Returns:
            VideoFileClip for the segment
        """
        # Load audio and get its duration
        audio_clip = AudioFileClip(audio_path)
        duration = audio_clip.duration
        
        # Get background clip
        background_clip = self.background_manager.get_background_clip(background_path, duration)
        
        # If no background is available, create a black background
        if background_clip is None:
            from moviepy.editor import ColorClip
            background_clip = ColorClip(size=(self.width, self.height), color=(0, 0, 0))
            background_clip = background_clip.set_duration(duration)
        
        # Create appropriate overlay based on segment type
        segment_type = segment.get('type', '')
        if segment_type == 'title':
            overlay = self.text_overlay_generator.create_title_card(segment, duration)
        elif segment_type == 'comment':
            overlay = self.text_overlay_generator.create_comment_overlay(segment, duration)
        elif segment_type == 'post_content':
            overlay = self.text_overlay_generator.create_post_content_overlay(segment, duration)
        else:
            # Default to simple text overlay
            text = segment.get('text', 'No text available')
            overlay = self.text_overlay_generator.create_text_clip(text, duration=duration)
        
        # Composite background and overlay
        composite = CompositeVideoClip([background_clip, overlay])
        composite = composite.set_audio(audio_clip)
        composite = composite.set_duration(duration)
        
        logger.info(f"Created segment clip (type: {segment_type}, duration: {duration:.2f}s)")
        return composite
    
    def create_video(self, 
                   segments: List[Dict[str, Any]], 
                   audio_paths: List[str],
                   output_path: str,
                   single_background: bool = True) -> str:
        """
        Create the final video from segments and audio files.
        
        Args:
            segments: List of segment data
            audio_paths: List of paths to audio files (one per segment)
            output_path: Path to save the final video
            single_background: Whether to use a single background for the entire video
            
        Returns:
            Path to the created video file
        """
        if len(segments) != len(audio_paths):
            logger.error(f"Number of segments ({len(segments)}) does not match number of audio files ({len(audio_paths)})")
            return ""
            
        try:
            # Select a single background if requested
            background_path = self.background_manager.select_random_background() if single_background else None
            
            # Create clip for each segment
            segment_clips = []
            for i, (segment, audio_path) in enumerate(tqdm(zip(segments, audio_paths), total=len(segments), desc="Creating segments")):
                clip = self._create_segment_clip(segment, audio_path, background_path)
                segment_clips.append(clip)
                
            logger.info(f"Created {len(segment_clips)} segment clips")
            
            # Concatenate all segment clips
            final_clip = concatenate_videoclips(segment_clips)
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            
            # Write the final video file
            logger.info(f"Writing final video to {output_path} (duration: {final_clip.duration:.2f}s)")
            final_clip.write_videofile(output_path, fps=self.fps, threads=4, logger=None)
            
            # Close clips to free resources
            final_clip.close()
            for clip in segment_clips:
                clip.close()
                
            logger.info(f"Video creation complete: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error creating video: {e}")
            return ""