# transformations/transform_clean.py

import sqlite3
import pandas as pd
import re


def clean_reddit_titles_from_db():
    # Database file path
    db_path = '../db/social_media.db'
    table_name = 'reddit_raw'

    # Connect to SQLite DB
    conn = sqlite3.connect(db_path)

    # Load data
    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)

    print(f"Loaded {len(df)} records from {table_name} in {db_path}")

    # --- TRANSFORMATION AND VALIDATION ---
    expectations = {}

    expectations['expect_column_to_exist'] = 'title' in df.columns

    if expectations['expect_column_to_exist']:
        df = df.dropna(subset=['title'])
        df['title'] = df['title'].astype(str)
        expectations['expect_column_values_to_be_string'] = df['title'].apply(lambda x: isinstance(x, str)).all()
        df['word_count'] = df['title'].apply(lambda x: len(x.split()))
        expectations['expect_column_word_count_to_be_between_1_and_100'] = df['word_count'].between(1, 100).all()
        expectations['expect_column_values_to_have_more_than_5_uniques'] = df['title'].nunique() > 5

        def has_special_chars(text):
            return bool(re.search(r'[^A-Za-z0-9\s]', text))

        df['has_special_chars'] = df['title'].apply(has_special_chars)
        num_special = df['has_special_chars'].sum()
        df['title'] = df['title'].apply(lambda x: re.sub(r'[^A-Za-z0-9\s]', '', x))
        df = df.drop(columns=['word_count', 'has_special_chars'])

        cleaned_table_name = 'reddit_cleaned'
        df.to_sql(cleaned_table_name, conn, if_exists='replace', index=False)

        print("\nGreat Expectations-style Checks on 'title' Column:\n")
        for check, result in expectations.items():
            print(f"{check.replace('_', ' ')}: {result}")

        print(f"\ntitles with special characters cleaned: {num_special}")
        print(f"Cleaned data written to table: '{cleaned_table_name}' in {db_path}")
    else:
        print("Column 'title' does not exist in the dataset!")

    conn.close()


if __name__ == "__main__":
    clean_reddit_titles_from_db()
