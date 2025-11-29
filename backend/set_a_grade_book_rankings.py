#!/usr/bin/env python3
"""
Script to set custom rankings for A-grade books.
This allows custom ordering of A-grade books (A+, A/A+, A) when sorting by rating.
"""

import os
import requests
import json

# Use production API URL if DATABASE_URL is set (Railway), otherwise local
API_URL = os.getenv('API_URL', 'http://localhost:5001/api')

# The 9 A-grade books with custom rankings
A_GRADE_BOOK_RANKINGS = [
    {'book_name': 'Animal Farm', 'rank': 1},
    {'book_name': 'The Amateurs', 'rank': 2},
    {'book_name': 'Confessions of an Advertising Man', 'rank': 3},
    {'book_name': 'Ethan Frome', 'rank': 4},
    {'book_name': 'The Things You Can See Only When You Slow Down: How to Be Calm in a Busy World', 'rank': 5, 'alternatives': ['Things You Can Only See When You Slow Down']},
    {'book_name': 'Gold in the Water: The True Story of Ordinary Men and their Extraordinary Dream of Olympic Glory', 'rank': 6, 'alternatives': ['Gold in the Water']},
    {'book_name': 'The Seven Habits of Highly Effective People', 'rank': 7, 'alternatives': ['Seven Habits']},
    {'book_name': 'Conscious Business: How to Build Value Through Values', 'rank': 8, 'alternatives': ['Conscious Business']},
    {'book_name': 'A Civil Action', 'rank': 9},
]

def set_a_grade_book_rankings():
    """Set A-grade book rankings via API"""
    print(f"Setting A-grade book rankings via API: {API_URL}")
    
    # First, try to get all A-grade books to see their exact titles
    try:
        response = requests.get(f'{API_URL}/books')
        if response.ok:
            all_books = response.json()
            a_grade_books = [b for b in all_books if b.get('j_rayting') in ['A+', 'A/A+', 'A']]
            print(f"\nFound {len(a_grade_books)} A-grade books in database:")
            for book in sorted(a_grade_books, key=lambda x: x.get('book_name', '')):
                print(f"  - {book.get('book_name')} ({book.get('j_rayting')})")
    except Exception as e:
        print(f"Could not fetch books: {e}")
    
    # Set the rankings
    try:
        response = requests.post(
            f'{API_URL}/admin/set-a-grade-book-rankings',
            json={'rankings': A_GRADE_BOOK_RANKINGS},
            headers={'Content-Type': 'application/json'}
        )
        
        if response.ok:
            result = response.json()
            print(f"\n✓ Successfully updated {result.get('updated', 0)} book rankings")
            if result.get('not_found'):
                print(f"\n⚠ Books not found:")
                for name in result['not_found']:
                    print(f"  - {name}")
        else:
            print(f"\n✗ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"\n✗ Error setting rankings: {e}")

if __name__ == '__main__':
    set_a_grade_book_rankings()

