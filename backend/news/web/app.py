#!/usr/bin/env python3
"""Flask web application for browsing personalized news."""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime, timedelta
import sys
import os
import re

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import DB_PATH

app = Flask(__name__)
CORS(app, origins=["https://www.jamesraybould.me", "https://jamesraybould.me"])

# Add custom filter to strip HTML tags
@app.template_filter('striphtml')
def strip_html_tags(text):
    """Remove HTML tags from text."""
    if not text:
        return ''
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

@app.template_filter('format_date')
def format_date(date_string):
    """Format date as 'December 16, 2025'."""
    if not date_string:
        return ''
    try:
        # Parse ISO format date
        dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        return dt.strftime('%B %d, %Y')
    except:
        return date_string[:10]

@app.template_filter('clean_hn_description')
def clean_hn_description(text):
    """Extract just Points and Comments from Hacker News description."""
    if not text:
        return ''

    # Check if this is a Hacker News description with metadata
    if 'Article URL:' in text or 'Points:' in text:
        import re
        parts = []

        # Extract Points
        points_match = re.search(r'Points:\s*(\d+)', text)
        if points_match:
            parts.append(f"{points_match.group(1)} points")

        # Extract Comments count
        comments_match = re.search(r'#\s*Comments:\s*(\d+)', text)
        if comments_match:
            parts.append(f"{comments_match.group(1)} comments")

        return ' • '.join(parts) if parts else ''

    return text

def get_db_connection():
    """Create a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    """Main page showing recent articles."""
    days = int(request.args.get('days', 7))
    source = request.args.get('source', '')
    section = request.args.get('section', 'tech')  # Default to tech section
    sort_by = request.args.get('sort', 'date_desc')  # Default to newest first

    conn = get_db_connection()
    cursor = conn.cursor()

    # Build query - show all articles regardless of score
    query = '''
    SELECT * FROM articles
    WHERE published_date >= ?
    '''
    params = [
        (datetime.now() - timedelta(days=days)).isoformat()
    ]

    # Filter by section
    if section == 'sports':
        query += ' AND category = ?'
        params.append('SPORTS')
    else:  # tech section
        query += ' AND category != ?'
        params.append('SPORTS')

    if source:
        query += ' AND source = ?'
        params.append(source)

    # Add sorting
    if sort_by == 'date_asc':
        query += ' ORDER BY published_date ASC'
    elif sort_by == 'score_desc':
        query += ' ORDER BY relevance_score DESC, published_date DESC'
    else:  # date_desc (default)
        query += ' ORDER BY published_date DESC'

    query += ' LIMIT 100'

    cursor.execute(query, params)
    articles = cursor.fetchall()

    # Get all sources for filter
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

@app.route('/article/<int:article_id>')
def article_detail(article_id):
    """View a single article."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM articles WHERE id = ?', (article_id,))
    article = cursor.fetchone()

    # Mark as read
    cursor.execute('UPDATE articles SET read = 1 WHERE id = ?', (article_id,))
    conn.commit()
    conn.close()

    if article is None:
        return "Article not found", 404

    return render_template('article.html', article=article)

@app.route('/stats')
def stats():
    """Show statistics about collected articles."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Total articles
    cursor.execute('SELECT COUNT(*) as count FROM articles')
    total = cursor.fetchone()['count']

    # Articles by source
    cursor.execute('''
    SELECT source, COUNT(*) as count, AVG(relevance_score) as avg_score
    FROM articles
    GROUP BY source
    ORDER BY count DESC
    ''')
    by_source = cursor.fetchall()

    # Recent activity (last 7 days)
    cursor.execute('''
    SELECT DATE(published_date) as date, COUNT(*) as count
    FROM articles
    WHERE published_date >= ?
    GROUP BY DATE(published_date)
    ORDER BY date DESC
    ''', [(datetime.now() - timedelta(days=7)).isoformat()])
    recent_activity = cursor.fetchall()

    conn.close()

    return render_template('stats.html',
                         total=total,
                         by_source=by_source,
                         recent_activity=recent_activity)

@app.route('/feedback/<int:article_id>/<rating>', methods=['POST'])
def submit_feedback(article_id, rating):
    """Submit thumbs up (1), thumbs down (-1), or clear (0) feedback for an article."""
    try:
        rating = int(rating)
    except ValueError:
        return jsonify({'error': 'Invalid rating'}), 400

    if rating not in [1, -1, 0]:
        return jsonify({'error': 'Invalid rating'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Update feedback
    cursor.execute('UPDATE articles SET user_feedback = ? WHERE id = ?', (rating, article_id))
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'rating': rating})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
