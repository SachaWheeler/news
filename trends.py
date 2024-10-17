#!/usr/bin/env python
from collections import Counter
from datetime import datetime, timedelta
import sqlite3
import string
from utils import my_stopwords

# Load stopwords from NLTK (you'll need to install NLTK and download stopwords)
import nltk
from nltk.corpus import stopwords
# nltk.download('stopwords')
stop_words = set(stopwords.words('english') + my_stopwords)

# Clean text by removing stopwords and punctuation
def clean_text(text):
    text = text.translate(str.maketrans('', '', string.punctuation)).lower()
    return [word for word in text.split()
            if word not in stop_words and
            word.isalpha() and len(word) > 3]

# Connect to the SQLite database
conn = sqlite3.connect('headlines.db')

# Function to fetch headlines from the previous day
def fetch_yesterday_headlines():
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    cursor = conn.cursor()
    cursor.execute("SELECT title FROM headlines WHERE date(timestamp) = ?",
            (yesterday,))
    return [row[0] for row in cursor.fetchall()]

# Function to analyze keyword trends
def analyze_keyword_trends():
    # Get yesterday's headlines and clean them
    headlines = fetch_yesterday_headlines()
    cleaned_headlines = [clean_text(headline) for headline in headlines]

    # Flatten the list of keywords and get frequency counts
    all_keywords = [keyword for sublist in cleaned_headlines for keyword in sublist]
    keyword_counts = Counter(all_keywords)

    bigrams = [bigram for sublist in cleaned_headlines
            for bigram in nltk.bigrams(sublist)]
    trigrams = [trigram for sublist in cleaned_headlines
            for trigram in nltk.trigrams(sublist)]

    # Count bigrams and trigrams
    bigram_counts = Counter(bigrams)
    trigram_counts = Counter(trigrams)

    # Get the top keywords, bigrams, and trigrams
    top_keywords = keyword_counts.most_common(10)
    top_bigrams = bigram_counts.most_common(5)
    top_trigrams = trigram_counts.most_common(5)

    print("Top Keywords:", top_keywords)
    print("Top Bigrams:", [' '.join(bigram) for bigram, _ in top_bigrams])
    print("Top Trigrams:", [' '.join(trigram) for trigram, _ in top_trigrams])

# Call the analysis function
analyze_keyword_trends()

