#!/usr/bin/env python
import sqlite3
import datetime
from newsapi import NewsApiClient
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re
from api_key import API_KEY

# Download stopwords (run this once)
nltk.download('stopwords')
nltk.download('punkt')

# Set up NewsAPI client
api = NewsApiClient(api_key=API_KEY)

# Connect to SQLite database
conn = sqlite3.connect('headlines_2.db')
c = conn.cursor()

# Create the headlines table if it doesn't exist
c.execute('''
    CREATE TABLE IF NOT EXISTS headlines (
        title TEXT,
        timestamp DATETIME
    )
''')

# Function to clean and tokenize text
def clean_and_tokenize(text):
    stop_words = set(stopwords.words('english'))
    tokens = word_tokenize(text)
    cleaned_tokens = [word.lower() for word in tokens if word.isalpha() and word.lower() not in stop_words]
    return cleaned_tokens

# Fetch the top world headlines using NewsAPI
def fetch_headlines():
    headlines = api.get_top_headlines(language='en', category='business')
    return [re.sub(r'[^A-Za-z0-9\s-]', '',
        article['title'].rpartition('-')[0].rstrip()) for article in headlines['articles']]

# Store headlines in the database
def store_headlines(headline_list):
    current_time = datetime.datetime.now()
    for title in headline_list:
        c.execute("INSERT INTO headlines (title, timestamp) VALUES (?, ?)", (title, current_time))
    conn.commit()

# Get previously stored headlines from the database
def get_previous_headlines():
    c.execute("SELECT title FROM headlines")
    previous_headlines = c.fetchall()
    return [clean_and_tokenize(title[0]) for title in previous_headlines]

# Detect and count new words in the latest headlines
def detect_new_words(headline_list):
    previous_words = set()
    for old_tokens in get_previous_headlines():
        previous_words.update(old_tokens)

    new_word_counts = {}
    for title in headline_list:
        tokens = clean_and_tokenize(title)
        new_words = set(tokens) - previous_words
        if new_words:
            new_word_counts[title] = len(new_words)  # Count of new words

    return new_word_counts

# Main function to run the entire process
def main():
    # Fetch latest headlines
    headline_list = fetch_headlines()

    # Store headlines in the database
    store_headlines(headline_list)

    # Detect and count new words in the latest headlines
    new_word_counts = detect_new_words(headline_list)

    # Sort and display headlines with the most new words
    sorted_headlines = sorted(new_word_counts.items(), key=lambda x: x[1], reverse=True)
    print("Headlines with the most new individual words:")
    for headline, count in sorted_headlines:
        print(f"Headline: {headline}")
        print(f"New Words Count: {count}\n")

# Run the script
if __name__ == "__main__":
    main()

# Close the database connection
conn.close()

