#!/usr/bin/env python3
"""
Script to update film fields in production via API
Usage: python update_film_field.py <film_title> <field_name> <value> [api_url]
"""

import sys
import requests
import json

# Default to production API URL - update this to match your actual backend URL
# Common patterns:
# - https://jamesraybould.me/api (if backend is on same domain)
# - https://your-railway-app.railway.app/api (if using Railway)
DEFAULT_API_URL = 'https://jamesraybould.me/api'

def find_film_by_title(title, api_url):
    """Find film ID by title"""
    try:
        # Try with /api prefix if not already there
        if not api_url.endswith('/api'):
            api_url = f'{api_url}/api' if not api_url.endswith('/') else f'{api_url}api'
        
        response = requests.get(f'{api_url}/films', params={'search': title}, timeout=10)
        response.raise_for_status()
        films = response.json()
        
        # Try exact match first
        for film in films:
            if film['title'].lower() == title.lower():
                return film['id']
        
        # Try partial match
        for film in films:
            if title.lower() in film['title'].lower():
                return film['id']
        
        return None
    except Exception as e:
        print(f"Error searching for film: {e}")
        return None

def update_film_field(film_id, field_name, value, api_url):
    """Update a film field via API"""
    try:
        # Ensure /api prefix
        if not api_url.endswith('/api'):
            api_url = f'{api_url}/api' if not api_url.endswith('/') else f'{api_url}api'
        url = f'{api_url}/admin/films/{film_id}/field'
        payload = {
            'field': field_name,
            'value': value
        }
        
        response = requests.put(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        try:
            error_data = e.response.json()
            return {'error': error_data.get('error', str(e))}
        except:
            return {'error': str(e)}
    except Exception as e:
        return {'error': str(e)}

def update_film_poster(film_id, poster_url, api_url):
    """Update film poster URL via API"""
    try:
        # Ensure /api prefix
        if not api_url.endswith('/api'):
            api_url = f'{api_url}/api' if not api_url.endswith('/') else f'{api_url}api'
        url = f'{api_url}/admin/films/{film_id}/poster'
        payload = {'poster_url': poster_url}
        
        response = requests.put(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        try:
            error_data = e.response.json()
            return {'error': error_data.get('error', str(e))}
        except:
            return {'error': str(e)}
    except Exception as e:
        return {'error': str(e)}

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Usage: python update_film_field.py <film_title> <field_name> <value> [api_url]")
        print("\nExamples:")
        print('  python update_film_field.py "F1 The Movie" poster_url "https://example.com/poster.jpg"')
        print('  python update_film_field.py "F1 The Movie" letter_rating "A"')
        print('  python update_film_field.py "F1 The Movie" rotten_tomatoes "85%" "https://jamesraybould.me/api"')
        sys.exit(1)
    
    film_title = sys.argv[1]
    field_name = sys.argv[2]
    field_value = sys.argv[3]
    api_url = sys.argv[4] if len(sys.argv) > 4 else DEFAULT_API_URL
    
    print(f"Searching for film: {film_title}")
    film_id = find_film_by_title(film_title, api_url)
    
    if not film_id:
        print(f"❌ Film '{film_title}' not found")
        sys.exit(1)
    
    print(f"✓ Found film ID: {film_id}")
    
    # Use poster-specific endpoint if updating poster
    if field_name == 'poster_url':
        result = update_film_poster(film_id, field_value, api_url)
    else:
        result = update_film_field(film_id, field_name, field_value, api_url)
    
    if 'error' in result:
        print(f"❌ Error: {result['error']}")
        sys.exit(1)
    else:
        print(f"✅ Success: {result.get('message', 'Updated successfully')}")
        print(f"   Film ID: {result.get('film_id')}")
        if 'field' in result:
            print(f"   Field: {result['field']} = {result.get('value')}")

