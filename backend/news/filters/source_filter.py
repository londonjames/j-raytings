"""Filter out unwanted sources based on user preferences."""

from typing import List, Dict

# Sources to exclude from AI & Tech categories
EXCLUDED_SOURCES_AI_TECH = [
    'Times of India',
    'The Times of India',
    'MensHealth.com',
    "Men's Health",
    'Fitnessista',
    'The Fitnessista',
    'r/tennis',  # Tennis subreddit only in Sports
    'r/nba',  # NBA subreddit only in Sports
    'r/nfl',  # NFL subreddit only in Sports
    'ESPN',  # All ESPN content only in Sports
    'Fitness',  # Any fitness-related sources
    'Health',  # Generic health sources (unless AI-health specific)
]

# Sources to exclude globally
EXCLUDED_SOURCES_GLOBAL = [
    # Add any sources you never want to see
]


def filter_sources(articles: List[Dict]) -> List[Dict]:
    """
    Filter out articles from unwanted sources.

    Rules:
    - Times of India, MensHealth.com excluded from AI & Tech categories
    - r/tennis only allowed in SPORTS category
    """
    filtered_articles = []

    for article in articles:
        source = article.get('source', '')
        category = article.get('category_hint', article.get('category', ''))

        # Check global exclusions
        if any(excluded.lower() in source.lower() for excluded in EXCLUDED_SOURCES_GLOBAL):
            continue

        # Check AI & Tech category exclusions
        if category != 'SPORTS':
            if any(excluded.lower() in source.lower() for excluded in EXCLUDED_SOURCES_AI_TECH):
                continue

        filtered_articles.append(article)

    return filtered_articles
