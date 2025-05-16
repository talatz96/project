import sqlite3

conn = sqlite3.connect('social_media.db')
cursor = conn.cursor()

#RAW TABLE
cursor.execute('''
CREATE TABLE IF NOT EXISTS reddit_raw (
    id TEXT PRIMARY KEY,
    title TEXT,
    text TEXT,
    url TEXT,
    score INTEGER,
    comments INTEGER,
    subreddit TEXT,
    timestamp_utc TEXT
)
''')

#CLEANED TABLE
cursor.execute('''
CREATE TABLE IF NOT EXISTS reddit_cleaned (
    id TEXT PRIMARY KEY,
    title TEXT,
    FOREIGN KEY (id) REFERENCES reddit_raw(id) ON DELETE CASCADE
)
''')

#LABELLED TABLE
cursor.execute('''
CREATE TABLE IF NOT EXISTS reddit_labelled (
    id TEXT PRIMARY KEY,
    title TEXT,
    label INTEGER,  -- 1 = cyberhate, 0 = not cyberhate
    FOREIGN KEY (id) REFERENCES reddit_cleaned(id) ON DELETE CASCADE
)
''')

conn.commit()
conn.close()
