import sqlite3
import requests
import time
from urllib.parse import urlparse

# Configuration
db_path = 'films.db'
sample_size = 50  # Test a sample first to estimate error rate
delay_between_requests = 0.5  # 500ms to be respectful

def test_rt_link(url, title):
    """Test if an RT link is valid"""
    try:
        # Use a HEAD request (faster than GET)
        response = requests.head(url, timeout=5, allow_redirects=True)

        # Check for common issues
        if response.status_code == 404:
            return {'status': 'NOT_FOUND', 'code': 404, 'title': title, 'url': url}
        elif response.status_code >= 400:
            return {'status': 'ERROR', 'code': response.status_code, 'title': title, 'url': url}
        elif response.url != url:  # Was redirected
            return {'status': 'REDIRECTED', 'code': response.status_code, 'title': title, 'url': url, 'redirect_to': response.url}
        else:
            return {'status': 'OK', 'code': response.status_code, 'title': title, 'url': url}
    except requests.exceptions.Timeout:
        return {'status': 'TIMEOUT', 'title': title, 'url': url}
    except requests.exceptions.RequestException as e:
        return {'status': 'ERROR', 'title': title, 'url': url, 'error': str(e)}

def analyze_rt_urls():
    """Analyze RT URL format for potential issues"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get all films with RT links
    cursor.execute("""
        SELECT id, title, rt_link
        FROM films
        WHERE rt_link IS NOT NULL AND rt_link != ''
        ORDER BY order_number ASC
    """)
    films = cursor.fetchall()
    conn.close()

    print("=" * 80)
    print(f"ROTTEN TOMATOES LINK ANALYSIS")
    print("=" * 80)
    print(f"Total films with RT links: {len(films)}\n")

    # Analyze URL format issues
    issues = {
        'special_chars': [],
        'very_long': [],
        'unusual_format': []
    }

    for film_id, title, rt_link in films:
        # Check for special characters that might cause issues
        slug = rt_link.split('/m/')[-1] if '/m/' in rt_link else ''

        # Check for characters that might indicate formatting issues
        if any(char in slug for char in ['(', ')', '[', ']', '!', '?', ':', ';', ',', "'"]):
            issues['special_chars'].append((title, rt_link))

        # Check for very long URLs (might be incorrect)
        if len(slug) > 50:
            issues['very_long'].append((title, rt_link))

        # Check for unusual format
        if not rt_link.startswith('https://www.rottentomatoes.com/m/'):
            issues['unusual_format'].append((title, rt_link))

    # Report issues
    if issues['special_chars']:
        print(f"⚠️  Found {len(issues['special_chars'])} URLs with special characters:")
        for title, url in issues['special_chars'][:10]:
            print(f"  - {title}: {url}")
        if len(issues['special_chars']) > 10:
            print(f"  ... and {len(issues['special_chars']) - 10} more")
        print()

    if issues['very_long']:
        print(f"⚠️  Found {len(issues['very_long'])} unusually long URLs:")
        for title, url in issues['very_long'][:10]:
            print(f"  - {title}: {url}")
        if len(issues['very_long']) > 10:
            print(f"  ... and {len(issues['very_long']) - 10} more")
        print()

    if issues['unusual_format']:
        print(f"⚠️  Found {len(issues['unusual_format'])} URLs with unusual format:")
        for title, url in issues['unusual_format'][:10]:
            print(f"  - {title}: {url}")
        if len(issues['unusual_format']) > 10:
            print(f"  ... and {len(issues['unusual_format']) - 10} more")
        print()

    return films

def test_sample_links(films, sample_size):
    """Test a sample of RT links"""
    import random

    print("\n" + "=" * 80)
    print(f"TESTING SAMPLE OF {sample_size} ROTTEN TOMATOES LINKS")
    print("=" * 80)
    print("This will take a moment...\n")

    # Take a random sample
    sample = random.sample(films, min(sample_size, len(films)))

    results = {
        'ok': [],
        'not_found': [],
        'error': [],
        'redirected': [],
        'timeout': []
    }

    for i, (film_id, title, rt_link) in enumerate(sample, 1):
        print(f"[{i}/{sample_size}] Testing: {title}...", end=' ')
        result = test_rt_link(rt_link, title)

        if result['status'] == 'OK':
            print("✓")
            results['ok'].append(result)
        elif result['status'] == 'NOT_FOUND':
            print("✗ 404")
            results['not_found'].append(result)
        elif result['status'] == 'REDIRECTED':
            print("⟳ Redirected")
            results['redirected'].append(result)
        elif result['status'] == 'TIMEOUT':
            print("⏱ Timeout")
            results['timeout'].append(result)
        else:
            print(f"✗ Error")
            results['error'].append(result)

        time.sleep(delay_between_requests)

    # Summary
    print("\n" + "=" * 80)
    print("TEST RESULTS SUMMARY")
    print("=" * 80)
    print(f"✓ OK: {len(results['ok'])} ({len(results['ok'])/sample_size*100:.1f}%)")
    print(f"✗ Not Found (404): {len(results['not_found'])} ({len(results['not_found'])/sample_size*100:.1f}%)")
    print(f"⟳ Redirected: {len(results['redirected'])} ({len(results['redirected'])/sample_size*100:.1f}%)")
    print(f"⏱ Timeout: {len(results['timeout'])} ({len(results['timeout'])/sample_size*100:.1f}%)")
    print(f"✗ Other Errors: {len(results['error'])} ({len(results['error'])/sample_size*100:.1f}%)")

    # Show problematic links
    if results['not_found']:
        print("\n" + "=" * 80)
        print("FILMS WITH 404 ERRORS:")
        print("=" * 80)
        for result in results['not_found']:
            print(f"  {result['title']}")
            print(f"    URL: {result['url']}\n")

    if results['redirected']:
        print("\n" + "=" * 80)
        print("FILMS WITH REDIRECTS (might be wrong):")
        print("=" * 80)
        for result in results['redirected'][:5]:
            print(f"  {result['title']}")
            print(f"    From: {result['url']}")
            print(f"    To: {result.get('redirect_to', 'N/A')}\n")

    # Estimate total issues
    error_rate = (len(results['not_found']) + len(results['error'])) / sample_size
    total_films = len(films)
    estimated_errors = int(total_films * error_rate)

    print("\n" + "=" * 80)
    print("ESTIMATED TOTAL ISSUES")
    print("=" * 80)
    print(f"Based on this sample, approximately {estimated_errors} out of {total_films} films")
    print(f"may have incorrect RT links ({error_rate*100:.1f}% error rate)")
    print("\n" + "=" * 80)

    return results

if __name__ == '__main__':
    print("\n🎬 Analyzing Rotten Tomatoes links...\n")

    # Step 1: Analyze URL format
    films = analyze_rt_urls()

    # Step 2: Test a sample
    user_input = input(f"\nTest {sample_size} random RT links? (y/n): ")
    if user_input.lower() == 'y':
        test_sample_links(films, sample_size)

    print("\n✅ Done!")
