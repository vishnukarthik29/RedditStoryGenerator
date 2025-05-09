"""
Updated main.py to work with dictionary-based Reddit posts
"""
import os
import argparse
import logging
import time
import tempfile
import datetime
from pathlib import Path

# Import modules
from reddit.reddit_client import RedditClient
from tts.tts_engine import TTSEngine
from video.background import BackgroundManager
from video.text_overlay import TextOverlayGenerator
from video.compositor import VideoCompositor

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("**main**")

# Constants
DEFAULT_OUTPUT_DIR = "output"
ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
BACKGROUNDS_DIR = os.path.join(ASSETS_DIR, "backgrounds")
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")
DEFAULT_FONT = os.path.join(FONTS_DIR, "arial.ttf")

def generate_video(subreddit_name, time_filter="day", output_dir=DEFAULT_OUTPUT_DIR):
    """Generate a video from a Reddit post with comments."""
    start_time = time.time()
    
    # Initialize components
    reddit_client = RedditClient()
    tts_engine = TTSEngine()
    background_manager = BackgroundManager(BACKGROUNDS_DIR)
    text_overlay = TextOverlayGenerator(font_path=DEFAULT_FONT)
    compositor = VideoCompositor()
    
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Generate timestamp for output filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"{subreddit_name}_{timestamp}.mp4")
    
    # Fetch posts from subreddit
    logger.info(f"Fetching posts from r/{subreddit_name}")
    posts = reddit_client.get_top_posts(subreddit_name, limit=5, time_filter=time_filter)
    
    if not posts:
        logger.error(f"No posts found in r/{subreddit_name}")
        return None
    
    # Select the first post and get its comments
    post = posts[0]
    logger.info(f"Fetching comments for post: {post['title']}")  # Modified to use dictionary access
    comments = reddit_client.get_top_comments(post, limit=10)
    
    # Process content into segments (post + comments)
    logger.info("Processing content into segments")
    segments = []
    
    # Add post title
    segments.append({
        "text": post['title'],  # Modified to use dictionary access
        "type": "title"
    })
    
    # Add post body
    if post['selftext']:  # Modified to use dictionary access
        segments.append({
            "text": post['selftext'],  # Modified to use dictionary access
            "type": "post"
        })
    
    # Generate audio for segments
    logger.info("Generating audio for segments")
    temp_audio_files = []
    
    for segment in segments:
        audio_file = tts_engine.text_to_speech(segment["text"])
        if audio_file:
            segment["audio"] = audio_file
            temp_audio_files.append(audio_file)
    
    # Generate the video
    logger.info("Generating video")
    try:
        compositor.generate_video(segments, background_manager, text_overlay, output_file)
        logger.info(f"Video saved to: {output_file}")
        return output_file
    except Exception as e:
        logger.error(f"Error creating video: {e}")
        return None
    finally:
        # Clean up temporary audio files
        for file in temp_audio_files:
            try:
                os.remove(file)
            except Exception as e:
                logger.warning(f"Failed to remove temporary file {file}: {e}")
        
        # Log completion time
        elapsed_time = time.time() - start_time
        logger.info(f"Video generation completed in {elapsed_time:.2f} seconds")

def main():
    """Main function."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Generate a video from a Reddit post with comments.")
    parser.add_argument("subreddit", help="Subreddit name (without the r/)")
    parser.add_argument("--time", "-t", choices=["hour", "day", "week", "month", "year", "all"], 
                        default="day", help="Time filter for posts (default: day)")
    parser.add_argument("--output", "-o", default=DEFAULT_OUTPUT_DIR, 
                        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})")
    args = parser.parse_args()
    
    # Start video generation
    logger.info(f"Starting video generation for r/{args.subreddit}")
    
    try:
        video_path = generate_video(args.subreddit, args.time, args.output)
        if not video_path:
            print("Failed to generate video. Check logs for details.")
    except Exception as e:
        logger.error(f"Unhandled exception: {e}")
        import traceback
        logger.error(traceback.format_exc())
        print(f"Error: {e}")

if __name__ == "__main__":
    main()