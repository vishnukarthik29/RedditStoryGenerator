import os
import sys

def main():
    """
    Interactive script to set up Reddit API credentials.
    Creates a .env file with the provided credentials.
    """
    print("===== Reddit Video Generator Setup =====")
    print("\nThis script will help you set up your Reddit API credentials.")
    print("You need to create a Reddit API application to get these credentials.")
    print("\nFollow these steps:")
    print("1. Go to https://www.reddit.com/prefs/apps")
    print("2. Click 'Create App' or 'Create Another App'")
    print("3. Fill in the required information:")
    print("   - Name: RedditVideoGenerator")
    print("   - App type: Select 'script'")
    print("   - Description: A script that generates videos from Reddit posts")
    print("   - Redirect URI: http://localhost:8080")
    print("4. Click 'Create App'")
    print("5. Note the client ID (the string under the app name) and client secret")
    
    print("\nNow, enter your Reddit API credentials:")
    client_id = input("Client ID: ").strip()
    client_secret = input("Client Secret: ").strip()
    user_agent = input("User Agent (press Enter for default [RedditVideoGenerator/1.0]): ").strip()
    
    if not client_id or not client_secret:
        print("\nError: Client ID and Client Secret are required.")
        return 1
        
    if not user_agent:
        user_agent = "RedditVideoGenerator/1.0"
    
    # Create the .env file
    env_content = f"""# Reddit API credentials
REDDIT_CLIENT_ID={client_id}
REDDIT_CLIENT_SECRET={client_secret}
REDDIT_USER_AGENT={user_agent}

# Uncomment and modify these lines to override default settings
# VIDEO_WIDTH=1080
# VIDEO_HEIGHT=1920
# VIDEO_FPS=30
# VIDEO_DURATION=60
# TTS_RATE=175
"""
    
    try:
        with open(".env", "w") as f:
            f.write(env_content)
        print("\nCredentials have been saved to .env file.")
        print("You can now run the Reddit Video Generator:")
        print("python main.py subreddit_name")
    except Exception as e:
        print(f"\nError creating .env file: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())