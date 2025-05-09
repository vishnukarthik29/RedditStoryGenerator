import praw
from typing import List, Dict, Any
import config
import logging

logger = logging.getLogger(__name__)

class RedditClient:
    """Client for fetching content from Reddit using PRAW."""
    
    def __init__(self):
        """Initialize the Reddit API client using credentials from config."""
        if not config.REDDIT_CLIENT_ID or not config.REDDIT_CLIENT_SECRET:
            raise ValueError(
                "Reddit API credentials are missing. Please set REDDIT_CLIENT_ID and "
                "REDDIT_CLIENT_SECRET in your .env file or environment variables.\n\n"
                "To get these credentials:\n"
                "1. Go to https://www.reddit.com/prefs/apps\n"
                "2. Click 'Create App' or 'Create Another App'\n"
                "3. Fill in the form (select 'script' as the app type)\n"
                "4. Get the client ID (below the app name) and client secret\n"
                "5. Create a .env file in the project root with these values"
            )
            
        self.reddit = praw.Reddit(
            client_id=config.REDDIT_CLIENT_ID,
            client_secret=config.REDDIT_CLIENT_SECRET,
            user_agent=config.REDDIT_USER_AGENT
        )
        logger.info("Reddit client initialized")
    
    def fetch_top_posts(self, subreddit_name: str, limit: int = 10, time_filter: str = 'day') -> List[Dict[str, Any]]:
        """
        Fetch top posts from the specified subreddit.
        
        Args:
            subreddit_name: Name of the subreddit to fetch from
            limit: Maximum number of posts to fetch
            time_filter: Time filter ('hour', 'day', 'week', 'month', 'year', 'all')
            
        Returns:
            List of post data dictionaries
        """
        subreddit = self.reddit.subreddit(subreddit_name)
        posts = []
        
        try:
            for post in subreddit.top(time_filter=time_filter, limit=limit):
                # Skip posts that are not text-based
                if post.is_self and not post.over_18:  # Ensure it's a text post and not NSFW
                    post_data = {
                        'id': post.id,
                        'title': post.title,
                        'selftext': post.selftext,
                        'score': post.score,
                        'num_comments': post.num_comments,
                        'created_utc': post.created_utc,
                        'url': post.url,
                        'permalink': post.permalink,
                        'author': post.author.name if post.author else "[deleted]",
                        'subreddit': post.subreddit.display_name
                    }
                    posts.append(post_data)
                    logger.debug(f"Fetched post: {post.title}")
            
            logger.info(f"Fetched {len(posts)} posts from r/{subreddit_name}")
            return posts
        except Exception as e:
            logger.error(f"Error fetching posts from r/{subreddit_name}: {e}")
            return []
    
    def fetch_comments(self, post_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Fetch top comments for a specific post.
        
        Args:
            post_id: Reddit post ID
            limit: Maximum number of comments to fetch
            
        Returns:
            List of comment data dictionaries
        """
        submission = self.reddit.submission(id=post_id)
        comments = []
        
        try:
            submission.comment_sort = 'top'
            submission.comments.replace_more(limit=0)  # Skip "load more comments" links
            
            for comment in submission.comments[:limit]:
                if not hasattr(comment, 'body'):
                    continue
                    
                comment_data = {
                    'id': comment.id,
                    'body': comment.body,
                    'score': comment.score,
                    'created_utc': comment.created_utc,
                    'author': comment.author.name if comment.author else "[deleted]",
                }
                comments.append(comment_data)
                logger.debug(f"Fetched comment: {comment.body[:50]}...")
            
            logger.info(f"Fetched {len(comments)} comments for post {post_id}")
            return comments
        except Exception as e:
            logger.error(f"Error fetching comments for post {post_id}: {e}")
            return []