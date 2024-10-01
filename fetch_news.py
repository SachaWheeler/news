#!/usr/bin/env python
import os
import sqlite3
import requests
import nltk
import re
import string
from datetime import datetime
from nltk.util import ngrams

# Ensure NLTK data is downloaded
nltk.download('punkt')

# API Key for NewsAPI
API_KEY = '131c1ddfd3104c10a57607a77fa15ecb'
NEWS_API_URL = 'https://newsapi.org/v2/top-headlines?country=us&pageSize=100&apiKey=' + API_KEY

# SQLite DB path
DB_PATH = 'headlines.db'

# Function to fetch latest headlines from NewsAPI
def fetch_latest_headlines():
    response = requests.get(NEWS_API_URL)
    if response.status_code == 200:
        data = response.json()
        articles = data.get('articles', [])
        headlines = [preprocess_headline(article['title']) for article in articles if 'title' in article]
        return headlines
    else:
        raise Exception(f"Error fetching data from NewsAPI: {response.status_code}")

# Function to clean and preprocess the headline text
def preprocess_headline(headline):
    # Remove commas, hyphens, single and double quotes
    new_headline = re.sub(r'[^A-Za-z0-9\s]', '', headline.rpartition('-')[0].strip())

    return new_headline

# Initialize or connect to SQLite database
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS headlines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            headline TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    return conn

# Save new headlines to the database
def save_headlines_to_db(headlines):
    conn = init_db()
    cursor = conn.cursor()

    for headline in headlines:
        # Preprocess the headline before saving
        # cleaned_headline = preprocess_headline(headline)
        cursor.execute('''
            INSERT INTO headlines (headline)
            SELECT ? WHERE NOT EXISTS(SELECT 1 FROM headlines WHERE headline = ?)
        ''', (headline, headline))

    conn.commit()
    conn.close()

# Fetch all stored headlines from the database
def fetch_all_headlines_from_db():
    conn = init_db()
    cursor = conn.cursor()
    cursor.execute('SELECT headline FROM headlines')
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]

# Extract and scan for n-grams of different lengths (unigrams, bigrams, trigrams, etc.)
def extract_ngrams(headlines, n):
    all_ngrams = set()
    for headline in headlines:
        tokens = nltk.word_tokenize(headline.lower())
        n_grams = list(ngrams(tokens, n))
        all_ngrams.update(n_grams)
    return all_ngrams

# Detect new phrases by comparing current n-grams with previously stored n-grams
def detect_new_phrases(new_headlines, n):
    conn = init_db()
    cursor = conn.cursor()

    # Fetch all previous n-grams from the database
    cursor.execute(f'SELECT phrase FROM ngrams WHERE length = {n}')
    previous_ngrams = set([tuple(row[0].split()) for row in cursor.fetchall()])

    # Get n-grams from current headlines
    new_ngrams = extract_ngrams(new_headlines, n)

    # Compare to detect new phrases
    new_phrases = new_ngrams - previous_ngrams

    # Save new n-grams to database
    for ngram in new_phrases:
        ngram_str = ' '.join(ngram)
        cursor.execute('INSERT INTO ngrams (phrase, length) VALUES (?, ?)', (ngram_str, n))

    conn.commit()
    conn.close()

    return new_phrases

# Initialize or update n-gram table for storing phrases
def init_ngram_db():
    conn = init_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ngrams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phrase TEXT NOT NULL,
            length INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Main function to fetch headlines, save to DB, and detect new phrases
def main():
    try:
        # Step 1: Fetch latest headlines
        print("Fetching latest headlines...")
        new_headlines = fetch_latest_headlines()

        # Step 2: Save headlines to database
        print("Saving headlines to database...")
        save_headlines_to_db(new_headlines)

        # Step 3: Fetch all stored headlines
        print("Fetching all headlines from database...")
        all_headlines = fetch_all_headlines_from_db()

        # Step 4: Detect new phrases by scanning different n-gram lengths
        init_ngram_db()
        for n in range(1, 6):  # Unigrams to 5-grams
            print(f"Detecting new {n}-grams...")
            new_phrases = detect_new_phrases(new_headlines, n)
            if new_phrases:
                print(f"New {n}-grams detected: {new_phrases}")
            else:
                print(f"No new {n}-grams detected.")

    except Exception as e:
        print(f"An error occurred: {e}")

# Run the script
if __name__ == "__main__":
    main()

