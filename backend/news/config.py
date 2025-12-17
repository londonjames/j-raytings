import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
NEWSAPI_KEY = os.getenv('NEWSAPI_KEY')

# Email Configuration
EMAIL_FROM = os.getenv('EMAIL_FROM')
EMAIL_TO = os.getenv('EMAIL_TO')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

# Database
DB_PATH = os.getenv('NEWS_DB_PATH', 'news_articles.db')

# Scheduling
DIGEST_TIME = os.getenv('DIGEST_TIME', '08:00')

# STRICT REQUIREMENTS
EXACT_ITEMS_COUNT = 30  # Total articles for AI/Tech section
SPORTS_ITEMS_COUNT = 30  # Separate quota for Sports section (increased from 10)
RECENCY_WINDOW_HOURS = 168  # Must be published within last 7 days (168 hours)

# Source Diversity Caps (maximum articles per source in final selection)
SOURCE_MAX_CAPS = {
    'Hacker News: Front Page': 5,  # Max 5 from HN (out of 30 = 16%)
    'Hacker News': 5,  # Combined with above
    'TechCrunch': 8,  # Max 8 from TC (out of 30 = 27%)
    'r/singularity': 3,  # Max 3 from any single subreddit
    'r/artificial': 3,
    'r/ChatGPT': 3,
    'r/ClaudeAI': 3,
    'r/MachineLearning': 3,
}
DEFAULT_SOURCE_MAX = 5  # Default max for any source not listed above

# Content Categories (in priority order)
CATEGORIES = {
    'AI_PRODUCTIVITY': {
        'priority': 1,
        'keywords': ['ai productivity', 'automation tools', 'ai agents', 'workflow automation',
                    'personal ai', 'ai assistant', 'ai workflows', 'zapier', 'n8n',
                    'cursor', 'copilot', 'claude projects', 'chatgpt plugins'],
        'required': True,
    },
    'AI_PRODUCTIVITY_PERSONAL': {
        'priority': 1,  # Same high priority
        'keywords': ['built with ai', 'ai workflow', 'how i use ai', 'ai automation',
                    'productivity hack', 'my ai setup', 'ai tools i use', 'show hn',
                    'i made', 'automated with ai', 'ai project', 'personal automation'],
        'required': True,
        'minimum': 5,  # MUST have 5 personal productivity posts
        'description': 'Personal posts from people sharing AI productivity hacks and workflows'
    },
    'AI_TECH': {
        'priority': 2,
        'keywords': ['artificial intelligence', 'machine learning', 'new ai model',
                    'openai', 'anthropic', 'google ai', 'llm', 'gpt', 'claude',
                    'ai breakthrough', 'ai research', 'neural network'],
        'required': True,
    },
    'BUSINESS_TECH': {
        'priority': 3,
        'keywords': ['startup', 'funding', 'valuation', 'acquisition', 'ipo',
                    'venture capital', 'tech company', 'strategy', 'market shift',
                    'big tech', 'meta', 'apple', 'google', 'amazon', 'microsoft'],
        'required': True,
    },
    'SPORTS': {
        'priority': 4,
        'keywords': [
            # HIGH PRIORITY - Tennis, Olympic Sports, Hyrox
            'tennis', 'atp', 'wta', 'grand slam', 'wimbledon', 'us open', 'french open', 'australian open',
            'olympics', 'olympic', 'hyrox', 'fitness racing', 'crossfit',
            'world cup soccer', 'fifa', 'premier league', 'la liga', 'champions league',
            # MEDIUM PRIORITY - NBA & Soccer
            'nba', 'basketball', 'football', 'soccer', 'messi', 'ronaldo',
            # AVOID - NFL (will be filtered by negative boost)
        ],
        'required': True,
        'minimum': 2,
        'boost_keywords': ['tennis', 'atp', 'wta', 'grand slam', 'olympics', 'olympic', 'hyrox', 'soccer', 'football', 'nba'],
        'penalize_keywords': ['nfl', 'american football', 'super bowl'],
    },
    'WEARABLES': {
        'priority': 5,
        'keywords': ['oura ring', 'whoop', 'wearable', 'fitness tracker', 'health tech'],
        'required': False,
    },
    'LANGUAGE_LEARNING': {
        'priority': 6,
        'keywords': ['language learning', 'duolingo', 'ai language', 'language ai'],
        'required': False,
    }
}

