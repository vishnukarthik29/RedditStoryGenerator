"""
Check the structure of the Reddit Story Generator project and validate required files and directories.
"""
import os
import sys

def check_structure():
    """Check the structure of the Reddit Story Generator project."""
    project_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define required directories and files
    required_dirs = [
        "assets",
        "assets/backgrounds",
        "assets/fonts",
        "reddit",
        "tts",
        "video",
        "output"
    ]
    
    required_files = [
        "main.py",
        "reddit/reddit_client.py",
        "tts/tts_engine.py",
        "video/background.py",
        "video/text_overlay.py",
        "video/compositor.py"
    ]
    
    # Check required directories
    print("Checking required directories...")
    missing_dirs = []
    for dir_path in required_dirs:
        full_path = os.path.join(project_dir, dir_path)
        if not os.path.isdir(full_path):
            missing_dirs.append(dir_path)
            print(f"  [MISSING] {dir_path}/")
        else:
            print(f"  [OK] {dir_path}/")
    
    # Check required files
    print("\nChecking required files...")
    missing_files = []
    for file_path in required_files:
        full_path = os.path.join(project_dir, file_path)
        if not os.path.isfile(full_path):
            missing_files.append(file_path)
            print(f"  [MISSING] {file_path}")
        else:
            print(f"  [OK] {file_path}")
    
    # Check backgrounds directory for content
    backgrounds_dir = os.path.join(project_dir, "assets/backgrounds")
    if os.path.isdir(backgrounds_dir):
        background_files = [f for f in os.listdir(backgrounds_dir) 
                           if f.endswith(('.mp4', '.mov', '.avi', '.png', '.jpg', '.jpeg'))]
        
        print(f"\nFound {len(background_files)} background files:")
        for bg_file in background_files:
            print(f"  - {bg_file}")
        
        if not background_files:
            print("  [WARNING] No background files found! Please add mp4, mov, avi, png, jpg, or jpeg files.")
    
    # Check fonts directory for content
    fonts_dir = os.path.join(project_dir, "assets/fonts")
    if os.path.isdir(fonts_dir):
        font_files = [f for f in os.listdir(fonts_dir) 
                     if f.endswith(('.ttf', '.otf'))]
        
        print(f"\nFound {len(font_files)} font files:")
        for font_file in font_files:
            print(f"  - {font_file}")
        
        if not font_files:
            print("  [WARNING] No font files found! Please add ttf or otf files.")
    
    # Summary
    print("\nProject Structure Summary:")
    if missing_dirs:
        print(f"  - Missing {len(missing_dirs)} directories")
        print("    Please create these directories:")
        for d in missing_dirs:
            print(f"    - {d}")
    else:
        print("  - All required directories are present")
    
    if missing_files:
        print(f"  - Missing {len(missing_files)} files")
        print("    Please create these files:")
        for f in missing_files:
            print(f"    - {f}")
    else:
        print("  - All required files are present")
    
    # Final recommendation
    if missing_dirs or missing_files:
        print("\nPlease create the missing directories and files before running the program.")
    else:
        print("\nProject structure looks good! You can now run the program.")

if __name__ == "__main__":
    print("Reddit Story Generator - Project Structure Checker")
    print("="*50)
    check_structure()