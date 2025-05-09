# Reddit Video Generator

Automatically generate TikTok/YouTube Shorts style videos from Reddit posts. This tool fetches popular posts from Reddit, converts them to speech, and creates engaging videos with text overlays and background visuals.

## Features

- Fetch top posts from any subreddit
- Text-to-speech conversion of post content and comments
- Dynamic text overlays with styling
- Background video management
- Automatic video composition

## Installation

1. Clone this repository:

   ```
   git clone https://github.com/yourusername/reddit-video-generator.git
   cd reddit-video-generator
   ```

2. Create a virtual environment and activate it:

   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

4. Set up your Reddit API credentials using the setup script:

   ```
   python setup_credentials.py
   ```

   This interactive script will guide you through the process of creating and configuring your Reddit API credentials.

   Alternatively, you can manually create a `.env` file in the project root:

   ```
   REDDIT_CLIENT_ID=your_client_id
   REDDIT_CLIENT_SECRET=your_client_secret
   REDDIT_USER_AGENT=RedditVideoGenerator/1.0
   ```

   To get these credentials:

   - Go to https://www.reddit.com/prefs/apps
   - Click "Create App" or "Create Another App"
   - Fill in the required information (name, description, etc.)
   - Select "script" as the app type
   - Set the redirect URI to http://localhost:8080
   - Click "Create App"
   - Your client ID is under the app name, and your client secret is labeled as "secret"

## Usage

### Basic Usage

Generate a video from the top post in a subreddit:

```
python main.py askreddit
```

### Advanced Options

```
python main.py askreddit --time week --output ./my_videos
```

Parameters:

- First argument: Subreddit name (required)
- `--time`: Time filter for posts ('hour', 'day', 'week', 'month', 'year', 'all')
- `--output`: Directory to save the output video

## Project Structure

- `main.py`: Main script and entry point
- `config.py`: Configuration settings
- `reddit/`: Reddit API client and post processing
- `tts/`: Text-to-speech conversion
- `video/`: Background video and text overlay handling
- `assets/`: Store background videos and fonts

## Adding Custom Backgrounds

To use your own background videos:

1. Place MP4 video files in the `assets/backgrounds/` directory
2. Make sure videos have proper dimensions (ideally 1080x1920 for vertical format)
3. The program will randomly select from available backgrounds

## Customization

You can customize various aspects of the generated videos by modifying `config.py`:

- Video dimensions and FPS
- Font settings
- Text colors
- Output directory
- And more

## Troubleshooting

### No videos generated

- Check if your Reddit API credentials are correct
- Ensure the subreddit exists and has text posts
- Check the log file (app.log) for detailed error messages

### Text-to-speech issues

- Make sure pyttsx3 is properly installed
- On Linux, you might need to install additional packages: `sudo apt-get install espeak`

### Video generation errors

- Make sure you have ffmpeg installed:
  - On Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH
  - On macOS: `brew install ffmpeg`
  - On Linux: `sudo apt-get install ffmpeg`

## License

MIT License

## Acknowledgments

- Inspired by the trend of Reddit content videos on social media platforms
- Thanks to the creators of PRAW, MoviePy, and pyttsx3 libraries

# Reddit Story Generator - Fix Guide

## Overview of the Issues

Your Reddit Story Generator is encountering errors related to:

1. Outdated Pillow version compatibility:
   - `module 'PIL.Image' has no attribute 'ANTIALIAS'`
   - `'ImageDraw' object has no attribute 'textsize'`
2. Outdated PRAW version warning

## Solution Steps

### 1. Update Dependencies

```bash
pip install --upgrade pillow praw
```

Or update all dependencies:

```bash
pip install -r requirements.txt
```

### 2. Apply Code Fixes

#### Option A: Manual Fix

Replace the following files with the fixed versions:

- `video/background.py`
- `video/text_overlay.py`

#### Option B: Automated Fix

Create a file called `fix_compatibility.py` using the code provided in the first artifact, then run:

```bash
python fix_compatibility.py
```

### 3. Check Asset Files

Ensure your assets folders are properly set up:

- `assets/backgrounds/` should contain at least one mp4 file
- `assets/fonts/` should contain your font files

If you're using a custom font, make sure it exists at the specified path.

### 4. Common Issues and Solutions

#### Cannot find font file

If you see a warning about font file not found, either:

1. Place your font file at the expected location
2. Or modify the code to use a system font that exists on your computer

#### Video backgrounds not working

If video backgrounds cause issues:

1. Check that you have FFmpeg installed
2. Try using an image background instead to test

#### AudioFileClip errors

If you encounter errors with TTS audio files:

1. Make sure you're using a compatible version of moviepy
2. Check that pyttsx3 is properly installed

## Running Your Generator

After applying these fixes, run your generator with:

```bash
python main.py AmItheAsshole
```

## Need More Help?

If you continue to experience issues:

1. Check the logs for specific error messages
2. Make sure all dependencies are correctly installed
3. Consider updating all dependencies to their latest versions
