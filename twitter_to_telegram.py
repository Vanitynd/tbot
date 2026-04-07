import tweepy
import requests
import time
import json
import os
from datetime import datetime

# Twitter credentials
TWITTER_API_KEY = os.environ.get('TWITTER_API_KEY')
TWITTER_API_SECRET = os.environ.get('TWITTER_API_SECRET')
TWITTER_ACCESS_TOKEN = os.environ.get('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_TOKEN_SECRET = os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')
TWITTER_USERNAME = os.environ.get('TWITTER_USERNAME')  # Your Twitter handle

# Telegram credentials
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHANNEL_ID = os.environ.get('TELEGRAM_CHANNEL_ID')

# File to store last tweet ID
LAST_TWEET_FILE = 'last_tweet_id.txt'

def get_last_sent_tweet_id():
    """Read last sent tweet ID from file"""
    try:
        with open(LAST_TWEET_FILE, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def save_last_tweet_id(tweet_id):
    """Save last sent tweet ID"""
    with open(LAST_TWEET_FILE, 'w') as f:
        f.write(str(tweet_id))

def get_latest_tweet():
    """Get latest tweet from your account"""
    auth = tweepy.OAuth1UserHandler(
        TWITTER_API_KEY, TWITTER_API_SECRET,
        TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET
    )
    api = tweepy.API(auth)
    
    tweets = api.user_timeline(screen_name=TWITTER_USERNAME, count=1, tweet_mode='extended')
    
    if tweets:
        tweet = tweets[0]
        return {
            'id': tweet.id_str,
            'text': tweet.full_text,
            'url': f"https://twitter.com/{TWITTER_USERNAME}/status/{tweet.id_str}",
            'created_at': tweet.created_at
        }
    return None

def send_to_telegram(message, tweet_url):
    """Send tweet to Telegram channel"""
    telegram_api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    # Format message
    full_message = f"📢 *New Tweet!*\n\n{message}\n\n🔗 [View on Twitter]({tweet_url})"
    
    payload = {
        'chat_id': TELEGRAM_CHANNEL_ID,
        'text': full_message,
        'parse_mode': 'Markdown',
        'disable_web_page_preview': False
    }
    
    response = requests.post(telegram_api_url, data=payload)
    return response.json()

def send_media_to_telegram(media_url, caption, tweet_url):
    """Send tweet with media to Telegram"""
    telegram_api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    
    payload = {
        'chat_id': TELEGRAM_CHANNEL_ID,
        'photo': media_url,
        'caption': f"{caption}\n\n🔗 [View on Twitter]({tweet_url})",
        'parse_mode': 'Markdown'
    }
    
    response = requests.post(telegram_api_url, data=payload)
    return response.json()

def main():
    print(f"Checking for new tweets at {datetime.now()}")
    
    # Get latest tweet
    latest_tweet = get_latest_tweet()
    
    if not latest_tweet:
        print("No tweets found")
        return
    
    # Check if already sent
    last_sent_id = get_last_sent_tweet_id()
    
    if last_sent_id == latest_tweet['id']:
        print("No new tweets")
        return
    
    # Send new tweet
    print(f"New tweet found: {latest_tweet['text'][:50]}...")
    
    # Check if tweet has media (simplified - you can expand)
    result = send_to_telegram(latest_tweet['text'], latest_tweet['url'])
    
    if result.get('ok'):
        save_last_tweet_id(latest_tweet['id'])
        print("Tweet sent to Telegram successfully!")
    else:
        print(f"Error sending to Telegram: {result}")

if __name__ == "__main__":
    main()
