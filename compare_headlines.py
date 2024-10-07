#!/usr/bin/env python
import sqlite3
import nltk
import string
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords

# Ensure stopwords are downloaded
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

# Function to fetch all headlines from the database
def fetch_all_headlines():
    conn = sqlite3.connect('headlines.db')
    c = conn.cursor()

    # Fetch all headlines
    c.execute('''SELECT title FROM headlines''')

    rows = c.fetchall()
    conn.close()

    # Return a list of headline strings
    return [row[0] for row in rows]

# Function to clean the headlines
def clean_headlines(headlines):
    cleaned_headlines = []
    for headline in headlines:
        # Remove punctuation and convert to lowercase
        cleaned = headline.translate(str.maketrans('', '', string.punctuation)).lower()
        # Split into words and remove stopwords
        cleaned_words = [word for word in cleaned.split() if word not in stop_words]
        cleaned_headlines.append(' '.join(cleaned_words))
    return cleaned_headlines

# Function to find similar headlines
def find_similar_headlines():
    # Fetch and clean all headlines
    headlines = fetch_all_headlines()
    cleaned_headlines = clean_headlines(headlines)

    # Vectorize headlines using TF-IDF
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(cleaned_headlines)

    # Compute cosine similarity between each pair of headlines
    similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)

    # Threshold for similarity (0.5 means moderately similar)
    threshold = 0.5
    similar_pairs = []

    # Iterate through similarity matrix to find similar headlines
    for i in range(len(headlines)):
        for j in range(i + 1, len(headlines)):  # Avoid comparing the same headlines
            similarity_score = similarity_matrix[i, j]
            if similarity_score > threshold:
                similar_pairs.append((headlines[i], headlines[j], similarity_score))

    # Sort similar pairs by similarity score in descending order
    similar_pairs.sort(key=lambda x: x[2], reverse=True)

    return similar_pairs

# Find and print similar headlines, sorted by similarity score
similar_headlines = find_similar_headlines()

for h1, h2, score in similar_headlines:
    print(f"Headline 1: {h1}")
    print(f"Headline 2: {h2}")
    print(f"Similarity score: {score:.2f}")
    print()

