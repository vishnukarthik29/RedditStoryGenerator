"""
Updated reddit_client.py to ensure consistent return types
"""
import praw
import logging
import config
from typing import List, Dict, Any, Union

class RedditClient:
    def __init__(self, client_id=None, client_secret=None, user_agent=None):
        """Initialize the Reddit client."""
        self.logger = logging.getLogger(__name__)
        
        # Create a Reddit instance - using read-only mode if no credentials provided
        try:
            self.reddit = praw.Reddit(
                client_id=config.REDDIT_CLIENT_ID,
                client_secret=config.REDDIT_CLIENT_SECRET,
                user_agent=config.REDDIT_USER_AGENT,
                check_for_updates=False,  # Disable update check to avoid warnings
            )
            self.reddit.read_only = True
            self.logger.info("Reddit client initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize Reddit client: {e}")
            raise
    
    def get_top_posts(self, subreddit_name: str, limit: int = 10, time_filter: str = "day") -> List[Dict[str, Any]]:
        """
        Get top posts from a subreddit.
        
        Args:
            subreddit_name: Name of the subreddit (without "r/")
            limit: Maximum number of posts to retrieve
            time_filter: One of "hour", "day", "week", "month", "year", "all"
            
        Returns:
            List of post objects
        """
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            posts = []
            
            for post in subreddit.top(time_filter=time_filter, limit=limit):
                # Convert PRAW post object to dictionary
                post_dict = {
                    "id": post.id,
                    "title": post.title,
                    "selftext": post.selftext,
                    "score": post.score,
                    "url": post.url,
                    "num_comments": post.num_comments,
                    "created_utc": post.created_utc,
                    "author": str(post.author) if post.author else "[deleted]",
                    "permalink": post.permalink,
                    "is_self": post.is_self,
                    "over_18": post.over_18,
                    "raw_post": post  # Keep the raw post object for getting comments later
                }
                posts.append(post_dict)
            
            self.logger.info(f"Fetched {len(posts)} posts from r/{subreddit_name}")
            return posts
            
        except Exception as e:
            self.logger.error(f"Error fetching posts from r/{subreddit_name}: {e}")
            return []
    
    def get_top_comments(self, post: Dict[str, Any], limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top comments from a post.
        
        Args:
            post: Post dictionary with 'raw_post' key containing the PRAW post object
            limit: Maximum number of comments to retrieve
            
        Returns:
            List of comment dictionaries
        """
        try:
            # Get the raw post object
            raw_post = post.get("raw_post")
            if not raw_post:
                self.logger.error("No raw_post found in post dictionary")
                return []
            
            # Extract comments
            raw_post.comment_sort = "top"
            raw_post.comments.replace_more(limit=0)  # Skip "load more comments" links
            
            comments = []
            for comment in raw_post.comments[:limit]:
                if not comment.author:
                    continue  # Skip deleted comments
                
                comment_dict = {
                    "id": comment.id,
                    "body": comment.body,
                    "score": comment.score,
                    "author": str(comment.author) if comment.author else "[deleted]",
                    "created_utc": comment.created_utc,
                }
                comments.append(comment_dict)
            
            self.logger.info(f"Fetched {len(comments)} comments for post {post['id']}")
            return comments
            
        except Exception as e:
            self.logger.error(f"Error fetching comments for post {post.get('id', 'unknown')}: {e}")
            return []
    
    def get_post_and_comments(self, subreddit_name: str, post_id: str = None, num_comments: int = 10) -> Dict[str, Any]:
        """
        Get a post and its comments.
        
        Args:
            subreddit_name: Name of the subreddit (without "r/")
            post_id: ID of the post to fetch (if None, get the top post)
            num_comments: Number of comments to fetch
            
        Returns:
            Dictionary with post and comments
        """
        try:
            # If post_id is provided, get that specific post
            if post_id:
                post = self.reddit.submission(id=post_id)
                post_dict = {
                    "id": post.id,
                    "title": post.title,
                    "selftext": post.selftext,
                    "score": post.score,
                    "url": post.url,
                    "num_comments": post.num_comments,
                    "created_utc": post.created_utc,
                    "author": str(post.author) if post.author else "[deleted]",
                    "permalink": post.permalink,
                    "is_self": post.is_self,
                    "over_18": post.over_18,
                    "raw_post": post
                }
            else:
                # Otherwise, get the top post from the subreddit
                posts = self.get_top_posts(subreddit_name, limit=1)
                if not posts:
                    self.logger.error(f"No posts found in r/{subreddit_name}")
                    return None
                post_dict = posts[0]
            
            # Get comments
            comments = self.get_top_comments(post_dict, limit=num_comments)
            
            return {
                "post": post_dict,
                "comments": comments
            }
            
        except Exception as e:
            self.logger.error(f"Error fetching post and comments: {e}")
            return None