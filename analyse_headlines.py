#!/usr/bin/env python
import nltk
from nltk.corpus import stopwords
from collections import Counter
import sqlite3
from datetime import datetime
from utils import my_stopwords, MIN_WORD_LENGTH

# Download NLTK stopwords if you haven't already
nltk.download('stopwords')

# Function to fetch today's headlines from the DB
def fetch_todays_headlines():
    conn = sqlite3.connect('headlines.db')
    c = conn.cursor()

    # Get today's headlines
    today = datetime.now().strftime('%Y-%m-%d')
    # c.execute("SELECT title FROM headlines ")
    c.execute("SELECT title, publication FROM headlines WHERE \
            timestamp >= datetime('now', '-2 hours')")
    rows = c.fetchall()
    # print(rows)

    conn.close()
    return [row[0] for row in rows]

# Function to find popular words excluding stopwords
def find_popular_words(headlines):
    stop_words = set(stopwords.words('english') + my_stopwords)
    words = ' '.join(headlines).lower().split()

    # Remove punctuation and stopwords
    words = [word.strip('.,!?\"\'')
            for word in words
            if word not in stop_words
            and word.isalpha()
            and len(word) >= MIN_WORD_LENGTH]

    # return Counter(words).most_common(20)
    counter = Counter(words)

    # Filter out items with a count of 1 or less
    return Counter(
            {item: count for item, count in counter.items() if count > 1}
            ).most_common(20)


# Fetch headlines and find the top 10 popular words
headlines = fetch_todays_headlines()
top_words = find_popular_words(headlines)
print("Top 10 words:", top_words)

# Function to find headlines containing top words and rank them
def rank_headlines_by_top_words(headlines, top_words):
    ranked_headlines = []

    for headline in headlines:
        count = sum(1 for word in top_words if word[0] in headline.lower())
        if count > 0:
            ranked_headlines.append((headline, count))

    # Sort headlines by how many top words they contain (descending)
    ranked_headlines.sort(key=lambda x: x[1], reverse=True)
    return ranked_headlines

# Rank headlines by top words
ranked_headlines = rank_headlines_by_top_words(headlines, top_words)
for headline, count in ranked_headlines:
    if count > 1:
        print(f"{count}: {headline}")


