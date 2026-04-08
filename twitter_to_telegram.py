import tweepy
import requests
import os
import sys
from datetime import datetime

# Get credentials from environment variables
TWITTER_API_KEY = os.environ.get('TWITTER_API_KEY')
TWITTER_API_SECRET = os.environ.get('TWITTER_API_SECRET')
TWITTER_ACCESS_TOKEN = os.environ.get('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_TOKEN_SECRET = os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')
TWITTER_USERNAME = os.environ.get('TWITTER_USERNAME')
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHANNEL_ID = os.environ.get('TELEGRAM_CHANNEL_ID')

# File to store last tweet ID
LAST_TWEET_FILE = 'last_tweet_id.txt'

def get_last_sent_tweet_id():
    """Read last sent tweet ID from file"""
    try:
        if os.path.exists(LAST_TWEET_FILE):
            with open(LAST_TWEET_FILE, 'r') as f:
                return f.read().strip()
        else:
            # Create file if it doesn't exist
            with open(LAST_TWEET_FILE, 'w') as f:
                f.write('0')
            return None
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

def save_last_tweet_id(tweet_id):
    """Save last sent tweet ID"""
    try:
        with open(LAST_TWEET_FILE, 'w') as f:
            f.write(str(tweet_id))
        print(f"Saved tweet ID: {tweet_id}")
    except Exception as e:
        print(f"Error saving file: {e}")

def get_latest_tweet():
    """Get latest tweet from your account"""
    try:
        # Check if credentials exist
        if not TWITTER_API_KEY:
            print("ERROR: TWITTER_API_KEY not set")
            return None
            
        auth = tweepy.OAuth1UserHandler(
            TWITTER_API_KEY, 
            TWITTER_API_SECRET,
            TWITTER_ACCESS_TOKEN, 
            TWITTER_ACCESS_TOKEN_SECRET
        )
        api = tweepy.API(auth, wait_on_rate_limit=True)
        
        # Get user timeline
        tweets = api.user_timeline(screen_name=TWITTER_USERNAME, count=1, tweet_mode='extended')
        
        if tweets and len(tweets) > 0:
            tweet = tweets[0]
            return {
                'id': str(tweet.id),
                'text': tweet.full_text,
                'url': f"https://twitter.com/{TWITTER_USERNAME}/status/{tweet.id}",
                'created_at': tweet.created_at
            }
        else:
            print("No tweets found")
            return None
            
    except tweepy.TweepError as e:
        print(f"Twitter API Error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def send_to_telegram(message, tweet_url):
    """Send tweet to Telegram channel"""
    try:
        if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHANNEL_ID:
            print("ERROR: Telegram credentials not set")
            return False
            
        telegram_api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        
        # Format message
        full_message = f"📢 *New Tweet!*\n\n{message}\n\n🔗 [View on Twitter]({tweet_url})"
        
        # Truncate if too long (Telegram limit is 4096)
        if len(full_message) > 4000:
            full_message = full_message[:4000] + "..."
        
        payload = {
            'chat_id': TELEGRAM_CHANNEL_ID,
            'text': full_message,
            'parse_mode': 'Markdown',
            'disable_web_page_preview': False
        }
        
        response = requests.post(telegram_api_url, data=payload, timeout=30)
        result = response.json()
        
        if result.get('ok'):
            return True
        else:
            print(f"Telegram API Error: {result}")
            return False
            
    except Exception as e:
        print(f"Error sending to Telegram: {e}")
        return False

def main():
    print(f"🤖 Bot started at {datetime.now()}")
    print(f"Checking tweets for @{TWITTER_USERNAME}")
    
    # Verify credentials
    if not all([TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, 
                TWITTER_ACCESS_TOKEN_SECRET, TWITTER_USERNAME, 
                TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID]):
        print("❌ ERROR: Missing credentials! Check your GitHub secrets.")
        print("Required: TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN,")
        print("          TWITTER_ACCESS_TOKEN_SECRET, TWITTER_USERNAME,")
        print("          TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID")
        sys.exit(1)
    
    # Get latest tweet
    latest_tweet = get_latest_tweet()
    
    if not latest_tweet:
        print("❌ Could not fetch tweets. Check Twitter credentials.")
        sys.exit(1)
    
    print(f"Latest tweet ID: {latest_tweet['id']}")
    print(f"Tweet content: {latest_tweet['text'][:100]}...")
    
    # Check if already sent
    last_sent_id = get_last_sent_tweet_id()
    print(f"Last sent tweet ID: {last_sent_id}")
    
    if last_sent_id == latest_tweet['id']:
        print("✅ No new tweets found")
        return
    
    # Send new tweet
    print(f"📤 Sending new tweet to Telegram...")
    
    if send_to_telegram(latest_tweet['text'], latest_tweet['url']):
        save_last_tweet_id(latest_tweet['id'])
        print("✅ Tweet sent to Telegram successfully!")
    else:
        print("❌ Failed to send to Telegram")
        sys.exit(1)

if __name__ == "__main__":
    main()
