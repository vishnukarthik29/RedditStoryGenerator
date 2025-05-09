# Step 1: First, let's look at the entire file structure and find all instances of getsize

# Run these commands in the terminal to find all instances:
# cd C:\Users\vk\Desktop\Reddit Story Generator
# findstr /s "getsize" video\text_overlay.py

# Or use this Python script to find all instances:
import re

with open(r"C:\Users\vk\Desktop\Reddit Story Generator\video\text_overlay.py", "r") as file:
    content = file.read()
    
matches = re.findall(r"\.getsize\(", content)
print(f"Found {len(matches)} instances of .getsize()")

# Step 2: Create a complete replacement for text_overlay.py
# Replace the entire file content with this updated version:

import os
import textwrap
from PIL import Image, ImageDraw, ImageFont

class TextOverlayGenerator:
    def __init__(self, font_path=None, font_size=40, text_color=(255, 255, 255)):
        """Initialize the text overlay generator."""
        if font_path is None:
            font_path = os.path.join(os.path.dirname(__file__), "../assets/fonts/Roboto-Regular.ttf")
        
        self.font_path = font_path
        self.font_size = font_size
        self.font = ImageFont.truetype(font_path, font_size)
        self.text_color = text_color
        self.padding = 50
        self.line_spacing = 10
        
        # Log initialization
        import logging
        self.logger = logging.getLogger(__name__)
        self.logger.info("Text overlay generator initialized")
    
    def get_font_dimensions(self, text):
        """Helper function to get text dimensions that works with both old and new Pillow versions"""
        try:
            # For older Pillow versions
            return self.font.getsize(text)
        except AttributeError:
            # For newer Pillow versions (9.2.0+)
            bbox = self.font.getbbox(text)
            width = bbox[2] - bbox[0]  # right - left
            height = bbox[3] - bbox[1]  # bottom - top
            return width, height
    
    def create_text_overlay(self, text, width, height):
        """Create a text overlay image with the specified text."""
        # Create a transparent image
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Calculate the maximum width for text
        max_text_width = width - (self.padding * 2)
        
        # Wrap text to fit within the width
        wrapped_text = self._wrap_text(text, max_text_width)
        
        # Calculate total text height
        total_height = 0
        for line in wrapped_text:
            line_width, line_height = self.get_font_dimensions(line)
            total_height += line_height + self.line_spacing
        
        # Remove last line spacing
        if total_height > 0:
            total_height -= self.line_spacing
        
        # Calculate starting y position to center text vertically
        y = (height - total_height) // 2
        
        # Draw each line of text
        for line in wrapped_text:
            line_width, line_height = self.get_font_dimensions(line)
            x = (width - line_width) // 2  # Center text horizontally
            draw.text((x, y), line, font=self.font, fill=self.text_color)
            y += line_height + self.line_spacing
        
        return img
    
    def _wrap_text(self, text, max_width):
        """Wrap text to fit within max_width."""
        words = text.split()
        wrapped_lines = []
        current_line = []
        
        for word in words:
            # Try adding the word to the current line
            test_line = ' '.join(current_line + [word])
            line_width, _ = self.get_font_dimensions(test_line)
            
            if line_width <= max_width:
                # Word fits, add it to the current line
                current_line.append(word)
            else:
                # Word doesn't fit, start a new line
                if current_line:
                    wrapped_lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    # If the word is too long by itself, force it onto its own line
                    wrapped_lines.append(word)
        
        # Add the last line if there is one
        if current_line:
            wrapped_lines.append(' '.join(current_line))
        
        return wrapped_lines