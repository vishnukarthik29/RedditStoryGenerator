"""
Updated text_overlay.py with fixes for Pillow compatibility
"""
import os
import textwrap
import logging
from PIL import Image, ImageDraw, ImageFont

class TextOverlayGenerator:
    def __init__(self, font_path=None, font_size=40, text_color=(255, 255, 255)):
        """Initialize the text overlay generator."""
        self.logger = logging.getLogger(__name__)
        
        # Try to load the specified font
        self.font = None
        if font_path and os.path.exists(font_path):
            try:
                self.font = ImageFont.truetype(font_path, font_size)
            except Exception as e:
                self.logger.warning(f"Failed to load font {font_path}: {e}")
        
        # Use default font if specified font not available
        if self.font is None:
            try:
                # Try to use a system font
                self.font = ImageFont.truetype("arial.ttf", font_size)
            except Exception:
                try:
                    # Try DejaVuSans as a fallback
                    self.font = ImageFont.truetype("DejaVuSans.ttf", font_size)
                except Exception:
                    # Last resort: use default font
                    self.font = ImageFont.load_default()
                    self.logger.warning(f"Font file not found: {font_path}. Using default font.")
        
        self.text_color = text_color
        self.font_size = font_size
        self.logger.info("Text overlay generator initialized")
    
    def create_text_overlay(self, text, width, height, padding=20, line_spacing=10):
        """Create an image with text overlay."""
        # Create a transparent image
        overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Calculate maximum text width
        max_text_width = width - (2 * padding)
        
        # Wrap text to fit within the width
        wrapped_text = self._wrap_text(text, max_text_width)
        
        # Calculate text dimensions
        # Updated to use getsize instead of textsize
        text_height = 0
        longest_line_width = 0
        line_heights = []
        
        for line in wrapped_text:
            # Using font.getsize as the replacement for draw.textsize
            line_width, line_height = self.font.getsize(line)
            line_heights.append(line_height)
            text_height += line_height + line_spacing
            longest_line_width = max(longest_line_width, line_width)
        
        # Remove the last line spacing
        if wrapped_text:
            text_height -= line_spacing
        
        # Calculate text position (centered)
        x = (width - longest_line_width) // 2
        y = (height - text_height) // 2
        
        # Draw text
        current_y = y
        for i, line in enumerate(wrapped_text):
            draw.text((x, current_y), line, font=self.font, fill=self.text_color)
            current_y += line_heights[i] + line_spacing
        
        return overlay
    
    def _wrap_text(self, text, max_width):
        """Wrap text to fit within a given width."""
        wrapped_lines = []
        
        # Split text into paragraphs
        paragraphs = text.split('\n')
        
        for paragraph in paragraphs:
            if not paragraph:
                wrapped_lines.append('')
                continue
            
            # Start with a reasonable character estimate
            avg_char_width = self.font_size * 0.6  # Rough estimate
            chars_per_line = int(max_width / avg_char_width)
            
            # Use textwrap to wrap the paragraph
            lines = textwrap.wrap(paragraph, width=chars_per_line)
            
            # Adjust wrapping if needed
            final_lines = []
            for line in lines:
                # Using font.getsize as the replacement for draw.textsize
                line_width, _ = self.font.getsize(line)
                
                if line_width <= max_width:
                    final_lines.append(line)
                else:
                    # Further split the line if it's still too long
                    words = line.split()
                    current_line = words[0]
                    
                    for word in words[1:]:
                        test_line = current_line + " " + word
                        test_width, _ = self.font.getsize(test_line)
                        
                        if test_width <= max_width:
                            current_line = test_line
                        else:
                            final_lines.append(current_line)
                            current_line = word
                    
                    final_lines.append(current_line)
            
            wrapped_lines.extend(final_lines)
        
        return wrapped_lines