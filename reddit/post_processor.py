import re
from typing import Dict, List, Any

class PostProcessor:
    """Process and format Reddit content for video generation."""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean up text by removing URLs, special characters, and markdown.
        
        Args:
            text: Text to clean
            
        Returns:
            Cleaned text
        """
        # Remove URLs
        text = re.sub(r'https?://\S+', '', text)
        
        # Remove Reddit-specific formatting
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)  # Remove markdown links
        text = re.sub(r'&amp;', '&', text)  # Convert HTML entities
        text = re.sub(r'&lt;', '<', text)
        text = re.sub(r'&gt;', '>', text)
        
        # Remove markdown formatting
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Bold
        text = re.sub(r'\*(.*?)\*', r'\1', text)      # Italic
        text = re.sub(r'~~(.*?)~~', r'\1', text)      # Strikethrough
        text = re.sub(r'#+ ', '', text)               # Headers
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    @staticmethod
    def format_for_video(post: Dict[str, Any], comments: List[Dict[str, Any]], max_length: int = 2000) -> List[Dict[str, Any]]:
        """
        Format post and comments into segments suitable for a video.
        
        Args:
            post: Post data dictionary
            comments: List of comment data dictionaries
            max_length: Maximum character length for the script
            
        Returns:
            List of dictionaries containing segments for the video
        """
        segments = []
        
        # Add post title
        segments.append({
            'type': 'title',
            'text': PostProcessor.clean_text(post['title']),
            'author': post['author'],
            'subreddit': post['subreddit']
        })
        
        # Add post content if it exists and isn't too long
        if post.get('selftext') and len(post['selftext']) > 0:
            cleaned_content = PostProcessor.clean_text(post['selftext'])
            
            # Split long posts into paragraphs
            paragraphs = re.split(r'\n+', cleaned_content)
            for i, paragraph in enumerate(paragraphs):
                if paragraph.strip():  # Skip empty paragraphs
                    segments.append({
                        'type': 'post_content',
                        'text': paragraph.strip(),
                        'author': post['author'],
                        'part': i + 1,
                        'total_parts': len([p for p in paragraphs if p.strip()])
                    })
        
        # Add comments
        for i, comment in enumerate(comments):
            cleaned_comment = PostProcessor.clean_text(comment['body'])
            
            # Skip very short or empty comments
            if len(cleaned_comment) < 5:
                continue
                
            segments.append({
                'type': 'comment',
                'text': cleaned_comment,
                'author': comment['author'],
                'score': comment['score'],
                'comment_number': i + 1
            })
            
        # Ensure the total script doesn't exceed max_length
        total_length = sum(len(segment['text']) for segment in segments)
        if total_length > max_length:
            # Keep title and truncate the rest
            result = [segments[0]]
            current_length = len(segments[0]['text'])
            
            for segment in segments[1:]:
                segment_length = len(segment['text'])
                if current_length + segment_length <= max_length:
                    result.append(segment)
                    current_length += segment_length
                else:
                    break
                    
            return result
        
        return segments