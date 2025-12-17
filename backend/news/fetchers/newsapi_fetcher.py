import requests
from datetime import datetime, timedelta
from typing import List, Dict

def fetch_newsapi_by_category(api_key: str, queries_dict: Dict[str, List[str]], recency_hours: int = 72) -> List[Dict]:
    """Fetch articles from NewsAPI based on category queries."""
    if not api_key:
        print("Warning: NewsAPI key not configured, skipping NewsAPI")
        return []

    articles = []
    base_url = "https://newsapi.org/v2/everything"
    cutoff_time = datetime.now() - timedelta(hours=recency_hours)

    # Flatten queries with category tracking
    query_category_map = []
    for category, queries in queries_dict.items():
        for query in queries[:2]:  # Limit queries per category to stay in free tier
            query_category_map.append((query, category))

    # Limit total queries to stay within NewsAPI free tier
    for query, category in query_category_map[:10]:
        try:
            params = {
                'q': query.strip(),
                'apiKey': api_key,
                'language': 'en',
                'sortBy': 'publishedAt',
                'from': cutoff_time.isoformat(),
                'pageSize': 5,
            }

            response = requests.get(base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            for article_data in data.get('articles', []):
                # Validate published date
                published_at = article_data.get('publishedAt', '')
                if not published_at:
                    continue

                try:
                    pub_datetime = datetime.fromisoformat(published_at.replace('Z', '+00:00').replace('+00:00', ''))
                    if pub_datetime < cutoff_time:
                        continue
                except:
                    continue

                # Validate URL
                url = article_data.get('url', '')
                if not url or not url.startswith('http'):
                    continue

                article = {
                    'title': article_data.get('title', '').strip(),
                    'url': url,
                    'source': article_data.get('source', {}).get('name', 'NewsAPI'),
                    'description': article_data.get('description', '').strip(),
                    'published_date': published_at,
                    'category_hint': category,  # Help AI categorization
                }

                if article['title']:
                    articles.append(article)

        except Exception as e:
            print(f"Error fetching NewsAPI for '{query}': {e}")

    return articles
