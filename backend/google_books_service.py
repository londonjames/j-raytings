import requests
import os
import time

GOOGLE_BOOKS_API_KEY = os.getenv('GOOGLE_BOOKS_API_KEY', '')
GOOGLE_BOOKS_BASE_URL = 'https://www.googleapis.com/books/v1/volumes'

def search_book(title, author=None, isbn=None):
    """Search for a book on Google Books API"""
    if not GOOGLE_BOOKS_API_KEY:
        print("Warning: GOOGLE_BOOKS_API_KEY not set")
        # API works without key but has lower rate limits
        pass

    # Build search query
    query_parts = []
    if title:
        query_parts.append(f'intitle:{title}')
    if author:
        query_parts.append(f'inauthor:{author}')
    if isbn:
        query_parts.append(f'isbn:{isbn}')
    
    if not query_parts:
        return None
    
    query = '+'.join(query_parts)
    
    params = {
        'q': query,
        'maxResults': 1
    }
    
    if GOOGLE_BOOKS_API_KEY:
        params['key'] = GOOGLE_BOOKS_API_KEY

    try:
        response = requests.get(GOOGLE_BOOKS_BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get('items') and len(data['items']) > 0:
            # Return the first result
            volume = data['items'][0]
            volume_info = volume.get('volumeInfo', {})
            
            # Extract cover image URL
            image_links = volume_info.get('imageLinks', {})
            cover_url = None
            if image_links.get('thumbnail'):
                # Replace thumbnail with larger image (remove zoom parameter and use larger size)
                cover_url = image_links['thumbnail'].replace('zoom=1', 'zoom=0').replace('&edge=curl', '')
            elif image_links.get('small'):
                cover_url = image_links['small']
            elif image_links.get('medium'):
                cover_url = image_links['medium']
            elif image_links.get('large'):
                cover_url = image_links['large']
            
            # Extract ISBNs
            isbn_13 = None
            isbn_10 = None
            industry_identifiers = volume_info.get('industryIdentifiers', [])
            for identifier in industry_identifiers:
                if identifier.get('type') == 'ISBN_13':
                    isbn_13 = identifier.get('identifier')
                elif identifier.get('type') == 'ISBN_10':
                    isbn_10 = identifier.get('identifier')
            
            return {
                'google_books_id': volume.get('id'),
                'title': volume_info.get('title'),
                'authors': volume_info.get('authors', []),
                'cover_url': cover_url,
                'isbn_13': isbn_13,
                'isbn_10': isbn_10,
                'isbn': isbn_13 or isbn_10,  # Prefer ISBN-13
                'average_rating': volume_info.get('averageRating'),
                'ratings_count': volume_info.get('ratingsCount'),
                'published_date': volume_info.get('publishedDate'),
                'description': volume_info.get('description'),
                'page_count': volume_info.get('pageCount'),
                'categories': volume_info.get('categories', [])
            }
    except requests.exceptions.RequestException as e:
        print(f"Error searching Google Books for '{title}': {e}")

    return None

def get_book_details(google_books_id):
    """Get detailed information about a book including rating"""
    params = {}
    if GOOGLE_BOOKS_API_KEY:
        params['key'] = GOOGLE_BOOKS_API_KEY

    try:
        response = requests.get(
            f'{GOOGLE_BOOKS_BASE_URL}/{google_books_id}',
            params=params,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        volume_info = data.get('volumeInfo', {})
        
        # Extract cover image URL
        image_links = volume_info.get('imageLinks', {})
        cover_url = None
        if image_links.get('thumbnail'):
            cover_url = image_links['thumbnail'].replace('zoom=1', 'zoom=0').replace('&edge=curl', '')
        elif image_links.get('small'):
            cover_url = image_links['small']
        elif image_links.get('medium'):
            cover_url = image_links['medium']
        elif image_links.get('large'):
            cover_url = image_links['large']
        
        # Extract ISBNs
        isbn_13 = None
        isbn_10 = None
        industry_identifiers = volume_info.get('industryIdentifiers', [])
        for identifier in industry_identifiers:
            if identifier.get('type') == 'ISBN_13':
                isbn_13 = identifier.get('identifier')
            elif identifier.get('type') == 'ISBN_10':
                isbn_10 = identifier.get('identifier')
        
        return {
            'google_books_id': data.get('id'),
            'title': volume_info.get('title'),
            'authors': volume_info.get('authors', []),
            'cover_url': cover_url,
            'isbn_13': isbn_13,
            'isbn_10': isbn_10,
            'isbn': isbn_13 or isbn_10,
            'average_rating': volume_info.get('averageRating'),
            'ratings_count': volume_info.get('ratingsCount'),
            'published_date': volume_info.get('publishedDate'),
            'description': volume_info.get('description'),
            'page_count': volume_info.get('pageCount'),
            'categories': volume_info.get('categories', [])
        }
    except requests.exceptions.RequestException as e:
        print(f"Error getting book details for ID {google_books_id}: {e}")

    return None

def get_book_cover_url(title, author=None, isbn=None):
    """Get just the cover URL for a book"""
    result = search_book(title, author, isbn)
    return result['cover_url'] if result else None

def batch_fetch_book_data(books, delay=0.25):
    """Fetch book data for multiple books with rate limiting"""
    results = []

    for i, book in enumerate(books):
        title = book.get('book_name') or book.get('title')
        author = book.get('author')
        isbn = book.get('isbn')
        book_id = book.get('id')

        print(f"Fetching data for '{title}' by {author or 'Unknown'} ({i+1}/{len(books)})...")

        book_data = search_book(title, author, isbn)

        results.append({
            'id': book_id,
            'title': title,
            'author': author,
            'book_data': book_data
        })

        # Rate limiting - Google Books allows 1000 requests/day free tier
        if i < len(books) - 1:
            time.sleep(delay)

    return results

