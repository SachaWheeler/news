#!/usr/bin/env python
import requests
import sqlite3
from datetime import datetime
# from api_key import API_KEY
from pygooglenews import GoogleNews
import re
from utils import my_sources


def fetch_headlines():
    gn = GoogleNews(lang='en', country='UK')
    # top_news = gn.topic_headlines('WORLD')
    top_news = gn.top_news()  # Fetch top news

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
            print("- skipping", publication, title)

    return articles

def headline_exists(c, title):
    c.execute("SELECT 1 FROM headlines WHERE title = ?", (title,))
    return c.fetchone() is not None

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

