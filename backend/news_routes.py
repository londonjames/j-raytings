"""News aggregator routes for j-raytings backend"""
from flask import Blueprint, render_template, request, jsonify
import sqlite3
from datetime import datetime, timedelta
import os
import re

# Import news config
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'news'))
from news.config import DB_PATH as NEWS_DB_PATH

news_bp = Blueprint('news', __name__,
                   template_folder='news/web/templates',
                   static_folder='news/web/static',
                   static_url_path='/curated/static')

def get_news_db():
    """Get news database connection"""
    conn = sqlite3.connect(NEWS_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Template filters
@news_bp.app_template_filter('striphtml')
def strip_html_tags(text):
    """Remove HTML tags from text."""
    if not text:
        return ''
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

@news_bp.app_template_filter('format_date')
def format_date(date_string):
    """Format date as 'December 16, 2025'."""
    if not date_string:
        return ''
    try:
        dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        return dt.strftime('%B %d, %Y')
    except:
        return date_string[:10]

@news_bp.app_template_filter('clean_hn_description')
def clean_hn_description(text):
    """Extract just Points and Comments from Hacker News description."""
    if not text:
        return ''
    
    if 'Article URL:' in text or 'Points:' in text:
        parts = []
        points_match = re.search(r'Points:\s*(\d+)', text)
        if points_match:
            parts.append(f"{points_match.group(1)} points")
        comments_match = re.search(r'#\s*Comments:\s*(\d+)', text)
        if comments_match:
            parts.append(f"{comments_match.group(1)} comments")
        return ' • '.join(parts) if parts else ''
    return text

@news_bp.route('/')
@news_bp.route('/curated')
def index():
    """Main news page"""
    days = int(request.args.get('days', 7))
    source = request.args.get('source', '')
    section = request.args.get('section', 'tech')
    sort_by = request.args.get('sort', 'date_desc')
    
    conn = get_news_db()
    cursor = conn.cursor()
    
    query = '''
    SELECT * FROM articles
    WHERE published_date >= ?
    '''
    params = [(datetime.now() - timedelta(days=days)).isoformat()]
    
    if section == 'sports':
        query += ' AND category = ?'
        params.append('SPORTS')
    else:
        query += ' AND category != ?'
        params.append('SPORTS')
    
    if source:
        query += ' AND source = ?'
        params.append(source)
    
    if sort_by == 'date_asc':
        query += ' ORDER BY published_date ASC'
    elif sort_by == 'score_desc':
        query += ' ORDER BY relevance_score DESC, published_date DESC'
    else:
        query += ' ORDER BY published_date DESC'
    
    query += ' LIMIT 100'
    
    cursor.execute(query, params)
    articles = cursor.fetchall()
    
    cursor.execute('SELECT DISTINCT source FROM articles ORDER BY source')
    sources = [row['source'] for row in cursor.fetchall()]
    
    conn.close()
    
    return render_template('index.html',
                         articles=articles,
                         days=days,
                         selected_source=source,
                         sources=sources,
                         section=section,
                         sort_by=sort_by)

@news_bp.route('/feedback/<int:article_id>/<rating>', methods=['POST'])
def submit_feedback(article_id, rating):
    """Submit feedback for an article"""
    try:
        rating = int(rating)
    except ValueError:
        return jsonify({'error': 'Invalid rating'}), 400
    
    if rating not in [1, -1, 0]:
        return jsonify({'error': 'Invalid rating'}), 400
    
    conn = get_news_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE articles SET user_feedback = ? WHERE id = ?', (rating, article_id))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'rating': rating})
