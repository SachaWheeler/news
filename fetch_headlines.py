#!/usr/bin/env python
import requests
import sqlite3
from datetime import datetime, timedelta
from pygooglenews import GoogleNews
import re
import string
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils import my_stopwords, my_sources, MIN_WORD_LENGTH


stop_words = set(nltk.corpus.stopwords.words('english') + my_stopwords)

def fetch_headlines():
    gn = GoogleNews(lang='en', country='UK')
    # top_news = gn.topic_headlines('NATION')
    # top_news = gn.geo_headlines('London')
    top_news = gn.top_news()  # Fetch top news
    # print(top_news)

    articles = []
    for entry in top_news['entries']:
        title = entry.title
        publication = entry.source.title
        if publication in my_sources:
            articles.append({
                'title': title.replace(publication, '').strip(),
                'publication': publication
            })
        else:
            # pass
            print("- skipping", publication, title)

    return articles

"""
def headline_exists(c, title):
    c.execute("SELECT 1 FROM headlines WHERE title = ?", (title,))
    return c.fetchone() is not None
"""

def clean_headline(headline):
    # Remove punctuation and convert to lowercase
    cleaned = headline.translate(str.maketrans('', '', string.punctuation)).lower()
    # Remove stopwords
    cleaned_words = [word for word in cleaned.split()
            if word not in stop_words and len(word) >= MIN_WORD_LENGTH]
    return ' '.join(cleaned_words)

def fetch_previous_day_headlines(c):

    # yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    # c.execute('''SELECT title FROM headlines WHERE date(timestamp) = ?''', (yesterday,))

    c.execute("SELECT title FROM headlines WHERE \
            timestamp >= datetime('now', '-24 hours')")

    rows = c.fetchall()

    # Return a list of headline strings
    return [row[0] for row in rows]


def headline_exists(c, current_headline):
    # Fetch and clean previous day headlines
    previous_day_headlines = fetch_previous_day_headlines(c)
    cleaned_previous_headlines = [clean_headline(h) for h in previous_day_headlines]

    # Clean the current headline
    cleaned_current_headline = clean_headline(current_headline)

    # Vectorize the previous day's headlines and the current headline
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(cleaned_previous_headlines + [cleaned_current_headline])

    # Extract the vector of the current headline (last row)
    current_vector = tfidf_matrix[-1]

    # Compute cosine similarity between the current headline and each previous headline
    try:
        similarities = cosine_similarity(current_vector, tfidf_matrix[:-1])
    except:  # in case we don't have enough records
        return False

    # Check if all similarities are less than 0.5
    for sim in similarities[0]:
        if sim >= 0.6:
            return True  # Similar headline exists

    return False  # No similar headlines found


def save_headlines_to_db(headlines):
    conn = sqlite3.connect('headlines.db')
    c = conn.cursor()

    # Create a table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS headlines
                 (title TEXT, publication TEXT, timestamp DATETIME)''')

    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Insert new headlines into the table
    for article in headlines:
        title = re.sub( r'[^A-Za-z0-9\s-]', '', article['title'].rpartition('-')[0].rstrip())
        if not headline_exists(c, title):
            publication = article['publication']
            print(f"adding '{title}' from {publication}")
            c.execute('''INSERT OR IGNORE INTO headlines
                (title, publication, timestamp) VALUES (?, ?, ?)''',
                (title, publication, current_time))

    conn.commit()
    conn.close()

# Fetch and save headlines every hour
headlines = fetch_headlines()
# print(headlines)
save_headlines_to_db(headlines)

