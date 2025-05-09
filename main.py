import os
import sys
import logging
import argparse
import time
from datetime import datetime
from typing import List, Dict, Any
import tempfile

import config
from reddit.reddit_client import RedditClient
from reddit.post_processor import PostProcessor
from tts.tts_engine import TTSEngine
from video.background import BackgroundManager
from video.text_overlay import TextOverlayGenerator
from video.compositor import VideoCompositor

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join(os.path.dirname(__file__), 'app.log'))
    ]
)

logger = logging.getLogger(__name__)

def generate_video(subreddit: str, time_filter: str = 'day', output_dir: str = config.OUTPUT_DIR) -> str:
    """
    Generate a Reddit video using content from the specified subreddit.
    
    Args:
        subreddit: Name of the subreddit to fetch content from
        time_filter: Time filter for posts ('hour', 'day', 'week', 'month', 'year', 'all')
        output_dir: Directory to save the output video
        
    Returns:
        Path to the generated video file
    """
    start_time = time.time()
    logger.info(f"Starting video generation for r/{subreddit}")
    
    # Initialize components
    reddit_client = RedditClient()
    post_processor = PostProcessor()
    tts_engine = TTSEngine()
    background_manager = BackgroundManager()
    text_overlay_generator = TextOverlayGenerator()
    video_compositor = VideoCompositor(background_manager, text_overlay_generator)
    
    # Fetch Reddit content
    logger.info(f"Fetching posts from r/{subreddit}")
    posts = reddit_client.fetch_top_posts(subreddit, limit=5, time_filter=time_filter)
    
    if not posts:
        logger.error(f"No posts found in r/{subreddit}")
        return ""
    
    # Select the first valid post
    post = posts[0]
    
    # Fetch comments for the post
    logger.info(f"Fetching comments for post: {post['title']}")
    comments = reddit_client.fetch_comments(post['id'], limit=10)
    
    # Process post and comments into segments
    logger.info("Processing content into segments")
    segments = post_processor.format_for_video(post, comments)
    
    if not segments:
        logger.error("No valid segments created")
        return ""
    
    # Generate audio for each segment
    logger.info("Generating audio for segments")
    audio_paths = []
    
    for i, segment in enumerate(segments):
        audio_path = tts_engine.text_to_speech(segment['text'])
        if audio_path:
            audio_paths.append(audio_path)
        else:
            logger.warning(f"Failed to generate audio for segment {i}")
            # Create an empty temporary file as a placeholder
            fd, temp_path = tempfile.mkstemp(suffix='.mp3')
            os.close(fd)
            audio_paths.append(temp_path)
    
    # Create output filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    sanitized_title = ''.join(c if c.isalnum() else '_' for c in post['title'][:30])
    output_filename = f"reddit_{subreddit}_{sanitized_title}_{timestamp}.mp4"
    output_path = os.path.join(output_dir, output_filename)
    
    # Generate the video
    logger.info("Generating video")
    video_path = video_compositor.create_video(segments, audio_paths, output_path)
    
    # Clean up temporary audio files
    for path in audio_paths:
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception as e:
            logger.warning(f"Failed to remove temporary file {path}: {e}")
    
    elapsed_time = time.time() - start_time
    logger.info(f"Video generation completed in {elapsed_time:.2f} seconds")
    logger.info(f"Video saved to: {video_path}")
    
    return video_path

def main():
    """Main entry point for the Reddit video generator."""
    parser = argparse.ArgumentParser(description="Generate videos from Reddit content")
    parser.add_argument("subreddit", help="Subreddit name to fetch content from")
    parser.add_argument("--time", choices=['hour', 'day', 'week', 'month', 'year', 'all'], 
                       default='day', help="Time filter for posts")
    parser.add_argument("--output", default=config.OUTPUT_DIR, 
                       help="Directory to save the output video")
    
    args = parser.parse_args()
    
    try:
        video_path = generate_video(args.subreddit, args.time, args.output)
        if video_path:
            print(f"\nVideo successfully generated: {video_path}")
        else:
            print("\nFailed to generate video. Check logs for details.")
            return 1
    except Exception as e:
        logger.error(f"Unhandled exception: {e}", exc_info=True)
        print(f"\nError: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())