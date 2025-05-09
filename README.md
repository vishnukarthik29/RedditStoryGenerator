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
