import feedparser
from collections import Counter
import argparse

# List of RSS feeds from major European news sources
RSS_FEEDS = {
    'BBC': 'https://feeds.bbci.co.uk/news/rss.xml',
    # 'Reuters': 'https://www.reuters.com/rssFeed',
    # 'Deutsche Welle': 'https://rss.dw.com/rdf/rss-en-top',
    'Euronews': 'https://www.euronews.com/rss',
    # 'Le Monde': 'https://www.lemonde.fr/rss/une.xml',
    # 'El Pais': 'https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada',
    'The Guardian': 'https://www.theguardian.com/uk/rss',
    # 'Politico Europe': 'https://www.politico.eu/rss/'
}

# Common words to exclude from top keywords
BLOCKLIST = {'the', 'and', 'is', 'in', 'to', 'of', 'a', 'for', 'on', 'with', 'by', 'at', 'as', 'it', 'that', 'from', 'an'}

def fetch_headlines(feed_url):
    feed = feedparser.parse(feed_url)
    headlines = []
    for entry in feed.entries:
        title = entry.get('title', 'No title')
        category = entry.get('category', 'No category')
        if category in ["UK news", "Wine", "UK weather"]:
            pass
        tags = [tag['term'] for tag in entry.get('tags', [])] if 'tags' in entry else []
        headlines.append({'title': title, 'category': category, 'tags': tags})
    return headlines

def display_headlines(feed_name, headlines):
    print(f"\n### {feed_name} ###")
    for item in headlines:
        print(f"- Title: {item['title']}")
        print(f"  Category: {item['category']}")
        print(f"  Tags: {', '.join(item['tags']) if item['tags'] else 'No tags'}")

def compile_top_stories(all_headlines):
    counter = Counter()
    for item in all_headlines:
        words = item['title'].split()
        filtered_words = [word.lower() for word in words if len(word) > 4 and word.lower() not in BLOCKLIST]
        counter.update(filtered_words)
    top_keywords = counter.most_common(10)
    print("\n### Top Keywords Across All Stories ###")
    for word, count in top_keywords:
        print(f"{word}: {count}")

def main():
    parser = argparse.ArgumentParser(description='European News RSS CLI Scanner')
    parser.add_argument('--feeds', nargs='+', choices=RSS_FEEDS.keys(), default=RSS_FEEDS.keys(), help='Select specific news sources')
    args = parser.parse_args()

    all_headlines = []
    for feed_name in args.feeds:
        print(f"Fetching headlines from {feed_name}...")
        headlines = fetch_headlines(RSS_FEEDS[feed_name])
        display_headlines(feed_name, headlines)
        all_headlines.extend(headlines)

    compile_top_stories(all_headlines)

if __name__ == '__main__':
    main()

