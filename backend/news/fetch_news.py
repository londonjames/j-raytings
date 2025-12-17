#!/usr/bin/env python3
"""Main script to fetch and filter news from all sources."""

import sqlite3
from datetime import datetime
import sys

from config import (
    ANTHROPIC_API_KEY,
    NEWSAPI_KEY,
    DB_PATH,
    RSS_FEEDS,
    SPORTS_RSS_FEEDS,
    REDDIT_SUBREDDITS,
    NEWSAPI_QUERIES,
    CATEGORIES,
    EXACT_ITEMS_COUNT,
    SPORTS_ITEMS_COUNT,
    RECENCY_WINDOW_HOURS
)

from fetchers.rss_fetcher import fetch_rss_feeds
from fetchers.newsapi_fetcher import fetch_newsapi_by_category
from fetchers.hackernews_fetcher import fetch_hackernews
from fetchers.reddit_fetcher import fetch_reddit
from filters.category_ranker import categorize_and_rank_articles
from filters.feedback_analyzer import get_feedback_insights, apply_feedback_boost
from filters.source_filter import filter_sources

def save_articles_to_db(articles):
    """Save articles to the database, avoiding duplicates."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    saved_count = 0
    for article in articles:
        try:
            cursor.execute('''
            INSERT OR IGNORE INTO articles
            (title, url, source, published_date, description, content, category, relevance_score, ai_summary, ai_reasoning)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                article['title'],
                article['url'],
                article['source'],
                article.get('published_date'),
                article.get('description', ''),
                article.get('content', ''),
                article.get('category', 'UNCATEGORIZED'),
                article.get('relevance_score', 0.5),
                article.get('ai_summary', ''),
                article.get('ai_reasoning', '')
            ))

            if cursor.rowcount > 0:
                saved_count += 1

        except Exception as e:
            print(f"Error saving article '{article.get('title', 'unknown')}': {e}")

    conn.commit()
    conn.close()

    return saved_count

def main():
    print("🔄 Fetching news from all sources...")
    print(f"   Recency window: {RECENCY_WINDOW_HOURS} hours")
    print(f"   Target: EXACTLY {EXACT_ITEMS_COUNT} articles\n")

    all_articles = []

    # Fetch from Tech/AI RSS feeds
    print("  → Fetching Tech/AI RSS feeds...")
    tech_rss_articles = fetch_rss_feeds(RSS_FEEDS, RECENCY_WINDOW_HOURS)
    all_articles.extend(tech_rss_articles)
    print(f"    ✓ Found {len(tech_rss_articles)} recent articles from Tech RSS")

    # Fetch from Sports RSS feeds
    print("  → Fetching Sports RSS feeds...")
    sports_rss_articles = fetch_rss_feeds(SPORTS_RSS_FEEDS, RECENCY_WINDOW_HOURS)
    all_articles.extend(sports_rss_articles)
    print(f"    ✓ Found {len(sports_rss_articles)} recent articles from Sports RSS")

    # Fetch from NewsAPI with category-specific queries
    print("  → Fetching NewsAPI by category...")
    newsapi_articles = fetch_newsapi_by_category(NEWSAPI_KEY, NEWSAPI_QUERIES, RECENCY_WINDOW_HOURS)
    all_articles.extend(newsapi_articles)
    print(f"    ✓ Found {len(newsapi_articles)} recent articles from NewsAPI")

    # Fetch from Hacker News
    print("  → Fetching Hacker News...")
    hn_articles = fetch_hackernews()
    all_articles.extend(hn_articles)
    print(f"    ✓ Found {len(hn_articles)} recent articles from Hacker News")

    # Fetch from Reddit
    print("  → Fetching Reddit...")
    reddit_articles = fetch_reddit(REDDIT_SUBREDDITS)
    all_articles.extend(reddit_articles)
    print(f"    ✓ Found {len(reddit_articles)} recent articles from Reddit")

    print(f"\n📊 Total articles fetched: {len(all_articles)}")

    # Filter out unwanted sources
    print(f"\n🚫 Filtering unwanted sources...")
    all_articles = filter_sources(all_articles)
    print(f"   After filtering: {len(all_articles)} articles")

    if len(all_articles) < EXACT_ITEMS_COUNT:
        print(f"⚠️  Warning: Only found {len(all_articles)} articles, need {EXACT_ITEMS_COUNT}")
        print("    Consider widening recency window or adding more sources")

    # Get user feedback insights
    print(f"\n💭 Analyzing user feedback...")
    feedback_insights = get_feedback_insights(DB_PATH)
    if feedback_insights['has_feedback']:
        print(f"   Found feedback data - applying preferences")
        all_articles = apply_feedback_boost(all_articles, feedback_insights)
    else:
        print(f"   No feedback data yet - using default ranking")

    # Split articles into Sports and AI/Tech
    sports_articles = [a for a in all_articles if any(src in a.get('source', '').lower()
                      for src in ['espn', 'marca', 'si.com', 'tennis', 'guardian', 'bbc', 'cnn',
                                  'nyt > sports', 'ringer', 'r/tennis', 'r/nba', 'r/soccer', 'r/hyrox'])]
    tech_articles = [a for a in all_articles if a not in sports_articles]

    print(f"\n🤖 Categorizing AI/Tech articles...")
    print(f"   Will select EXACTLY {EXACT_ITEMS_COUNT} AI/Tech articles")
    tech_selected = categorize_and_rank_articles(
        tech_articles,
        {k: v for k, v in CATEGORIES.items() if k != 'SPORTS'},
        ANTHROPIC_API_KEY,
        EXACT_ITEMS_COUNT,
        feedback_insights,
        exclude_sports=True
    )

    print(f"\n⚽ Categorizing Sports articles...")
    print(f"   Will select EXACTLY {SPORTS_ITEMS_COUNT} Sports articles")
    sports_selected = categorize_and_rank_articles(
        sports_articles,
        {'SPORTS': CATEGORIES['SPORTS']},
        ANTHROPIC_API_KEY,
        SPORTS_ITEMS_COUNT,
        feedback_insights,
        sports_only=True
    )

    # Combine both selections
    selected_articles = tech_selected + sports_selected
    print(f"\n📋 Final selection: {len(tech_selected)} AI/Tech + {len(sports_selected)} Sports = {len(selected_articles)} total articles")

    # Save to database
    print("\n💾 Saving to database...")
    saved_count = save_articles_to_db(selected_articles)
    print(f"    ✓ Saved {saved_count} new articles")

    # Print summary
    if selected_articles:
        print("\n📰 Articles by category:")
        category_counts = {}
        for article in selected_articles:
            cat = article.get('category', 'UNCATEGORIZED')
            category_counts[cat] = category_counts.get(cat, 0) + 1

        for cat, count in sorted(category_counts.items(), key=lambda x: -x[1]):
            print(f"   {cat}: {count}")

    print("\n✅ Done!")

if __name__ == "__main__":
    main()
