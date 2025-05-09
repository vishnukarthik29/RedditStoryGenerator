import os
import textwrap
import logging
from PIL import Image, ImageDraw, ImageFont
from typing import Tuple, Dict, Any, List, Optional
from moviepy.editor import TextClip, ImageClip, CompositeVideoClip, ColorClip

import config

logger = logging.getLogger(__name__)

class TextOverlayGenerator:
    """Generate text overlays for Reddit videos."""
    
    def __init__(self, 
                font_path: str = config.DEFAULT_FONT, 
                text_color: str = config.TEXT_COLOR,
                shadow_color: str = config.SHADOW_COLOR,
                width: int = config.VIDEO_WIDTH,
                height: int = config.VIDEO_HEIGHT):
        """
        Initialize the text overlay generator.
        
        Args:
            font_path: Path to font file
            text_color: Color of the text
            shadow_color: Color of the text shadow
            width: Width of the video
            height: Height of the video
        """
        self.font_path = font_path
        self.text_color = text_color
        self.shadow_color = shadow_color
        self.width = width
        self.height = height
        
        # Ensure font file exists
        if not os.path.exists(self.font_path):
            logger.warning(f"Font file not found: {self.font_path}. Using default font.")
            self.font_path = None
            
        logger.info("Text overlay generator initialized")
    
    def _calculate_max_font_size(self, text: str, max_width: int, max_height: int) -> int:
        """
        Calculate the maximum font size that fits within the given dimensions.
        
        Args:
            text: Text to measure
            max_width: Maximum width available
            max_height: Maximum height available
            
        Returns:
            Font size that fits
        """
        font_size = 120  # Start with a large font size
        min_font_size = 24  # Don't go smaller than this
        
        # Create a temporary image for font measurement
        temp_img = Image.new('RGB', (1, 1))
        temp_draw = ImageDraw.Draw(temp_img)
        
        # Reduce font size until text fits
        while font_size > min_font_size:
            font = ImageFont.truetype(self.font_path, font_size) if self.font_path else ImageFont.load_default()
            text_width, text_height = temp_draw.textsize(text, font=font)
            
            if text_width <= max_width and text_height <= max_height:
                break
                
            font_size -= 2
            
        return font_size
    
    def _wrap_text(self, text: str, font_size: int, max_width: int) -> List[str]:
        """
        Wrap text to fit within max_width.
        
        Args:
            text: Text to wrap
            font_size: Font size
            max_width: Maximum width in pixels
            
        Returns:
            List of wrapped text lines
        """
        font = ImageFont.truetype(self.font_path, font_size) if self.font_path else ImageFont.load_default()
        
        # Calculate average character width
        temp_img = Image.new('RGB', (1, 1))
        temp_draw = ImageDraw.Draw(temp_img)
        avg_char_width = temp_draw.textsize('x', font=font)[0]
        
        # Estimate characters per line
        chars_per_line = max(1, int(max_width / avg_char_width * 0.9))
        
        # Wrap text
        wrapped_lines = textwrap.wrap(text, width=chars_per_line)
        
        return wrapped_lines
    
    def create_text_clip(self, text: str, position: Tuple[str, str] = ('center', 'center'), 
                        duration: float = 5.0, font_size: Optional[int] = None) -> TextClip:
        """
        Create a text clip for the video.
        
        Args:
            text: Text to display
            position: Position of the text ('center', 'center') by default
            duration: Duration of the clip in seconds
            font_size: Font size (calculated automatically if None)
            
        Returns:
            TextClip object
        """
        # Set default margins
        margin = 50
        max_width = self.width - (2 * margin)
        max_height = self.height // 3  # Use at most 1/3 of the screen height
        
        if font_size is None:
            font_size = self._calculate_max_font_size(text, max_width, max_height)
        
        # Wrap text
        wrapped_text = '\n'.join(self._wrap_text(text, font_size, max_width))
        
        try:
            # Create text clip with shadow for better visibility
            txt_clip = TextClip(wrapped_text, font=self.font_path, fontsize=font_size, 
                              color=self.text_color, align='center', method='label')
            
            # Create shadow clip (slightly offset)
            shadow_clip = TextClip(wrapped_text, font=self.font_path, fontsize=font_size, 
                                 color=self.shadow_color, align='center', method='label')
            
            # Composite text with shadow
            final_clip = CompositeVideoClip([
                shadow_clip.set_position((position[0] + 2, position[1] + 2)),
                txt_clip.set_position(position)
            ])
            
            final_clip = final_clip.set_duration(duration)
            
            logger.info(f"Created text clip with {len(wrapped_text.split())} words")
            return final_clip
        except Exception as e:
            logger.error(f"Error creating text clip: {e}")
            # Fallback to simpler text clip without shadow
            txt_clip = TextClip(wrapped_text, fontsize=font_size, 
                              color=self.text_color, align='center')
            txt_clip = txt_clip.set_position(position).set_duration(duration)
            return txt_clip
    
    def create_title_card(self, segment: Dict[str, Any], duration: float) -> CompositeVideoClip:
        """
        Create a title card for the video.
        
        Args:
            segment: Segment data containing title and metadata
            duration: Duration of the clip in seconds
            
        Returns:
            CompositeVideoClip object
        """
        # Create background
        background = ColorClip(size=(self.width, self.height), color=(30, 30, 30))
        background = background.set_duration(duration)
        
        # Create title text
        title_text = segment['text']
        title_clip = self.create_text_clip(
            title_text, 
            position=('center', self.height // 3), 
            duration=duration,
            font_size=60
        )
        
        # Create subreddit text
        subreddit_text = f"r/{segment['subreddit']}"
        subreddit_clip = self.create_text_clip(
            subreddit_text,
            position=('center', self.height // 3 + title_clip.h + 50),
            duration=duration,
            font_size=40
        )
        
        # Create author text
        author_text = f"Posted by u/{segment['author']}"
        author_clip = self.create_text_clip(
            author_text,
            position=('center', self.height // 3 + title_clip.h + subreddit_clip.h + 100),
            duration=duration,
            font_size=32
        )
        
        # Composite all clips
        composite = CompositeVideoClip([
            background,
            title_clip,
            subreddit_clip,
            author_clip
        ])
        
        logger.info(f"Created title card for '{title_text[:30]}...'")
        return composite
    
    def create_comment_overlay(self, segment: Dict[str, Any], duration: float) -> CompositeVideoClip:
        """
        Create a comment overlay for the video.
        
        Args:
            segment: Segment data containing comment and metadata
            duration: Duration of the clip in seconds
            
        Returns:
            CompositeVideoClip object
        """
        # Create semi-transparent background
        background = ColorClip(size=(self.width - 100, self.height // 2), color=(30, 30, 30))
        background = background.set_opacity(0.8).set_duration(duration)
        background = background.set_position(('center', 'center'))
        
        # Create comment text
        comment_text = segment['text']
        comment_clip = self.create_text_clip(
            comment_text, 
            position=(self.width // 2, background.pos(0)[1] + 50), 
            duration=duration,
            font_size=42
        )
        
        # Create author text
        author_text = f"u/{segment['author']} • {segment['score']} points"
        author_clip = self.create_text_clip(
            author_text,
            position=(self.width // 2, background.pos(0)[1] + background.h - 50),
            duration=duration,
            font_size=30
        )
        
        # Composite all clips
        composite = CompositeVideoClip([
            background,
            comment_clip,
            author_clip
        ])
        
        logger.info(f"Created comment overlay for comment #{segment['comment_number']}")
        return composite
    
    def create_post_content_overlay(self, segment: Dict[str, Any], duration: float) -> CompositeVideoClip:
        """
        Create a post content overlay for the video.
        
        Args:
            segment: Segment data containing post content and metadata
            duration: Duration of the clip in seconds
            
        Returns:
            CompositeVideoClip object
        """
        # Create semi-transparent background
        background = ColorClip(size=(self.width - 100, self.height // 2), color=(30, 30, 30))
        background = background.set_opacity(0.8).set_duration(duration)
        background = background.set_position(('center', 'center'))
        
        # Create content text
        content_text = segment['text']
        content_clip = self.create_text_clip(
            content_text, 
            position=(self.width // 2, background.pos(0)[1] + 50), 
            duration=duration,
            font_size=42
        )
        
        # Create part indicator if there are multiple parts
        if segment.get('total_parts', 1) > 1:
            part_text = f"Part {segment['part']}/{segment['total_parts']}"
            part_clip = self.create_text_clip(
                part_text,
                position=(self.width // 2, background.pos(0)[1] + background.h - 50),
                duration=duration,
                font_size=30
            )
            
            # Composite all clips with part indicator
            composite = CompositeVideoClip([
                background,
                content_clip,
                part_clip
            ])
        else:
            # Composite without part indicator
            composite = CompositeVideoClip([
                background,
                content_clip
            ])
        
        logger.info(f"Created post content overlay for part {segment.get('part', 1)}")
        return composite