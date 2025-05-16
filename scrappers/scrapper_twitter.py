import tweepy
import csv
import time
from datetime import datetime, timedelta

# Replace with your actual bearer token
bearer_token = "AAAAAAAAAAAAAAAAAAAAAFnB0wEAAAAARGDUtwfIS7BxB7%2FlM%2B8syjyIknI%3DSbRDkj5AfuTylMUePWbxx35asVLj72tQH7JFrFaa4gzFMKj2Vz"
client = tweepy.Client(bearer_token=bearer_token, wait_on_rate_limit=True)

keywords = ["bullying", "racism", "hate", "discrimination", "slur", "abuse", "prejudice"]
query = " OR ".join(keywords) + " -is:retweet lang:en"

def scrape_twitter(duration_minutes=10):
    print("🔍 Starting Twitter scrape...")
    start_time = datetime.now()
    end_time = start_time + timedelta(minutes=duration_minutes)
    print(f"⏰ Running from {start_time} to {end_time}")

    all_tweets = []
    seen_ids = set()

    while datetime.now() < end_time:
        try:
            print(f"📡 [{datetime.now()}] Querying Twitter...")
            tweets = client.search_recent_tweets(
                query=query,
                max_results=100,
                tweet_fields=["created_at", "public_metrics", "text", "author_id"]
            )

            if tweets and tweets.data:
                new_count = 0
                for tweet in tweets.data:
                    if tweet.id not in seen_ids:
                        all_tweets.append(tweet)
                        seen_ids.add(tweet.id)
                        new_count += 1
                        # Optional: Print tweet text
                        print(f"📝 {tweet.text[:80]}...")
                print(f"✅ Found {new_count} new tweets. Total: {len(all_tweets)}")
            else:
                print("⏳ No new tweets found.")

            time.sleep(30)  # Pause between calls

        except tweepy.TooManyRequests:
            print("⏱ Rate limit hit. Sleeping for 1 minute...")
            time.sleep(60)
        except tweepy.TweepyException as e:
            print("❌ Tweepy error:", e)
            break
        except Exception as e:
            print("❌ Unexpected error:", e)
            break

    if not all_tweets:
        print("❌ No relevant tweets found in the given time.")
        return

    # Save to CSV
    with open("twitter_scraped_tweets.csv", mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Text", "Created At", "Author ID", "Retweets", "Likes"])
        for tweet in all_tweets:
            writer.writerow([
                tweet.text,
                tweet.created_at,
                tweet.author_id,
                tweet.public_metrics.get("retweet_count", 0),
                tweet.public_metrics.get("like_count", 0)
            ])

    print(f"✅ Done. Saved {len(all_tweets)} tweets to twitter_scraped_tweets.csv.")

if __name__ == "__main__":
    scrape_twitter(duration_minutes=10)
