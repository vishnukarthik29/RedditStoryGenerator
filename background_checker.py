"""
Check for background assets and create a sample background if none exists.
"""
import os
import sys
import numpy as np
from PIL import Image

def check_backgrounds():
    """Check for background assets and create a sample if none exists."""
    project_dir = os.path.dirname(os.path.abspath(__file__))
    backgrounds_dir = os.path.join(project_dir, "assets", "backgrounds")
    
    # Create the backgrounds directory if it doesn't exist
    if not os.path.exists(backgrounds_dir):
        print(f"Creating backgrounds directory: {backgrounds_dir}")
        os.makedirs(backgrounds_dir, exist_ok=True)
    
    # Check if there are any background files
    background_files = [f for f in os.listdir(backgrounds_dir) 
                       if f.endswith(('.mp4', '.mov', '.avi', '.png', '.jpg', '.jpeg'))]
    
    if not background_files:
        print("No background files found. Creating a sample background image...")
        
        # Create a simple gradient background
        width, height = 1080, 1920
        
        # Create a gradient array
        x = np.linspace(0, 1, width)
        y = np.linspace(0, 1, height)
        X, Y = np.meshgrid(x, y)
        Z = (X + Y) / 2.0
        
        # Convert to RGB image
        img_array = np.stack([
            Z * 0 + 0.1,  # R channel - dark blue
            Z * 0.2 + 0.2,  # G channel - medium blue
            Z * 0.4 + 0.6  # B channel - light blue gradient
        ], axis=2)
        
        # Scale to 0-255 and convert to uint8
        img_array = (img_array * 255).astype(np.uint8)
        
        # Create the PIL image
        img = Image.fromarray(img_array)
        
        # Save the image
        background_path = os.path.join(backgrounds_dir, "sample_background.jpg")
        img.save(background_path)
        
        print(f"Created sample background image: {background_path}")
        
        return [background_path]
    else:
        print(f"Found {len(background_files)} background files:")
        for file in background_files:
            print(f"  - {file}")
        
        return [os.path.join(backgrounds_dir, f) for f in background_files]

def check_fonts():
    """Check for font files and create the fonts directory if it doesn't exist."""
    project_dir = os.path.dirname(os.path.abspath(__file__))
    fonts_dir = os.path.join(project_dir, "assets", "fonts")
    
    # Create the fonts directory if it doesn't exist
    if not os.path.exists(fonts_dir):
        print(f"Creating fonts directory: {fonts_dir}")
        os.makedirs(fonts_dir, exist_ok=True)
    
    # Check if there are any font files
    font_files = [f for f in os.listdir(fonts_dir) 
                 if f.endswith(('.ttf', '.otf'))]
    
    if not font_files:
        print("No font files found. The program will use the system default font.")
    else:
        print(f"Found {len(font_files)} font files:")
        for file in font_files:
            print(f"  - {file}")

if __name__ == "__main__":
    print("Reddit Story Generator - Background Assets Checker")
    print("="*50)
    background_files = check_backgrounds()
    check_fonts()
    
    print("\nSummary:")
    if background_files:
        print("✓ Background files are available.")
    else:
        print("× No background files found. Please add some background images or videos.")
    
    print("\nYou can now run the main.py script.")