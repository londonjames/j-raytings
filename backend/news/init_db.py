import sqlite3
import os
from pathlib import Path

def init_database():
    """Initialize the SQLite database with required tables."""

    # Ensure data directory exists
    Path("data").mkdir(exist_ok=True)

    conn = sqlite3.connect('data/articles.db')
    cursor = conn.cursor()

    # Articles table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS articles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        url TEXT UNIQUE NOT NULL,
        source TEXT NOT NULL,
        published_date TEXT,
        description TEXT,
        content TEXT,
        category TEXT,
        relevance_score REAL,
        ai_summary TEXT,
        ai_reasoning TEXT,
        user_feedback INTEGER DEFAULT 0,
        fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        read BOOLEAN DEFAULT 0
    )
    ''')

    # Create index for faster queries
    cursor.execute('''
    CREATE INDEX IF NOT EXISTS idx_published_date
    ON articles(published_date DESC)
    ''')

    cursor.execute('''
    CREATE INDEX IF NOT EXISTS idx_relevance
    ON articles(relevance_score DESC)
    ''')

    conn.commit()
    conn.close()

    print("✓ Database initialized successfully!")

if __name__ == "__main__":
    init_database()
