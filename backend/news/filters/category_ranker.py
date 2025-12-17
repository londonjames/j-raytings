import anthropic
from typing import List, Dict, Tuple
from collections import Counter
import json

def _enforce_source_diversity(articles: List[Dict], exact_count: int) -> List[Dict]:
    """
    Enforce source diversity caps by removing excess articles from over-represented sources.
    """
    from config import SOURCE_MAX_CAPS, DEFAULT_SOURCE_MAX

    # Count articles per source
    source_counts = Counter(article.get('source', 'Unknown') for article in articles)

    # Track which articles to keep
    kept_articles = []
    removed_articles = []
    source_current_counts = Counter()

    # First pass: keep articles under the cap
    for article in articles:
        source = article.get('source', 'Unknown')
        max_for_source = SOURCE_MAX_CAPS.get(source, DEFAULT_SOURCE_MAX)

        # Combine Hacker News variants
        if 'hacker news' in source.lower():
            hn_count = source_current_counts.get('Hacker News: Front Page', 0) + source_current_counts.get('Hacker News', 0)
            if hn_count >= 5:
                removed_articles.append(article)
                continue

        if source_current_counts[source] < max_for_source:
            kept_articles.append(article)
            source_current_counts[source] += 1
        else:
            removed_articles.append(article)

    # If we removed too many, add back highest scored removed articles
    while len(kept_articles) < exact_count and removed_articles:
        # Sort removed by score and add back the best
        removed_articles.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        kept_articles.append(removed_articles.pop(0))

    if len(kept_articles) != len(articles):
        print(f"  Source diversity: removed {len(articles) - len(kept_articles)} excess articles")
        for source, count in source_current_counts.most_common():
            if count > 3:
                print(f"    {source}: {count} articles")

    return kept_articles

