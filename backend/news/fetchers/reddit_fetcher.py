import requests
from datetime import datetime
from typing import List, Dict

def fetch_reddit(subreddits: List[str]) -> List[Dict]:
    """Fetch hot posts from Reddit subreddits."""
    articles = []

    headers = {
        'User-Agent': 'PersonalizedNews/1.0'
    }

    for subreddit in subreddits:
        try:
            url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=10"
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            for post in data.get('data', {}).get('children', []):
                post_data = post.get('data', {})

                # Skip self posts without external links
                if post_data.get('is_self') and not post_data.get('url_overridden_by_dest'):
                    continue

                article = {
                    'title': post_data.get('title', ''),
                    'url': post_data.get('url', ''),
                    'source': f"r/{subreddit}",
                    'description': post_data.get('selftext', '')[:500],
                    'published_date': datetime.fromtimestamp(post_data.get('created_utc', 0)).isoformat(),
                }
                articles.append(article)

        except Exception as e:
            print(f"Error fetching Reddit r/{subreddit}: {e}")

    return articles
