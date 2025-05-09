import os
import random
import logging
from typing import List, Optional
from moviepy.editor import VideoFileClip

import config

logger = logging.getLogger(__name__)

class BackgroundManager:
    """Manage background videos for the Reddit video generator."""
    
    def __init__(self, background_dir: str = config.BACKGROUND_DIR):
        """
        Initialize the background manager.
        
        Args:
            background_dir: Directory containing background videos
        """
        self.background_dir = background_dir
        self.video_extensions = ['.mp4', '.avi', '.mov', '.mkv']
        logger.info(f"Background manager initialized with directory {background_dir}")
    
    def get_available_backgrounds(self) -> List[str]:
        """
        Get list of available background videos.
        
        Returns:
            List of paths to background videos
        """
        backgrounds = []
        
        if not os.path.exists(self.background_dir):
            logger.warning(f"Background directory {self.background_dir} does not exist")
            return backgrounds
            
        for filename in os.listdir(self.background_dir):
            file_path = os.path.join(self.background_dir, filename)
            if os.path.isfile(file_path) and any(filename.lower().endswith(ext) for ext in self.video_extensions):
                backgrounds.append(file_path)
                
        logger.info(f"Found {len(backgrounds)} background videos")
        return backgrounds
    
    def select_random_background(self) -> Optional[str]:
        """
        Select a random background video.
        
        Returns:
            Path to selected background video, or None if no backgrounds are available
        """
        backgrounds = self.get_available_backgrounds()
        
        if not backgrounds:
            logger.warning("No background videos available")
            return None
            
        selected = random.choice(backgrounds)
        logger.info(f"Selected background video: {selected}")
        return selected
    
    def get_background_clip(self, path: Optional[str] = None, duration: float = config.VIDEO_DURATION) -> Optional[VideoFileClip]:
        """
        Get a background video clip.
        
        Args:
            path: Path to background video (if None, a random one is selected)
            duration: Duration of the clip in seconds
            
        Returns:
            VideoFileClip object, or None if no background is available
        """
        if path is None:
            path = self.select_random_background()
            
        if not path or not os.path.exists(path):
            logger.error(f"Background video not found: {path}")
            return None
            
        try:
            # Load the video clip
            clip = VideoFileClip(path)
            
            # Resize to match target dimensions
            clip = clip.resize(height=config.VIDEO_HEIGHT)
            
            # Center crop to match target width
            clip_width = clip.w
            if clip_width > config.VIDEO_WIDTH:
                x_center = clip_width / 2
                x1 = x_center - (config.VIDEO_WIDTH / 2)
                clip = clip.crop(x1=x1, y1=0, x2=x1 + config.VIDEO_WIDTH, y2=config.VIDEO_HEIGHT)
            
            # Loop the clip if it's shorter than the target duration
            if clip.duration < duration:
                clip = clip.loop(duration=duration)
            
            # Trim if longer than target duration
            if clip.duration > duration:
                clip = clip.subclip(0, duration)
                
            logger.info(f"Background clip prepared (duration: {clip.duration}s)")
            return clip
        except Exception as e:
            logger.error(f"Error loading background video {path}: {e}")
            return None