def categorize_and_rank_articles(
    articles: List[Dict],
    categories: Dict[str, Dict],
    api_key: str,
    exact_count: int = 10,
    feedback_insights: Dict = None,
    exclude_sports: bool = False,
    sports_only: bool = False
) -> List[Dict]:
    """
    Use Claude AI to categorize, rank, and select exactly N articles.

    Ensures:
    - Exactly 10 items returned
    - Articles ranked by relevance within categories
    - Category diversity (AI Productivity, AI Tech, Business, Sports, etc.)
    - At least 1 sports article
    - No duplicates
    - All URLs validated
    """

    if not api_key:
        print("Warning: Anthropic API key not configured")
        return articles[:exact_count]

    if not articles:
        print("Warning: No articles to filter")
        return []

    # Remove duplicates by URL first
    seen_urls = set()
    unique_articles = []
    for article in articles:
        url = article.get('url', '')
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_articles.append(article)

    if len(unique_articles) < exact_count:
        print(f"Warning: Only {len(unique_articles)} unique articles available, need {exact_count}")
        return unique_articles

    client = anthropic.Anthropic(api_key=api_key)

    try:
        # Build category descriptions for the AI
        category_desc = []
        for cat_name, cat_info in categories.items():
            priority = cat_info['priority']
            required = cat_info.get('required', False)
            minimum = cat_info.get('minimum', 0)
            keywords = ', '.join(cat_info['keywords'][:5])  # Sample keywords

            req_text = "REQUIRED" if required else "optional"
            min_text = f" (minimum {minimum})" if minimum > 0 else ""

            category_desc.append(
                f"{priority}. {cat_name} ({req_text}{min_text}): {keywords}..."
            )

        categories_text = "\n".join(category_desc)

        # Prepare article list for AI (simplified to reduce token usage)
        articles_text = []
        # Limit to 80 articles and shorter descriptions to leave room for response
        for idx, article in enumerate(unique_articles[:80]):
            desc = article.get('description', '')[:100]  # Reduced from 200
            articles_text.append(
                f"[{idx}] {article['title']}\n"
                f"    Source: {article['source']} | Date: {article.get('published_date', 'unknown')[:10]}\n"
                f"    {desc}"
            )

        articles_list = "\n\n".join(articles_text)

        # Add feedback insights to prompt if available
        feedback_context = ""
        if feedback_insights and feedback_insights.get('has_feedback'):
            cat_feedback = feedback_insights.get('category_feedback', {})
            liked_categories = [cat for cat, data in cat_feedback.items() if data['net_score'] > 0]
            disliked_categories = [cat for cat, data in cat_feedback.items() if data['net_score'] < 0]

            if liked_categories or disliked_categories:
                feedback_context = "\n\nUSER PREFERENCES (based on thumbs up/down feedback):\n"
                if liked_categories:
                    feedback_context += f"- User LIKES these categories: {', '.join(liked_categories)}\n"
                if disliked_categories:
                    feedback_context += f"- User DISLIKES these categories: {', '.join(disliked_categories)}\n"
                feedback_context += "Consider these preferences when selecting articles.\n"

        # Build prompt based on whether this is sports-only or tech-only
        if sports_only:
            # Sports-only feed
            prompt = f"""You are selecting EXACTLY {exact_count} SPORTS articles for a personalized news digest.{feedback_context}

CATEGORIES (in priority order):
{categories_text}

STRICT REQUIREMENTS:
1. Return EXACTLY {exact_count} articles - no more, no fewer
2. All articles MUST be about SPORTS
3. Prioritize: Tennis > Olympic Sports > Hyrox > Soccer/Football > NBA
4. AVOID NFL content (user dislikes American football)
5. Focus on actual sports news, matches, tournaments, player news
6. Ensure diversity across different sports
7. Rank by relevance to user's sports interests
8. Exclude low-quality content (SEO spam, content farms, thin articles)
9. All URLs must be valid and clickable

SOURCE DIVERSITY REQUIREMENTS:
- Maximum 3 articles from any single source
- Prefer diverse sports sources (ESPN, Marca, SI, Tennis.com, Guardian, BBC, etc.)

ARTICLES TO EVALUATE:
{articles_list}

Respond ONLY with valid JSON in this EXACT format (no extra text):
{{
  "selected_articles": [
    {{
      "index": 0,
      "category": "SPORTS",
      "relevance_score": 0.95
    }},
    {{
      "index": 1,
      "category": "SPORTS",
      "relevance_score": 0.90
    }}
  ]
}}

CRITICAL:
- Include the "index" field for each article (from the [number] prefix above)
- Return EXACTLY {exact_count} SPORTS articles
- Prioritize tennis and Olympic sports
- Return ONLY valid JSON, no markdown code blocks or explanations"""
        else:
            # AI/Tech feed (exclude sports)
            prompt = f"""You are selecting EXACTLY {exact_count} articles for a personalized AI & Tech news digest.{feedback_context}

CATEGORIES (in priority order):
{categories_text}

STRICT REQUIREMENTS:
1. Return EXACTLY {exact_count} articles - no more, no fewer
2. Must include at least 5 AI_PRODUCTIVITY_PERSONAL articles (people sharing AI hacks/workflows)
3. Must include at least 5 AI_TECH articles (AI news, model releases, breakthroughs)
4. NO SPORTS articles - this is AI & Tech feed only
5. Prioritize AI_PRODUCTIVITY, AI_PRODUCTIVITY_PERSONAL, and AI_TECH articles highest
6. Ensure category diversity across all categories
7. Rank by relevance within each category
8. Exclude low-quality content (SEO spam, content farms, thin articles)
9. All URLs must be valid and clickable

SOURCE DIVERSITY REQUIREMENTS (IMPORTANT):
- Maximum 5 articles from "Hacker News: Front Page" or "Hacker News" (combined)
- Maximum 8 articles from "TechCrunch"
- Maximum 3 articles from any single subreddit (r/singularity, r/artificial, etc.)
- Prefer diverse sources to give user variety

ARTICLES TO EVALUATE:
{articles_list}

Respond ONLY with valid JSON in this EXACT format (no extra text):
{{
  "selected_articles": [
    {{
      "index": 0,
      "category": "AI_PRODUCTIVITY",
      "relevance_score": 0.95
    }},
    {{
      "index": 1,
      "category": "AI_TECH",
      "relevance_score": 0.92
    }}
  ]
}}

CRITICAL:
- Include the "index" field for each article (from the [number] prefix above)
- Return EXACTLY {exact_count} articles
- Must include at least 5 AI_PRODUCTIVITY_PERSONAL and 5 AI_TECH articles
- Return ONLY valid JSON, no markdown code blocks or explanations"""

        message = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=8192,  # Max for Haiku
            messages=[{"role": "user", "content": prompt}]
        )

        # Parse AI response
        response_text = message.content[0].text
        print(f"  Debug: Got response, length: {len(response_text)}")

        # Extract JSON from response - improved parsing
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()

        # Find the JSON object boundaries
        if "{" in response_text and "}" in response_text:
            json_start = response_text.index("{")
            # Find the matching closing brace by counting
            brace_count = 0
            json_end = -1
            for i in range(json_start, len(response_text)):
                if response_text[i] == "{":
                    brace_count += 1
                elif response_text[i] == "}":
                    brace_count -= 1
                    if brace_count == 0:
                        json_end = i + 1
                        break

            if json_end > json_start:
                response_text = response_text[json_start:json_end]

        print(f"  Debug: Extracted JSON, length: {len(response_text)}")
        if not response_text:
            print(f"  Debug: Empty response. Raw: {message.content[0].text[:200]}")

        result = json.loads(response_text)
        print(f"  Debug: JSON keys: {list(result.keys())}")
        if 'selected_articles' in result:
            print(f"  Debug: Number of selected_articles: {len(result['selected_articles'])}")
            if result['selected_articles']:
                print(f"  Debug: First article keys: {list(result['selected_articles'][0].keys())}")

        # Build final ranked list
        selected_articles = []
        selected_items = result.get('selected_articles', [])

        # Sort by category priority, then relevance score
        category_priority_map = {cat: info['priority'] for cat, info in categories.items()}
        selected_items.sort(
            key=lambda x: (
                category_priority_map.get(x.get('category', ''), 999),
                -x.get('relevance_score', 0)
            )
        )

        for item in selected_items[:exact_count]:
            idx = item.get('index')

            # If AI provided an index, use it
            if idx is not None and idx < len(unique_articles):
                article = unique_articles[idx].copy()
            # Otherwise, try to match by title or URL
            elif 'title' in item or 'url' in item:
                title = item.get('title', '').strip()
                url = item.get('url', '').strip()

                # Find matching article
                matched_article = None
                for a in unique_articles:
                    # Try exact URL match first (most reliable)
                    if url and a.get('url') == url:
                        matched_article = a
                        break
                    # Try exact title match
                    elif title and a.get('title', '').strip() == title:
                        matched_article = a
                        break
                    # Try partial title match (first 50 chars)
                    elif title and len(title) >= 30:
                        article_title = a.get('title', '').strip()
                        if title[:50] in article_title or article_title[:50] in title:
                            matched_article = a
                            break

                if matched_article:
                    article = matched_article.copy()
                else:
                    print(f"  Warning: Could not match article: {title[:50]}")
                    continue
            else:
                print(f"  Warning: Invalid article format (no index, title, or url): {item}")
                continue

            # Add category and scoring info
            # For sports_only mode, always use SPORTS category (not subcategories like Tennis, NBA, etc.)
            if sports_only:
                article['category'] = 'SPORTS'
            else:
                article['category'] = item.get('category', 'UNCATEGORIZED')
            article['relevance_score'] = item.get('relevance_score', item.get('score', 0.5))
            article['ai_summary'] = item.get('summary', '')  # Add AI-generated summary
            article['ai_reasoning'] = item.get('reasoning', '')
            selected_articles.append(article)

        # Ensure exactly the right count
        if len(selected_articles) < exact_count:
            print(f"Warning: AI returned {len(selected_articles)} articles, need {exact_count}")
            # Fill with highest scored remaining articles
            used_indices = {item['index'] for item in selected_items}
            for idx, article in enumerate(unique_articles):
                if idx not in used_indices and len(selected_articles) < exact_count:
                    article = article.copy()
                    article['category'] = 'UNCATEGORIZED'
                    article['relevance_score'] = 0.5
                    selected_articles.append(article)

        print(f"✓ Selected exactly {len(selected_articles)} articles")
        print(f"  Category distribution: {result.get('category_distribution', {})}")

        # Enforce source diversity caps
        selected_articles = _enforce_source_diversity(selected_articles, exact_count)

        return selected_articles[:exact_count]

    except Exception as e:
        print(f"Error in AI categorization: {e}")
        # Fallback: return first N unique articles
        print("Falling back to simple selection")
        for article in unique_articles[:exact_count]:
            # For sports_only mode, use SPORTS category even in fallback
            article['category'] = 'SPORTS' if sports_only else 'UNCATEGORIZED'
            article['relevance_score'] = 0.5
        return unique_articles[:exact_count]
