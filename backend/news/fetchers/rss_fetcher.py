import feedparser
from datetime import datetime, timedelta
from typing import List, Dict, Optional

def fetch_rss_feeds(feed_urls: List[str], recency_hours: int = 72) -> List[Dict]:
    """Fetch articles from RSS feeds within the recency window."""
    articles = []
    # Use timezone-aware cutoff time
    from datetime import timezone
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=recency_hours)

    for feed_url in feed_urls:
        try:
            feed = feedparser.parse(feed_url)
            source_name = feed.feed.get('title', feed_url)

            for entry in feed.entries[:30]:  # Check more entries to find recent ones
                published_date = parse_date(entry.get('published', entry.get('updated', '')))

                # Skip if no valid date or older than cutoff
                if not published_date:
                    continue

                try:
                    # Parse datetime (keeps timezone info)
                    pub_datetime = datetime.fromisoformat(published_date.replace('Z', '+00:00'))

                    # Convert to UTC for comparison if it has timezone info
                    if pub_datetime.tzinfo is not None:
                        pub_datetime = pub_datetime.astimezone(timezone.utc)
                    else:
                        # If naive, assume UTC
                        pub_datetime = pub_datetime.replace(tzinfo=timezone.utc)

                    if pub_datetime < cutoff_time:
                        continue
                except Exception as e:
                    # Skip articles with unparseable dates
                    continue

                # Validate URL exists
                url = entry.get('link', '')
                if not url or not url.startswith('http'):
                    continue

                article = {
                    'title': entry.get('title', '').strip(),
                    'url': url,
                    'source': source_name,
                    'description': entry.get('summary', '').strip(),
                    'published_date': published_date,
                }

                if article['title']:  # Only add if has a title
                    articles.append(article)

        except Exception as e:
            print(f"Error fetching RSS feed {feed_url}: {e}")

    return articles

def parse_date(date_string: str) -> Optional[str]:
    """Parse date string to ISO format. Returns None if parsing fails."""
    if not date_string:
        return None

    # Try common RSS date formats
    from email.utils import parsedate_to_datetime

    try:
        # First try RFC 2822 format (most common in RSS)
        dt = parsedate_to_datetime(date_string)
        return dt.isoformat()
    except:
        pass

    # Try common formats
    for fmt in ['%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%a, %d %b %Y %H:%M:%S']:
        try:
            return datetime.strptime(date_string.strip(), fmt).isoformat()
        except:
            continue

    return None
