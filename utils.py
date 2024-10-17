my_stopwords = [
    'live', 'latest', 'like', 'almost', 'wheres',
    'trump', 'boris', 'johnson', 'tory', 'tories',
    'elon', 'musk', 'tesla',
    'attempt', 'first', 'show', 'join', 'involves', 'site',
    'rape', 'protest', 'paedophile',
    'city', 'year', 'search', 'home',
    'us','thousands',
    'new', 'jobs', 'report', 'crisis',
    'israel', 'israeli', 'jew',
    'pakistan',
    'fantasy', 'football', 'cricket', 'rugby', 'league',
    'could', 'might',
    'see', 'man', 'week', 'says', 'video',
    'arsenal', 'chelsea',
    'scotland',
]

my_sources = [
    'The Telegraph',
    'The Guardian',
    'The Independent',
    'Financial Times',
    'BBC',
    # 'BBC.com',
    # 'ITV News',
    'SciTechDaily',
]

MIN_WORD_LENGTH = 4
HOURS_WINDOW = 24

import nltk
stop_words = set(nltk.corpus.stopwords.words('english') + my_stopwords)
