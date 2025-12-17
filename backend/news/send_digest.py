#!/usr/bin/env python3
"""Send email digest of top articles."""

import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

from config import (
    EMAIL_FROM,
    EMAIL_TO,
    EMAIL_PASSWORD,
    DB_PATH,
    EXACT_ITEMS_COUNT
)

def get_latest_articles():
    """Get the latest EXACT_ITEMS_COUNT articles from the most recent fetch."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get articles from the most recent fetch batch
    # Order by fetched_at DESC to get the latest run, then by category priority
    cursor.execute('''
    SELECT * FROM articles
    ORDER BY fetched_at DESC,
             CASE category
                WHEN 'AI_PRODUCTIVITY' THEN 1
                WHEN 'AI_TECH' THEN 2
                WHEN 'BUSINESS_TECH' THEN 3
                WHEN 'SPORTS' THEN 4
                WHEN 'WEARABLES' THEN 5
                WHEN 'LANGUAGE_LEARNING' THEN 6
                ELSE 7
             END,
             relevance_score DESC
    LIMIT ?
    ''', (EXACT_ITEMS_COUNT,))

    articles = cursor.fetchall()
    conn.close()

    return articles

def create_email_html(articles, exact_count):
    """Create HTML email content with EXACTLY N articles."""
    if not articles:
        return """
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <h1 style="color: #2563eb;">📰 Your Daily News Digest</h1>
            <p>No new articles matched your interests today. Check back tomorrow!</p>
        </body>
        </html>
        """

    # Category colors
    category_colors = {
        'AI_PRODUCTIVITY': '#8b5cf6',  # Purple
        'AI_TECH': '#3b82f6',  # Blue
        'BUSINESS_TECH': '#10b981',  # Green
        'SPORTS': '#f59e0b',  # Orange
        'WEARABLES': '#ec4899',  # Pink
        'LANGUAGE_LEARNING': '#14b8a6',  # Teal
    }

    articles_html = ""
    for idx, article in enumerate(articles[:exact_count], 1):
        category = article.get('category', 'UNCATEGORIZED')
        category_color = category_colors.get(category, '#6b7280')
        category_display = category.replace('_', ' ').title()

        # Format date
        try:
            pub_date = article.get('published_date', '')[:10] if article.get('published_date') else 'Unknown'
        except:
            pub_date = 'Unknown'

        articles_html += f"""
        <div style="margin-bottom: 25px; padding-bottom: 20px; border-bottom: 1px solid #e2e8f0;">
            <div style="margin-bottom: 8px;">
                <span style="background: {category_color}; color: white; padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">
                    {category_display}
                </span>
                <span style="color: #94a3b8; font-size: 12px; margin-left: 10px;">{article['source']}</span>
            </div>
            <h2 style="margin: 8px 0;">
                <a href="{article['url']}" style="color: #1e293b; text-decoration: none; font-size: 18px; line-height: 1.4;">{article['title']}</a>
            </h2>
            <p style="color: #64748b; margin: 8px 0; line-height: 1.6; font-size: 14px;">{article.get('description', '')[:200]}</p>
            <div style="margin-top: 8px;">
                <span style="color: #94a3b8; font-size: 13px;">📅 {pub_date}</span>
                <span style="color: #cbd5e1; margin: 0 8px;">•</span>
                <a href="{article['url']}" style="color: #2563eb; font-size: 13px; text-decoration: none;">Read more →</a>
            </div>
        </div>
        """

    html = f"""
    <html>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f8fafc;">
        <div style="background: white; padding: 30px; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
            <h1 style="color: #1e293b; margin-top: 0; font-size: 28px;">📰 Your Daily News Digest</h1>
            <p style="color: #64748b; margin-bottom: 30px; font-size: 14px;">
                Your top {len(articles[:exact_count])} articles • {datetime.now().strftime('%B %d, %Y')}
            </p>
            {articles_html}
            <div style="margin-top: 30px; padding-top: 20px; border-top: 2px solid #e2e8f0; text-align: center; color: #94a3b8; font-size: 12px;">
                <p>Powered by your personalized AI news automation</p>
            </div>
        </div>
    </body>
    </html>
    """

    return html

def send_email(subject, html_content):
    """Send email via Gmail SMTP."""
    if not all([EMAIL_FROM, EMAIL_TO, EMAIL_PASSWORD]):
        print("Error: Email configuration incomplete in .env file")
        return False

    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = EMAIL_FROM
        msg['To'] = EMAIL_TO

        # Attach HTML content
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)

        # Send via Gmail SMTP
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_FROM, EMAIL_PASSWORD)
            server.send_message(msg)

        print(f"✓ Email sent successfully to {EMAIL_TO}")
        return True

    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def main():
    print(f"📧 Preparing daily digest (EXACTLY {EXACT_ITEMS_COUNT} articles)...")

    # Get latest articles
    articles = get_latest_articles()

    if not articles:
        print("⚠️  No articles found. Run fetch_news.py first.")
        return

    print(f"   Found {len(articles)} articles")

    # Create email
    subject = f"📰 Your Top {EXACT_ITEMS_COUNT} - {datetime.now().strftime('%B %d, %Y')}"
    html_content = create_email_html(articles, EXACT_ITEMS_COUNT)

    # Send email
    send_email(subject, html_content)

if __name__ == "__main__":
    main()
