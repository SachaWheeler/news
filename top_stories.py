#!/usr/bin/env python
# import nltk
from utils import stop_words, MIN_WORD_LENGTH, HOURS_WINDOW
import sqlite3
import string
import nltk
from nltk.corpus import stopwords
from collections import Counter
from datetime import datetime, timedelta

# Download stopwords
# nltk.download('stopwords')
# stop_words = set(stopwords.words('english'))

# Function to clean and remove stop words from headlines
def clean_headline(headline):
    # Remove punctuation and convert to lowercase
    cleaned = headline.translate(str.maketrans('', '', string.punctuation)).lower()
    # Remove stopwords
    cleaned_words = [word for word in cleaned.split() if word not in stop_words]
    return cleaned_words

# Function to fetch headlines from a specific date
def fetch_headlines_by_date(target_date):
    conn = sqlite3.connect('headlines.db')
    c = conn.cursor()

    # Fetch all headlines from the given date
    c.execute('''SELECT title FROM headlines WHERE date(timestamp) = ?''', (target_date,))

    rows = c.fetchall()
    conn.close()
    return [row[0] for row in rows]

# Function to find the most popular keywords in a list of headlines
def find_popular_keywords(headlines, top_n=20):
    all_words = []
    for headline in headlines:
        cleaned_words = clean_headline(headline)
        all_words.extend(cleaned_words)

    # Use Counter to find the most common words
    word_counts = Counter(all_words)
    return word_counts.most_common(top_n)

# Function to rank headlines by keyword overlap
def rank_headlines_by_keywords(headlines, popular_keywords):
    keyword_set = set([word for word, _ in popular_keywords])
    ranked_headlines = []

    for headline in headlines:
        cleaned_words = set(clean_headline(headline))
        overlap = len(keyword_set & cleaned_words)
        ranked_headlines.append((headline, overlap))

    # Sort by overlap in descending order
    ranked_headlines.sort(key=lambda x: x[1], reverse=True)
    return ranked_headlines

# Main function to analyze yesterday and today's headlines
def analyze_headlines():
    # Define date format
    date_format = '%Y-%m-%d'

    # Get yesterday's and today's date
    today = datetime.now().strftime(date_format)
    yesterday = (datetime.now() - timedelta(days=1)).strftime(date_format)

    # Fetch headlines from yesterday and today
    yesterday_headlines = fetch_headlines_by_date(yesterday)
    today_headlines = fetch_headlines_by_date(today)

    if not yesterday_headlines or not today_headlines:
        print("No headlines found for either yesterday or today.")
        return

    # Find the most popular keywords in yesterday's headlines
    yesterday_keywords = find_popular_keywords(yesterday_headlines)

    # Rank yesterday's headlines by keyword overlap (top stories of yesterday)
    ranked_yesterday_headlines = rank_headlines_by_keywords(yesterday_headlines, yesterday_keywords)

    print("Top stories from yesterday based on keyword popularity:")
    for headline, overlap in ranked_yesterday_headlines[:5]:
        print(f"Headline: {headline} | Overlap with popular keywords: {overlap}")

    # Find the most popular keywords in today's headlines
    today_keywords = find_popular_keywords(today_headlines)

    # Compare keywords from today with yesterday's keywords
    yesterday_keyword_set = set([word for word, _ in yesterday_keywords])
    new_keywords_today = [word for word, _ in today_keywords if word not in yesterday_keyword_set]

    print("\nNew keywords from today's headlines that weren't in yesterday's:")
    print(new_keywords_today)

    # Rank today's headlines based on new keywords
    new_keyword_pairs = [(word, count) for word, count in today_keywords if word in new_keywords_today]
    ranked_today_headlines = rank_headlines_by_keywords(today_headlines, new_keyword_pairs)

    print("\nTop stories from today based on new keywords:")
    for headline, overlap in ranked_today_headlines[:5]:
        print(f"Headline: {headline} | Overlap with new keywords: {overlap}")

# Run the analysis
if __name__ == "__main__":
    analyze_headlines()

