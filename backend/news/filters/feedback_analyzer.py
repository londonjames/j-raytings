import sqlite3
from typing import Dict, List, Set
from collections import defaultdict, Counter
import re

# Common words to ignore when extracting keywords
STOP_WORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'been', 'be',
    'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should',
    'could', 'may', 'might', 'can', 'this', 'that', 'these', 'those',
    'it', 'its', 'they', 'them', 'their', 'what', 'which', 'who', 'when',
    'where', 'why', 'how', 'all', 'each', 'every', 'both', 'few', 'more',
    'most', 'other', 'some', 'such', 'only', 'own', 'same', 'so', 'than',
    'too', 'very', 'just', 'now', 'you', 'your', 'we', 'our', 'new'
}

def _extract_keywords(titles: List[str]) -> Counter:
    """
    Extract meaningful keywords from article titles.

    Returns a Counter with keyword frequencies.
    """
    keywords = Counter()

    for title in titles:
        # Convert to lowercase and extract words
        words = re.findall(r'\b[a-z]{3,}\b', title.lower())

        # Filter out stop words and count
        for word in words:
            if word not in STOP_WORDS:
                keywords[word] += 1

    return keywords

def get_feedback_insights(db_path: str) -> Dict:
    """
    Analyze user feedback to understand preferences.

    Returns insights about:
    - Categories the user likes/dislikes
    - Sources the user prefers
    - Keywords from liked articles
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get feedback statistics by category
    cursor.execute('''
        SELECT category,
               SUM(CASE WHEN user_feedback = 1 THEN 1 ELSE 0 END) as thumbs_up,
               SUM(CASE WHEN user_feedback = -1 THEN 1 ELSE 0 END) as thumbs_down,
               COUNT(*) as total_feedback
        FROM articles
        WHERE user_feedback != 0
        GROUP BY category
    ''')

    category_feedback = {}
    for row in cursor.fetchall():
        category, ups, downs, total = row
        if category:
            category_feedback[category] = {
                'thumbs_up': ups,
                'thumbs_down': downs,
                'total': total,
                'net_score': ups - downs,
                'ratio': ups / total if total > 0 else 0
            }

    # Get feedback statistics by source
    cursor.execute('''
        SELECT source,
               SUM(CASE WHEN user_feedback = 1 THEN 1 ELSE 0 END) as thumbs_up,
               SUM(CASE WHEN user_feedback = -1 THEN 1 ELSE 0 END) as thumbs_down,
               COUNT(*) as total_feedback
        FROM articles
        WHERE user_feedback != 0
        GROUP BY source
    ''')

    source_feedback = {}
    for row in cursor.fetchall():
        source, ups, downs, total = row
        if source:
            source_feedback[source] = {
                'thumbs_up': ups,
                'thumbs_down': downs,
                'total': total,
                'net_score': ups - downs,
                'ratio': ups / total if total > 0 else 0
            }

    # Get titles of liked and disliked articles for keyword extraction
    cursor.execute('''
        SELECT title, category, user_feedback
        FROM articles
        WHERE user_feedback != 0
        ORDER BY fetched_at DESC
        LIMIT 100
    ''')

    liked_articles = []
    disliked_articles = []
    for row in cursor.fetchall():
        title, category, feedback = row
        if feedback == 1:
            liked_articles.append({'title': title, 'category': category})
        elif feedback == -1:
            disliked_articles.append({'title': title, 'category': category})

    conn.close()

    # Extract keywords from liked and disliked articles
    liked_keywords = _extract_keywords([a['title'] for a in liked_articles])
    disliked_keywords = _extract_keywords([a['title'] for a in disliked_articles])

    return {
        'category_feedback': category_feedback,
        'source_feedback': source_feedback,
        'liked_articles': liked_articles,
        'disliked_articles': disliked_articles,
        'liked_keywords': liked_keywords,
        'disliked_keywords': disliked_keywords,
        'has_feedback': len(category_feedback) > 0 or len(source_feedback) > 0
    }


def apply_feedback_boost(articles: List[Dict], feedback_insights: Dict) -> List[Dict]:
    """
    Boost relevance scores of articles based on user feedback patterns.

    Four signals:
    - Category preference: Boost/penalize based on category feedback
    - Source preference: Boost/penalize based on source feedback (reduced weight)
    - Keyword matching: Boost articles with keywords from liked articles
    - Keyword avoidance: Penalize articles with keywords from disliked articles
    """
    if not feedback_insights['has_feedback']:
        return articles

    category_feedback = feedback_insights['category_feedback']
    source_feedback = feedback_insights['source_feedback']
    liked_keywords = feedback_insights.get('liked_keywords', Counter())
    disliked_keywords = feedback_insights.get('disliked_keywords', Counter())

    # Get top keywords (most frequently appearing in liked/disliked articles)
    top_liked_keywords = set(word for word, count in liked_keywords.most_common(20) if count >= 2)
    top_disliked_keywords = set(word for word, count in disliked_keywords.most_common(20) if count >= 2)

    for article in articles:
        boost = 0.0

        # 1. Boost based on category preference
        category = article.get('category_hint') or article.get('category', '')
        if category in category_feedback:
            cat_data = category_feedback[category]
            if cat_data['net_score'] > 0:
                boost += 0.15 * (cat_data['ratio'])  # Up to 0.15 boost
            elif cat_data['net_score'] < 0:
                boost -= 0.15 * (1 - cat_data['ratio'])  # Up to 0.15 penalty

            if cat_data['ratio'] >= 0.8 and cat_data['total'] >= 3:
                boost += 0.1  # Bonus for highly preferred categories

        # 2. Boost based on source preference (REDUCED from 0.1 to 0.05)
        source = article.get('source', '')
        if source in source_feedback:
            src_data = source_feedback[source]
            if src_data['net_score'] > 0:
                boost += 0.05 * (src_data['ratio'])  # Up to 0.05 boost
            elif src_data['net_score'] < 0:
                boost -= 0.05 * (1 - src_data['ratio'])  # Up to 0.05 penalty

        # 3. NEW: Boost based on keyword matching from liked articles
        title = article.get('title', '').lower()
        title_words = set(re.findall(r'\b[a-z]{3,}\b', title))

        # Count matches with liked keywords
        liked_matches = len(title_words & top_liked_keywords)
        if liked_matches > 0:
            boost += 0.15 * min(liked_matches / 3, 1.0)  # Up to 0.15 boost for keyword matches

        # 4. NEW: Penalize based on keyword matching from disliked articles
        disliked_matches = len(title_words & top_disliked_keywords)
        if disliked_matches > 0:
            boost -= 0.15 * min(disliked_matches / 3, 1.0)  # Up to 0.15 penalty for disliked keywords

        # Store the feedback boost
        article['feedback_boost'] = boost

    return articles
