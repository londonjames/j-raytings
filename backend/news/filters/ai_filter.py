import anthropic
from typing import List, Dict
import json

def filter_articles_with_ai(articles: List[Dict], interests: List[str], api_key: str) -> List[Dict]:
    """Use Claude AI to filter and score articles based on user interests."""

    if not api_key:
        print("Warning: Anthropic API key not configured, skipping AI filtering")
        return articles

    client = anthropic.Anthropic(api_key=api_key)

    filtered_articles = []

    # Process articles in batches to reduce API calls
    batch_size = 10
    for i in range(0, len(articles), batch_size):
        batch = articles[i:i+batch_size]

        try:
            # Prepare article summaries for the AI
            articles_text = "\n\n".join([
                f"Article {idx}:\nTitle: {article['title']}\nSource: {article['source']}\nDescription: {article.get('description', 'N/A')}"
                for idx, article in enumerate(batch)
            ])

            interests_text = ", ".join(interests)

            prompt = f"""You are filtering news articles for a user with these interests: {interests_text}

Here are the articles to evaluate:

{articles_text}

For each article, provide:
1. A relevance score from 0.0 to 1.0 (where 1.0 is highly relevant to the user's interests)
2. A brief 1-2 sentence summary

Respond in JSON format:
{{
  "articles": [
    {{"index": 0, "score": 0.8, "summary": "Brief summary here"}},
    {{"index": 1, "score": 0.3, "summary": "Brief summary here"}},
    ...
  ]
}}"""

            message = client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )

            # Parse AI response
            response_text = message.content[0].text

            # Extract JSON from response (handles markdown code blocks)
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()

            result = json.loads(response_text)

            # Add scores and summaries to articles
            for item in result.get('articles', []):
                idx = item['index']
                if idx < len(batch):
                    batch[idx]['relevance_score'] = item['score']
                    batch[idx]['ai_summary'] = item['summary']
                    filtered_articles.append(batch[idx])

        except Exception as e:
            print(f"Error filtering batch with AI: {e}")
            # If AI filtering fails, include articles with default score
            for article in batch:
                article['relevance_score'] = 0.5
                article['ai_summary'] = article.get('description', '')[:200]
                filtered_articles.append(article)

    return filtered_articles
