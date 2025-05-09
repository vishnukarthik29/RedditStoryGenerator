"""
Updated background.py with fixes for Pillow compatibility
"""
import os
import random
import logging
from PIL import Image, ImageFilter

class BackgroundManager:
    def __init__(self, backgrounds_dir):
        """Initialize the background manager with a directory of background videos/images."""
        self.backgrounds_dir = backgrounds_dir
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Background manager initialized with directory {backgrounds_dir}")
    
    def get_random_background(self):
        """Return a random background video or image from the backgrounds directory."""
        if not os.path.exists(self.backgrounds_dir):
            self.logger.warning(f"Backgrounds directory not found: {self.backgrounds_dir}")
            return None
        
        # Get all files in the backgrounds directory
        background_files = [f for f in os.listdir(self.backgrounds_dir) 
                           if f.endswith(('.mp4', '.mov', '.avi', '.png', '.jpg', '.jpeg'))]
        
        if not background_files:
            self.logger.warning(f"No background files found in {self.backgrounds_dir}")
            return None
        
        self.logger.info(f"Found {len(background_files)} background videos")
        
        # Select a random background
        selected_bg = os.path.join(self.backgrounds_dir, random.choice(background_files))
        self.logger.info(f"Selected background video: {selected_bg}")
        
        return selected_bg
    
    def resize_background(self, image, target_width, target_height):
        """Resize a background image to the target dimensions while maintaining aspect ratio."""
        try:
            # Calculate aspect ratios
            img_aspect = image.width / image.height
            target_aspect = target_width / target_height
            
            if img_aspect > target_aspect:
                # Image is wider than target, crop width
                new_width = int(target_aspect * image.height)
                left = (image.width - new_width) // 2
                image = image.crop((left, 0, left + new_width, image.height))
            elif img_aspect < target_aspect:
                # Image is taller than target, crop height
                new_height = int(image.width / target_aspect)
                top = (image.height - new_height) // 2
                image = image.crop((0, top, image.width, top + new_height))
            
            # Resize to target dimensions
            # Updated to use LANCZOS instead of ANTIALIAS
            return image.resize((target_width, target_height), Image.LANCZOS)
        
        except Exception as e:
            self.logger.error(f"Error resizing background image: {e}")
            return None
    
    def apply_blur(self, image, blur_radius=5):
        """Apply a blur effect to the background image."""
        try:
            return image.filter(ImageFilter.GaussianBlur(blur_radius))
        except Exception as e:
            self.logger.error(f"Error applying blur to background image: {e}")
            return image