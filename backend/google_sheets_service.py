"""
Google Sheets API Service
Handles reading from and writing to Google Sheets using the Google Sheets API
"""
import os
import gspread
from google.oauth2.service_account import Credentials
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta

# Google Sheets ID
SHEET_ID = "1G4v10KupkEqA7gn6KZ1yZmXxc07-ymPPTDX4gxfudiA"

# Sheet names/tab IDs
BOOKS_SHEET_NAME = "all books"  # gid=2
FILMS_SHEET_NAME = "all films"  # gid=0

def get_sheets_client():
    """
    Get authenticated Google Sheets client
    
    Requires:
    - GOOGLE_SHEETS_CREDENTIALS environment variable with path to service account JSON
    - OR GOOGLE_SHEETS_CREDENTIALS_JSON environment variable with JSON content
    """
    # Check for credentials file path
    creds_path = os.getenv('GOOGLE_SHEETS_CREDENTIALS')
    creds_json = os.getenv('GOOGLE_SHEETS_CREDENTIALS_JSON')
    
    if creds_json:
        # Parse JSON string from environment variable
        import json
        creds_info = json.loads(creds_json)
        creds = Credentials.from_service_account_info(creds_info, scopes=[
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ])
    elif creds_path and os.path.exists(creds_path):
        # Load from file
        creds = Credentials.from_service_account_file(creds_path, scopes=[
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ])
    else:
        raise ValueError(
            "Google Sheets credentials not found. Set GOOGLE_SHEETS_CREDENTIALS (file path) "
            "or GOOGLE_SHEETS_CREDENTIALS_JSON (JSON string) environment variable."
        )
    
    return gspread.authorize(creds)

def get_sheet(sheet_name: str = None, gid: int = None):
    """
    Get a specific sheet (tab) from the spreadsheet
    
    Args:
        sheet_name: Name of the sheet tab (e.g., "all books")
        gid: Sheet ID (gid) if sheet_name doesn't work
    
    Returns:
        gspread Worksheet object
    """
    client = get_sheets_client()
    spreadsheet = client.open_by_key(SHEET_ID)
    
    if sheet_name:
        try:
            return spreadsheet.worksheet(sheet_name)
        except gspread.exceptions.WorksheetNotFound:
            print(f"Sheet '{sheet_name}' not found, trying by gid...")
    
    if gid:
        # Get sheet by gid
        for sheet in spreadsheet.worksheets():
            if sheet.id == gid:
                return sheet
    
    raise ValueError(f"Sheet not found: {sheet_name or f'gid={gid}'}")

def get_books_data() -> List[Dict[str, Any]]:
    """
    Get all books data from Google Sheets with exact dates
    
    Returns:
        List of dictionaries with book data
    """
    sheet = get_sheet(sheet_name=BOOKS_SHEET_NAME, gid=2)
    
    # Get all values (handles empty first column)
    all_values = sheet.get_all_values()
    
    if not all_values or len(all_values) < 2:
        return []
    
    # Find header row (skip empty rows at top)
    header_row_idx = None
    headers = []
    col_map = {}
    
    for idx, row in enumerate(all_values):
        # Look for "Order" column to find header row
        if 'Order' in row:
            header_row_idx = idx
            headers = row
            # Map column names to indices (skip empty first column)
            for col_idx, header in enumerate(headers):
                header_clean = header.strip()
                if header_clean:
                    col_map[header_clean] = col_idx
            break
    
    if not col_map:
        return []
    
    books = []
    date_col_idx = col_map.get('Date Read', None)
    
    # Batch get all date values at once for efficiency
    date_cell_refs = []
    date_row_indices = []
    
    # First pass: collect all date cell references
    for row_idx in range(header_row_idx + 2, len(all_values) + 1):
        row = all_values[row_idx - 1]
        order_col_idx = col_map.get('Order', 0)
        if order_col_idx >= len(row) or not row[order_col_idx] or not row[order_col_idx].strip():
            continue
        
        if date_col_idx is not None:
            col_letter = chr(ord('A') + date_col_idx)
            cell_ref = f"{col_letter}{row_idx}"
            date_cell_refs.append(cell_ref)
            date_row_indices.append(row_idx)
    
    # Batch get all date values (process in chunks to avoid rate limits)
    date_values = {}
    if date_cell_refs:
        # Process in chunks of 50 to avoid rate limits
        chunk_size = 50
        for chunk_start in range(0, len(date_cell_refs), chunk_size):
            chunk_refs = date_cell_refs[chunk_start:chunk_start + chunk_size]
            chunk_indices = date_row_indices[chunk_start:chunk_start + chunk_size]
            
            try:
                # Get unformatted values (date serial numbers)
                unformatted = sheet.batch_get(chunk_refs, value_render_option='UNFORMATTED_VALUE')
                # batch_get returns: [[[value1]], [[value2]], ...] for multiple ranges
                if unformatted:
                    for idx, result in enumerate(unformatted):
                        if idx < len(chunk_indices) and result and len(result) > 0 and len(result[0]) > 0:
                            val = result[0][0]
                            if isinstance(val, (int, float)) and val > 0:
                                # Convert date serial to date
                                base_date = datetime(1899, 12, 30)
                                date_obj = base_date + timedelta(days=int(val))
                                date_values[chunk_indices[idx]] = date_obj.strftime('%B %d, %Y')
            except Exception as e:
                # Continue with other chunks even if one fails
                pass
    
    # Second pass: build book dicts with converted dates
    date_idx = 0
    for row_idx in range(header_row_idx + 2, len(all_values) + 1):
        row = all_values[row_idx - 1]
        
        # Skip empty rows
        order_col_idx = col_map.get('Order', 0)
        if order_col_idx >= len(row) or not row[order_col_idx] or not row[order_col_idx].strip():
            continue
        
        # Build book dict
        book = {}
        for header, col_idx in col_map.items():
            if col_idx < len(row):
                value = row[col_idx].strip() if row[col_idx] else ''
                book[header] = value
        
        # Replace date with converted value if available
        if row_idx in date_values:
            book['Date Read'] = date_values[row_idx]
        
        books.append(book)
    
    return books