# News Sources Configuration - Organized by category

# AI + Tech RSS Feeds
RSS_FEEDS = [
    'https://hnrss.org/frontpage',  # Hacker News - AI/Tech
    'https://techcrunch.com/feed/',  # TechCrunch - Startups/Tech
    'https://www.theverge.com/rss/index.xml',  # The Verge - Tech
    'https://feeds.arstechnica.com/arstechnica/technology-lab',  # Ars Technica - Tech
    'https://www.artificialintelligence-news.com/feed/',  # AI News
    'https://blog.google/technology/ai/rss/',  # Google AI Blog
    'https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml',  # NY Times - Technology
    'https://rss.nytimes.com/services/xml/rss/nyt/Business.xml',  # NY Times - Business
    'https://www.techmeme.com/feed.xml',  # Techmeme - Tech news aggregator
    'https://www.wired.com/feed/rss',  # Wired - Tech & Culture
    'https://www.axios.com/feeds/feed.rss',  # Axios - Tech & Business
    'https://venturebeat.com/feed/',  # VentureBeat - AI & Tech
    'https://www.theinformation.com/feed',  # The Information - Tech news
    'https://www.technologyreview.com/feed/',  # MIT Technology Review
]

# Sports RSS Feeds
SPORTS_RSS_FEEDS = [
    # TENNIS (highest priority)
    'https://www.espn.com/espn/rss/tennis/news',  # ESPN Tennis
    'https://www.theguardian.com/sport/tennis/rss',  # Guardian Tennis
    'https://www.bbc.com/sport/tennis/rss.xml',  # BBC Tennis

    # SOCCER / FOOTBALL (high priority)
    'https://www.espn.com/espn/rss/soccer/news',  # ESPN Soccer
    'https://www.theguardian.com/football/rss',  # Guardian Football
    'https://www.bbc.com/sport/football/rss.xml',  # BBC Football

    # NBA (medium priority)
    'https://www.espn.com/espn/rss/nba/news',  # ESPN NBA
    'https://www.theguardian.com/sport/nba/rss',  # Guardian NBA
    'https://www.bbc.com/sport/basketball/rss.xml',  # BBC Basketball

    # GENERAL SPORTS (quality sources for broader coverage)
    'https://www.cbssports.com/rss/headlines/',  # CBS Sports - quality journalism
    'https://sports.yahoo.com/rss/',  # Yahoo Sports - broad coverage

    # Note: The Athletic/NYT Sports no longer offer RSS (subscription/paywall only)
    # Note: The Ringer no longer has RSS (Spotify-owned, podcast-focused now)
    # Note: Tennis.com, Marca, SI.com, CNN Sports, AP News RSS feeds are broken/removed
]

# Reddit sources
REDDIT_SUBREDDITS = [
    'artificial',  # AI news
    'MachineLearning',  # ML/AI
    'singularity',  # AI/AGI discussions
    'ChatGPT',  # AI productivity - lots of "how I use" posts
    'ChatGPTPro',  # Advanced AI productivity
    'ClaudeAI',  # Claude-specific productivity
    'LocalLLaMA',  # AI tech + self-hosted productivity
    'OpenAI',  # OpenAI productivity posts
    'AutomateYourself',  # Personal automation
    'productivity',  # Productivity hacks (some AI-related)
    'Oobabooga',  # Personal AI setups
    'StableDiffusion',  # AI art/creativity workflows
    'tennis',  # Tennis
    'nba',  # NBA
    'soccer',  # Soccer/Football
    'hyrox',  # Hyrox fitness racing
]

# NewsAPI search terms by category
NEWSAPI_QUERIES = {
    'AI_PRODUCTIVITY': ['AI automation', 'AI productivity tools', 'AI workflow'],
    'AI_TECH': ['artificial intelligence', 'new AI model', 'OpenAI', 'Anthropic'],
    'BUSINESS_TECH': ['tech startup funding', 'tech acquisition', 'tech valuation'],
    'SPORTS': ['tennis ATP', 'tennis WTA', 'NBA', 'NFL'],
    'WEARABLES': ['Oura ring', 'fitness wearable'],
    'LANGUAGE_LEARNING': ['AI language learning'],
}
