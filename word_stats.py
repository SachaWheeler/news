#!/usr/bin/env python
import sqlite3
from collections import Counter
import string
import nltk
from nltk.corpus import stopwords
from datetime import datetime, timedelta
from utils import my_stopwords

# Ensure stopwords are downloaded
nltk.download('stopwords')
stop_words = set(stopwords.words('english') + my_stopwords)

# Function to fetch all headlines for a given day from the database
def fetch_headlines_for_day(day):
    conn = sqlite3.connect('headlines.db')
    c = conn.cursor()

    # Fetch all headlines for the given day
    c.execute('''SELECT title FROM headlines
                 WHERE date(timestamp) = ?''', (day,))

    rows = c.fetchall()
    conn.close()

    # Return a list of headline strings
    return [row[0] for row in rows]

# Function to clean and tokenize the headlines
def clean_and_tokenize_headlines(headlines):
    # Remove punctuation and stopwords, and convert to lowercase
    words = []
    for headline in headlines:
        # Remove punctuation
        cleaned = headline.translate(str.maketrans('', '', string.punctuation))
        # Split into words and filter out stopwords
        words += [word.lower() for word in cleaned.split()
                if word.lower() not in stop_words and word.isalpha() and len(word) > 2]
    return words

# Function to find the x most common words from the headlines of a day
def find_top_words_for_day(day):
    # Fetch all headlines for the given day
    headlines = fetch_headlines_for_day(day)

    # Clean and tokenize the headlines
    words = clean_and_tokenize_headlines(headlines)

    # Count word occurrences
    word_counts = Counter(words)

    return word_counts.most_common(30)

# Example usage: Find the top words for today's headlines
today = datetime.now()
days=0
all_words = []
while True:
    day = today - timedelta(days=days)
    day_formatted = day.strftime('%Y-%m-%d')

    top_words = find_top_words_for_day(day_formatted)
    if len(top_words) == 0:
        break

    # Print the 20 most common words
    print("Top 20 words for", today)
    for word, count in top_words:
        for _ in range(count):
            all_words.append(word)
        print(f"{word}: {count}")
    days += 1

print("--------------------")
all_counter = Counter(all_words).most_common()
for word, count in all_counter:
    print(f"{word}: {count}")