def get_films_data() -> List[Dict[str, Any]]:
    """
    Get all films data from Google Sheets with exact dates
    
    Returns:
        List of dictionaries with film data
    """
    sheet = get_sheet(sheet_name=FILMS_SHEET_NAME, gid=0)
    
    # Get all values
    all_values = sheet.get_all_values()
    
    if not all_values or len(all_values) < 2:
        return []
    
    # First row is headers
    headers = all_values[0]
    
    # Find column indices
    col_map = {}
    for idx, header in enumerate(headers):
        col_map[header.strip()] = idx
    
    films = []
    for row_idx, row in enumerate(all_values[1:], start=2):  # Start at row 2
        if not row or not row[0]:  # Skip empty rows
            continue
        
        # Build film dict
        film = {}
        for header, col_idx in col_map.items():
            if col_idx < len(row):
                value = row[col_idx].strip() if row[col_idx] else ''
                film[header] = value
        
        # Get exact date from the cell
        date_col = col_map.get('Date Film Seen', col_map.get('Date Seen', 1))
        if date_col is not None:
            date_cell = sheet.cell(row_idx, date_col + 1)  # gspread is 1-indexed
            if date_cell and date_cell.value:
                film['Date Seen'] = date_cell.value
        
        films.append(film)
    
    return films

def update_book_in_sheet(order_number: int, updates: Dict[str, Any], sheet_name: str = BOOKS_SHEET_NAME):
    """
    Update a book row in Google Sheets
    
    Args:
        order_number: Order number to identify the row
        updates: Dictionary of column names to values to update
        sheet_name: Name of the sheet tab
    """
    sheet = get_sheet(sheet_name=sheet_name, gid=2)
    
    # Find the row by order number
    all_values = sheet.get_all_values()
    headers = all_values[0]
    
    # Find Order column
    order_col_idx = None
    for idx, header in enumerate(headers):
        if 'Order' in header:
            order_col_idx = idx
            break
    
    if order_col_idx is None:
        raise ValueError("Order column not found in sheet")
    
    # Find the row
    row_idx = None
    for idx, row in enumerate(all_values[1:], start=2):
        if len(row) > order_col_idx and str(row[order_col_idx]).strip() == str(order_number):
            row_idx = idx
            break
    
    if row_idx is None:
        raise ValueError(f"Book with order number {order_number} not found")
    
    # Update cells
    for col_name, value in updates.items():
        # Find column index
        col_idx = None
        for idx, header in enumerate(headers):
            if header.strip() == col_name:
                col_idx = idx
                break
        
        if col_idx is not None:
            sheet.update_cell(row_idx, col_idx + 1, value)  # gspread is 1-indexed

def update_film_in_sheet(order_number: int, updates: Dict[str, Any], sheet_name: str = FILMS_SHEET_NAME):
    """
    Update a film row in Google Sheets
    
    Args:
        order_number: Order number to identify the row
        updates: Dictionary of column names to values to update
        sheet_name: Name of the sheet tab
    """
    sheet = get_sheet(sheet_name=sheet_name, gid=0)
    
    # Find the row by order number
    all_values = sheet.get_all_values()
    headers = all_values[0]
    
    # Find Order column
    order_col_idx = None
    for idx, header in enumerate(headers):
        if 'Order' in header:
            order_col_idx = idx
            break
    
    if order_col_idx is None:
        raise ValueError("Order column not found in sheet")
    
    # Find the row
    row_idx = None
    for idx, row in enumerate(all_values[1:], start=2):
        if len(row) > order_col_idx and str(row[order_col_idx]).strip() == str(order_number):
            row_idx = idx
            break
    
    if row_idx is None:
        raise ValueError(f"Film with order number {order_number} not found")
    
    # Update cells
    for col_name, value in updates.items():
        # Find column index
        col_idx = None
        for idx, header in enumerate(headers):
            if header.strip() == col_name:
                col_idx = idx
                break
        
        if col_idx is not None:
            sheet.update_cell(row_idx, col_idx + 1, value)  # gspread is 1-indexed

