"""
This script updates the code to work with newer versions of Pillow.
Run this to apply the fixes to your codebase.
"""
import os
import re
import glob

def fix_antialias_issue(file_path):
    """Replace ANTIALIAS with newer LANCZOS constant in the file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Replace ANTIALIAS with LANCZOS
    updated_content = re.sub(r'PIL\.Image\.ANTIALIAS', 'PIL.Image.LANCZOS', content)
    updated_content = re.sub(r'Image\.ANTIALIAS', 'Image.LANCZOS', updated_content)
    
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(updated_content)

def fix_textsize_issue(file_path):
    """Replace textsize with getbbox/getsize in the file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Pattern to find draw.textsize(text, font) calls
    pattern = r'(\w+)\.textsize\(([^,]+),\s*([^)]+)\)'
    
    def replace_textsize(match):
        draw_obj = match.group(1)
        text = match.group(2)
        font = match.group(3)
        return f"{font}.getsize({text})"
    
    updated_content = re.sub(pattern, replace_textsize, content)
    
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(updated_content)

def find_python_files(directory):
    """Find all Python files in the directory and subdirectories."""
    return glob.glob(os.path.join(directory, '**', '*.py'), recursive=True)

def apply_fixes():
    # Get the project directory
    project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    # Find all Python files
    python_files = find_python_files(project_dir)
    
    for file_path in python_files:
        print(f"Processing: {file_path}")
        fix_antialias_issue(file_path)
        fix_textsize_issue(file_path)
        print(f"Updated: {file_path}")

if __name__ == "__main__":
    print("Applying compatibility fixes for newer Pillow versions...")
    apply_fixes()
    print("Fixes applied successfully!")
    print("\nYou might need to update your requirements.txt with these versions:")
    print("pillow>=9.0.0")
    print("praw>=7.8.1")