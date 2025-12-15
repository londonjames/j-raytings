#!/usr/bin/env python3
"""
Extract Notion hyperlinks from Google Sheets HTML export and update database
Usage: Download Google Sheet as HTML (File -> Download -> Web Page), then run this script
"""
import os
import sys
import re
from bs4 import BeautifulSoup
from urllib.parse import unquote
from import_books import get_db, init_database

def extract_hyperlinks_from_html(html_file_path: str) -> dict:
    """
    Extract hyperlinks from HTML export of Google Sheets
    
    Args:
        html_file_path: Path to the HTML file exported from Google Sheets
    
    Returns:
        Dictionary mapping order_number to Notion link URL
    """
    notion_links = {}
    
    if not os.path.exists(html_file_path):
        print(f"❌ Error: HTML file not found: {html_file_path}")
        return notion_links
    
    print(f"Reading HTML file: {html_file_path}")
    with open(html_file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find the table (Google Sheets exports as HTML table)
    table = soup.find('table')
    if not table:
        print("❌ Error: No table found in HTML file")
        return notion_links
    
    # Find header row - Google Sheets HTML exports have column letters in row 0,
    # actual headers are usually in row 1 or 2
    rows = table.find_all('tr')
    headers = []
    header_row_idx = None
    
    # Look for the row containing "Order" as the header
    for idx, row in enumerate(rows):
        cells = row.find_all(['td', 'th'])
        cell_texts = [cell.get_text(strip=True) for cell in cells]
        if 'Order' in cell_texts:
            headers = cell_texts
            header_row_idx = idx
            break
    
    if not headers:
        print("❌ Error: Could not find header row with 'Order' column")
        return notion_links
    
    # Find "Order" and "Notes in Notion" column indices
    order_col_idx = None
    notion_col_idx = None
    
    for idx, header in enumerate(headers):
        if 'Order' in header and order_col_idx is None:
            order_col_idx = idx
        if 'Notes in Notion' in header or ('Notes' in header and 'Notion' in header):
            notion_col_idx = idx
    
    if order_col_idx is None:
        print("❌ Error: Could not find 'Order' column")
        return notion_links
    
    if notion_col_idx is None:
        print("❌ Error: Could not find 'Notes in Notion' column")
        return notion_links
    
    print(f"Found columns: Order={order_col_idx}, Notes in Notion={notion_col_idx}")
    
    # Process data rows (skip header row and any empty rows after it)
    data_rows = rows[header_row_idx + 1:]
    extracted_count = 0
    
    for row in data_rows:
        cells = row.find_all(['td', 'th'])
        if len(cells) <= max(order_col_idx, notion_col_idx):
            continue
        
        # Get order number
        order_cell = cells[order_col_idx]
        order_text = order_cell.get_text(strip=True)
        if not order_text or not order_text.isdigit():
            continue
        
        order_number = int(order_text)
        
        # Get Notes in Notion cell
        notion_cell = cells[notion_col_idx]
        notion_text = notion_cell.get_text(strip=True).upper()
        
        # Only process if it says "YES"
        if notion_text != 'YES':
            continue
        
        # Look for hyperlink in the cell
        link = None
        
        # Check for <a> tag with href
        link_tag = notion_cell.find('a', href=True)
        if link_tag:
            link = link_tag.get('href', '').strip()
            # Decode URL-encoded characters
            if link:
                link = unquote(link)
        
        # If no <a> tag, check cell attributes or parent attributes
        if not link:
            # Check if cell itself has a hyperlink attribute
            link = notion_cell.get('href', '') or notion_cell.get('data-href', '')
            if link:
                link = unquote(link)
        
        # Check parent row for hyperlink
        if not link:
            link = row.get('href', '') or row.get('data-href', '')
            if link:
                link = unquote(link)
        
        if link:
            notion_links[order_number] = link
            extracted_count += 1
    
    print(f"✓ Extracted {extracted_count} Notion hyperlinks from HTML")
    return notion_links

def update_database_with_links(notion_links: dict):
    """
    Update database with extracted Notion links
    
    Args:
        notion_links: Dictionary mapping order_number to Notion link URL
    """
    if not notion_links:
        print("No links to update")
        return
    
    print("\nInitializing database...")
    init_database()
    
    db = get_db()
    updated_count = 0
    not_found_count = 0
    
    print(f"\nUpdating {len(notion_links)} Notion links in database...")
    print()
    
    for order_number, notion_link in notion_links.items():
        cursor = db.cursor()
        cursor.execute('SELECT id, notion_link FROM books WHERE order_number = ?', (order_number,))
        existing = cursor.fetchone()
        
        if existing:
            book_id, existing_link = existing
            if existing_link != notion_link:
                cursor.execute(
                    'UPDATE books SET notion_link = ? WHERE id = ?',
                    (notion_link, book_id)
                )
                updated_count += 1
                print(f"  ✓ Updated order {order_number}: {notion_link[:60]}...")
        else:
            not_found_count += 1
            print(f"  ⚠ Order {order_number} not found in database")
    
    db.commit()
    db.close()
    
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"  Notion links extracted from HTML: {len(notion_links)}")
    print(f"  Updated in database: {updated_count}")
    print(f"  Books not found in database: {not_found_count}")
    print()
    print("✓ Notion links update complete!")

def main():
    print("=" * 80)
    print("EXTRACT NOTION LINKS FROM GOOGLE SHEETS HTML EXPORT")
    print("=" * 80)
    print()
    print("Instructions:")
    print("1. Open your Google Sheet")
    print("2. File -> Download -> Web Page (.html, zipped)")
    print("3. Unzip the downloaded file")
    print("4. Run this script with the path to the HTML file")
    print()
    
    if len(sys.argv) < 2:
        print("Usage: python3 extract_notion_links_from_html.py <path_to_html_file>")
        print()
        print("Example:")
        print("  python3 extract_notion_links_from_html.py ~/Downloads/all_books.html")
        return
    
    html_file = sys.argv[1]
    
    # Extract hyperlinks
    notion_links = extract_hyperlinks_from_html(html_file)
    
    if not notion_links:
        print("\n❌ No Notion links extracted. Please check:")
        print("  - Is the HTML file from the correct sheet?")
        print("  - Does it contain the 'Notes in Notion' column?")
        print("  - Are there cells with 'YES' that have hyperlinks?")
        return
    
    # Update database
    update_database_with_links(notion_links)

if __name__ == '__main__':
    main()
