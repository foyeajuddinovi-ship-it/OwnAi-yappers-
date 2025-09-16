
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from collections import defaultdict
import tweepy
import os

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Twitter API credentials from environment
API_KEY = os.getenv("TWITTER_API_KEY")
API_SECRET = os.getenv("TWITTER_API_SECRET")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")

auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth)

@app.get("/top-posters")
async def get_top_posters(username: str = Query(..., description="Twitter username without @")):
    user_post_counts = defaultdict(int)
    try:
        tweets = api.user_timeline(screen_name=username, count=20, tweet_mode='extended')
        for tweet in tweets:
            replies = tweepy.Cursor(api.search_tweets,
                                    q=f'to:{username}',
                                    since_id=tweet.id,
                                    tweet_mode='extended').items(50)
            for reply in replies:
                if hasattr(reply, 'in_reply_to_status_id') and reply.in_reply_to_status_id == tweet.id:
                    user_post_counts[reply.user.screen_name] += 1

        sorted_users = dict(sorted(user_post_counts.items(), key=lambda x: x[1], reverse=True)[:50])
        return {"top_posters": sorted_users}
    except Exception as e:
        return {"error": str(e)}
