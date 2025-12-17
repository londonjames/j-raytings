import requests
from datetime import datetime
from typing import List, Dict

def fetch_hackernews() -> List[Dict]:
    """Fetch top stories from Hacker News."""
    articles = []

    try:
        # Get top stories
        top_stories_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        response = requests.get(top_stories_url, timeout=10)
        response.raise_for_status()
        story_ids = response.json()[:20]  # Top 20 stories

        # Fetch details for each story
        for story_id in story_ids:
            try:
                story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
                story_response = requests.get(story_url, timeout=5)
                story_response.raise_for_status()
                story = story_response.json()

                if story.get('type') == 'story' and story.get('url'):
                    article = {
                        'title': story.get('title', ''),
                        'url': story.get('url', ''),
                        'source': 'Hacker News',
                        'description': story.get('text', '')[:500] if story.get('text') else '',
                        'published_date': datetime.fromtimestamp(story.get('time', 0)).isoformat(),
                    }
                    articles.append(article)

            except Exception as e:
                print(f"Error fetching HN story {story_id}: {e}")
                continue

    except Exception as e:
        print(f"Error fetching Hacker News: {e}")

    return articles
