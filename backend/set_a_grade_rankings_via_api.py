#!/usr/bin/env python3
"""
Script to set A-grade rankings via the API (works with production).
Usage: 
  python set_a_grade_rankings_via_api.py
  OR
  API_URL=https://your-railway-url.railway.app/api python set_a_grade_rankings_via_api.py
"""

import requests
import os
import sys

# Get API URL from environment or prompt user
API_URL = os.getenv('API_URL')

if not API_URL:
    print("Please provide your Railway backend URL.")
    print("You can find it in your Railway dashboard.")
    print("\nUsage:")
    print("  API_URL=https://your-app.railway.app/api python backend/set_a_grade_rankings_via_api.py")
    print("\nOr set it as an environment variable:")
    print("  export API_URL='https://your-app.railway.app/api'")
    print("  python backend/set_a_grade_rankings_via_api.py")
    sys.exit(1)

# Ensure API_URL ends with /api if it doesn't already
if not API_URL.endswith('/api'):
    if API_URL.endswith('/'):
        API_URL = API_URL + 'api'
    else:
        API_URL = API_URL + '/api'

# The 18 A-grade movies with custom rankings
# Rank 1 = best, rank 18 = lowest ranked
# Using exact titles as they appear in the database
rankings = [
    {'title': 'Jaws', 'rank': 1},
    {'title': 'Goodfellas', 'rank': 2},
    {'title': 'The Social Network', 'rank': 3},
    {'title': 'Parasite', 'rank': 4},
    {'title': 'Stand By Me', 'rank': 5},
    {'title': 'Ferris Bueller\'s Day Off', 'rank': 6},
    {'title': 'Back to the Future', 'rank': 7},
    {'title': '12 Angry Men', 'rank': 8},
    {'title': 'About A Boy', 'rank': 9},
    {'title': 'All About Eve', 'rank': 10},
    {'title': 'The American President', 'rank': 11},
    {'title': 'A Beautiful Mind', 'rank': 12},
    {'title': 'Braveheart', 'rank': 13},
    {'title': 'Forrest Gump', 'rank': 14},
    {'title': 'Mystic River', 'rank': 15},
    {'title': 'The Philadelphia Story', 'rank': 16},
    {'title': 'The Shawshank Redemption', 'rank': 17},
    {'title': 'The Sting', 'rank': 18},
]

def main():
    print(f"Setting A-grade rankings via API: {API_URL}")
    print("=" * 60)
    
    # First, try to get all A-grade films to see their exact titles
    try:
        print("\nFetching A-grade films from database to check exact titles...")
        films_response = requests.get(f'{API_URL}/films')
        if films_response.status_code == 200:
            all_films = films_response.json()
            a_grade_films = [f for f in all_films if f.get('letter_rating') == 'A']
            print(f"Found {len(a_grade_films)} A-grade films in database:")
            for film in sorted(a_grade_films, key=lambda x: x.get('title', '')):
                print(f"  - '{film.get('title')}'")
            print()
    except Exception as e:
        print(f"Could not fetch films list: {e}\n")
    
    # Prepare rankings to send
    rankings_to_send = [{'title': item['title'], 'rank': item['rank']} for item in rankings]
    
    try:
        response = requests.post(
            f'{API_URL}/admin/set-a-grade-rankings',
            json={'rankings': rankings_to_send},
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
                print("\nPlease check the titles above and update them if needed.")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error connecting to API: {e}")
        print(f"\nMake sure the API_URL is correct: {API_URL}")
        print("You can set it via environment variable: export API_URL='https://your-api-url.com/api'")

if __name__ == '__main__':
    main()

