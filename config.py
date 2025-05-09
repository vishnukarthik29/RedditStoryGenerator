import os
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

# Reddit API credentials
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT', 'RedditVideoGenerator/1.0')

# Log status of Reddit credentials
logger = logging.getLogger(__name__)
if not REDDIT_CLIENT_ID or not REDDIT_CLIENT_SECRET:
    logger.warning("Reddit API credentials not found in environment variables or .env file.")
    logger.warning("Please set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET.")
    
    # For testing/development, you can uncomment and set these directly
    # REDDIT_CLIENT_ID = "your_client_id_here"
    # REDDIT_CLIENT_SECRET = "your_client_secret_here"

# Video settings
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
VIDEO_FPS = 30
VIDEO_DURATION = 60  # Max duration in seconds

# Path settings
ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')
BACKGROUND_DIR = os.path.join(ASSETS_DIR, 'backgrounds')
FONTS_DIR = os.path.join(ASSETS_DIR, 'fonts')
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')

# Create directories if they don't exist
for directory in [ASSETS_DIR, BACKGROUND_DIR, FONTS_DIR, OUTPUT_DIR]:
    os.makedirs(directory, exist_ok=True)

# Text settings
DEFAULT_FONT = os.path.join(FONTS_DIR, 'arial.ttf')
TEXT_COLOR = 'white'
SHADOW_COLOR = 'black'

# TTS settings
TTS_RATE = 175  # Words per minute