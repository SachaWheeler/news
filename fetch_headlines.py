#!/usr/bin/env python
import requests
import sqlite3
from datetime import datetime
from api_key import API_KEY
import re

# Function to fetch headlines using NewsAPI
def fetch_headlines():
    api_key = API_KEY
    url = "https://newsapi.org/v2/top-headlines"
    params = {
        'apiKey': api_key,
        'category': 'general',
        'language': 'en',
        'pageSize': 100,  # Maximum number of results
        # 'sources': 'bbc-news',
        'page': 1,        # Page of results to fetch
    }
    response = requests.get(url, params=params)
    return response.json()['articles']

def headline_exists(c, title):
    c.execute("SELECT 1 FROM headlines WHERE title = ?", (title,))
    return c.fetchone() is not None

# Function to save headlines to SQLite database
def save_headlines_to_db(headlines):
    conn = sqlite3.connect('headlines.db')
    c = conn.cursor()

    # Create a table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS headlines
                 (title TEXT, publication TEXT, timestamp DATETIME)''')

    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Insert headlines into the table, ignoring if already present (based on timestamp)
    for article in headlines:
        if "-" in article['title']:
            title = re.sub( r'[^A-Za-z0-9\s-]', '',
                article['title'].rpartition('-')[0].rstrip())
        else:
            title = article['title']
        if not headline_exists(c, title):
            publication = article['source']['name'].strip()
            c.execute('''INSERT OR IGNORE INTO headlines (title, publication, timestamp)
                    VALUES (?, ?, ?)''',
                    (title, publication, current_time))

    conn.commit()
    conn.close()

# Fetch and save headlines every hour
headlines = fetch_headlines()
# print(headlines)
save_headlines_to_db(headlines)

