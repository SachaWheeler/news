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
        'page': 1,        # Page of results to fetch
    }
    response = requests.get(url, params=params)
    return response.json()['articles']

# Function to save headlines to SQLite database
def save_headlines_to_db(headlines):
    conn = sqlite3.connect('headlines.db')
    c = conn.cursor()

    # Create a table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS headlines
                 (title TEXT, publication TEXT, publishedAt TEXT UNIQUE)''')

    # Insert headlines into the table, ignoring if already present (based on timestamp)
    for article in headlines:
        title = re.sub( r'[^A-Za-z0-9\s-]', '',
                article['title'].rpartition('-')[0].rstrip())
        publication = article['source']['name'].strip()
        print(title)
        print(publication)
        print("")
        c.execute('''INSERT OR IGNORE INTO headlines (title, publication, publishedAt)
                     VALUES (?, ?, ?)''',
                  (title, publication, article['publishedAt']))

    conn.commit()
    conn.close()

# Fetch and save headlines every hour
headlines = fetch_headlines()
save_headlines_to_db(headlines)

