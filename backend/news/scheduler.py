#!/usr/bin/env python3
"""Scheduler to run news fetching and email digest automatically."""

import schedule
import time
from datetime import datetime

from config import DIGEST_TIME
import fetch_news
import send_digest

def fetch_and_send():
    """Fetch news and send digest."""
    print(f"\n{'='*50}")
    print(f"Running scheduled task at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}\n")

    # Fetch news
    fetch_news.main()

    # Wait a moment for articles to be saved
    time.sleep(2)

    # Send digest
    send_digest.main()

    print(f"\n{'='*50}")
    print("Scheduled task completed")
    print(f"{'='*50}\n")

def main():
    print("🔔 Starting news automation scheduler...")
    print(f"   Daily digest will be sent at {DIGEST_TIME}")
    print("   Press Ctrl+C to stop\n")

    # Schedule daily task
    schedule.every().day.at(DIGEST_TIME).do(fetch_and_send)

    # Keep running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nScheduler stopped by user")
