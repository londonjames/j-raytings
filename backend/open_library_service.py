import requests
import time

OPEN_LIBRARY_BASE_URL = 'https://openlibrary.org'

def search_book_by_isbn(isbn):
    """Search for a book by ISBN on Open Library"""
    if not isbn:
        return None
    
    try:
        # Open Library API endpoint for ISBN lookup
        response = requests.get(
            f'{OPEN_LIBRARY_BASE_URL}/isbn/{isbn}.json',
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return data
        elif response.status_code == 404:
            return None
        else:
            print(f"Open Library API returned status {response.status_code} for ISBN {isbn}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error searching Open Library for ISBN {isbn}: {e}")
        return None

def search_book_by_title_author(title, author=None):
    """Search for a book by title and author on Open Library"""
    try:
        # Build search query
        query = title
        if author:
            query += f" {author}"
        
        params = {
            'q': query,
            'limit': 1
        }
        
        response = requests.get(
            f'{OPEN_LIBRARY_BASE_URL}/search.json',
            params=params,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('docs') and len(data['docs']) > 0:
                return data['docs'][0]
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error searching Open Library for '{title}': {e}")
        return None

def get_book_rating(book_data):
    """Extract rating from Open Library book data"""
    if not book_data:
        return None
    
    # Open Library stores ratings in ratings_summary
    ratings_summary = book_data.get('ratings_summary', {})
    if ratings_summary:
        average = ratings_summary.get('average')
        count = ratings_summary.get('count', 0)
        if average is not None and count > 0:
            return {
                'average_rating': average,
                'ratings_count': count
            }
    
    # Sometimes ratings are in a different format
    if 'average' in book_data:
        return {
            'average_rating': book_data.get('average'),
            'ratings_count': book_data.get('ratings_count', 0)
        }
    
    return None

def get_book_rating_by_isbn(isbn):
    """Get book rating from Open Library by ISBN"""
    book_data = search_book_by_isbn(isbn)
    if book_data:
        # Get the work key to fetch more details
        works = book_data.get('works', [])
        if works and len(works) > 0:
            work_key = works[0].get('key', '').replace('/works/', '')
            if work_key:
                try:
                    work_response = requests.get(
                        f'{OPEN_LIBRARY_BASE_URL}/works/{work_key}.json',
                        timeout=10
                    )
                    if work_response.status_code == 200:
                        work_data = work_response.json()
                        return get_book_rating(work_data)
                except:
                    pass
        
        # Fallback to edition data
        return get_book_rating(book_data)
    
    return None

def get_book_rating_by_title_author(title, author=None):
    """Get book rating from Open Library by title and author"""
    book_data = search_book_by_title_author(title, author)
    if book_data:
        # Try to get work details
        work_keys = book_data.get('work_key', [])
        if work_keys and len(work_keys) > 0:
            work_key = work_keys[0].replace('/works/', '')
            try:
                work_response = requests.get(
                    f'{OPEN_LIBRARY_BASE_URL}/works/{work_key}.json',
                    timeout=10
                )
                if work_response.status_code == 200:
                    work_data = work_response.json()
                    return get_book_rating(work_data)
            except:
                pass
        
        # Fallback to search result data
        return get_book_rating(book_data)
    
    return None

