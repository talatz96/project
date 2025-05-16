import praw
import sqlite3
from datetime import datetime

# Connect to existing database (don't recreate the table)
DB_PATH = "../db/social_media.db"
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Initialize Reddit client
reddit = praw.Reddit(
    client_id="IG1IzZGAdmS3FRTPyMndvA",
    client_secret="tR2hKKi9-b430nYk6hl6iB8QwvVecw",
    user_agent="MyRedditScraper/0.1 by u/csgeekkkkk",
)

# Define subreddits and limits
subreddits = ["news", "worldnews", "politics", "all", "pakistan", 'AskReddit', 'worldnews', 'memes', 'funny']
total_limit = 10000  

def scrape_reddit():
    seen_ids = set()
    count = 0

    for subreddit_name in subreddits:
        subreddit = reddit.subreddit(subreddit_name)

        for submission in subreddit.hot(limit=200):
            if submission.id in seen_ids:
                continue
            seen_ids.add(submission.id)

            post_time = datetime.utcfromtimestamp(submission.created_utc).strftime('%Y-%m-%d %H:%M:%S')

            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO reddit_raw 
                    (id, title, url, score, comments, subreddit, timestamp_utc)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    submission.id,
                    submission.title,
                    submission.url,
                    submission.score,
                    submission.num_comments,
                    submission.subreddit.display_name,
                    post_time,

                ))
                conn.commit()
                count += 1
                print(f"{count}: Inserted: {submission.title[:60]}")

                if count >= total_limit:
                    print("✅ Reached scraping limit.")
                    return

            except Exception as e:
                print(f"❌ Error: {e}")
                continue

if __name__ == "__main__":
    scrape_reddit()
    conn.close()
