#!/usr/bin/env python3
"""
Script to set A-grade rankings via the API (works with production).
Usage: python set_a_grade_rankings_via_api.py
"""

import requests
import os

# Get API URL from environment or use default
API_URL = os.getenv('API_URL', 'https://film-tracker-production.up.railway.app/api')

# The 18 A-grade movies with custom rankings
# Rank 1 = best, rank 18 = lowest ranked
rankings = [
    {'title': 'Jaws', 'rank': 1},
    {'title': 'Goodfellas', 'rank': 2},
    {'title': 'Social Network, The', 'rank': 3},
    {'title': 'Parasite', 'rank': 4},
    {'title': 'Stand By Me', 'rank': 5},
    {'title': 'Ferris Bueller\'s Day Off', 'rank': 6},
    {'title': 'Back to the Future', 'rank': 7},
    {'title': '12 Angry Men', 'rank': 8},
    {'title': 'About A Boy', 'rank': 9},
    {'title': 'All About Eve', 'rank': 10},
    {'title': 'American President, The', 'rank': 11},
    {'title': 'Beautiful Mind, A', 'rank': 12},
    {'title': 'Braveheart', 'rank': 13},
    {'title': 'Forrest Gump', 'rank': 14},
    {'title': 'Mystic River', 'rank': 15},
    {'title': 'Philadelphia Story, The', 'rank': 16},
    {'title': 'Shawshank Redemption, The', 'rank': 17},
    {'title': 'Sting, The', 'rank': 18},
]

def main():
    print(f"Setting A-grade rankings via API: {API_URL}")
    print("=" * 60)
    
    try:
        response = requests.post(
            f'{API_URL}/admin/set-a-grade-rankings',
            json={'rankings': rankings},
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Successfully updated {result.get('updated', 0)} rankings!")
            
            not_found = result.get('not_found', [])
            if not_found:
                print(f"\n⚠ Could not find {len(not_found)} movies:")
                for title in not_found:
                    print(f"  - {title}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error connecting to API: {e}")
        print(f"\nMake sure the API_URL is correct: {API_URL}")
        print("You can set it via environment variable: export API_URL='https://your-api-url.com/api'")

if __name__ == '__main__':
    main()

