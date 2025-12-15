"""
Google Sheets API Service
Handles reading from and writing to Google Sheets using the Google Sheets API
"""
import os
import gspread
import requests
import json
from google.oauth2.service_account import Credentials
from google.auth.transport.requests import Request as GoogleRequest
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

def get_notion_hyperlinks(col_idx: int, start_row: int, end_row: int, gid: int = 2) -> Dict[int, str]:
    """
    Extract Notion hyperlinks from a specific column using Google Sheets API
    Processes in batches to avoid rate limits and API size limits
    
    Args:
        col_idx: Column index (0-based) for "Notes in Notion" column
        start_row: Starting row index (1-based, after header)
        end_row: Ending row index (1-based)
        gid: Sheet ID (gid=2 for "all books")
    
    Returns:
        Dictionary mapping row index (1-based) to Notion link URL
    """
    notion_links = {}
    
    try:
        # Get credentials for API request
        creds_path = os.getenv('GOOGLE_SHEETS_CREDENTIALS')
        creds_json = os.getenv('GOOGLE_SHEETS_CREDENTIALS_JSON')
        
        if creds_json:
            import json as json_lib
            creds_info = json_lib.loads(creds_json)
            creds = Credentials.from_service_account_info(creds_info, scopes=[
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ])
        elif creds_path and os.path.exists(creds_path):
            creds = Credentials.from_service_account_file(creds_path, scopes=[
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ])
        else:
            print("Warning: Could not get credentials for hyperlink extraction")
            return notion_links
        
        # Refresh credentials if needed
        if not creds.valid:
            creds.refresh(GoogleRequest())
        
        # Convert column index to letter (A=0, B=1, etc.)
        # Handle columns beyond Z (AA, AB, etc.)
        if col_idx < 26:
            col_letter = chr(ord('A') + col_idx)
        else:
            first_letter = chr(ord('A') + (col_idx // 26) - 1)
            second_letter = chr(ord('A') + (col_idx % 26))
            col_letter = first_letter + second_letter
        
        # Process in batches of 100 rows to avoid API limits
        batch_size = 100
        headers = {
            'Authorization': f'Bearer {creds.token}',
            'Content-Type': 'application/json'
        }
        
        for batch_start in range(start_row, end_row + 1, batch_size):
            batch_end = min(batch_start + batch_size - 1, end_row)
            range_name = f"'{BOOKS_SHEET_NAME}'!{col_letter}{batch_start}:{col_letter}{batch_end}"
            
            # Build API request URL - correct format for Google Sheets API v4
            url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}"
            params = {
                'includeGridData': 'true',
                'ranges': range_name,
                'fields': 'sheets.data.rowData.values(hyperlink,textFormatRuns,userEnteredFormat,effectiveValue,formattedValue)'
            }
            
            try:
                response = requests.get(url, headers=headers, params=params, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    sheets = data.get('sheets', [])
                    
                    for sheet in sheets:
                        sheet_data = sheet.get('data', [])
                        for data_range in sheet_data:
                            row_data = data_range.get('rowData', [])
                            
                            for idx, row in enumerate(row_data):
                                row_idx = batch_start + idx
                                values = row.get('values', [])
                                if values and len(values) > 0:
                                    cell = values[0]
                                    
                                    # Check for direct hyperlink
                                    if 'hyperlink' in cell and cell['hyperlink']:
                                        notion_links[row_idx] = cell['hyperlink']
                                        continue
                                    
                                    # Check textFormatRuns for hyperlinks (most common location)
                                    # textFormatRuns can have hyperlinks even when cell value is just "YES"
                                    text_format_runs = cell.get('textFormatRuns', [])
                                    if text_format_runs:
                                        for run in text_format_runs:
                                            run_format = run.get('format', {})
                                            # Check multiple possible locations for link
                                            if 'link' in run_format:
                                                link_obj = run_format['link']
                                                if isinstance(link_obj, dict):
                                                    link_url = link_obj.get('uri', '') or link_obj.get('url', '') or link_obj.get('linkUri', '')
                                                elif isinstance(link_obj, str):
                                                    link_url = link_obj
                                                else:
                                                    link_url = str(link_obj)
                                                if link_url and link_url not in ['', 'None']:
                                                    notion_links[row_idx] = link_url
                                                    break
                                            # Also check nested link structure
                                            if isinstance(run_format, dict):
                                                for key in ['link', 'hyperlink', 'url']:
                                                    if key in run_format:
                                                        link_val = run_format[key]
                                                        if isinstance(link_val, dict):
                                                            link_url = link_val.get('uri', '') or link_val.get('url', '')
                                                        elif isinstance(link_val, str):
                                                            link_url = link_val
                                                        else:
                                                            link_url = str(link_val)
                                                        if link_url and link_url not in ['', 'None']:
                                                            notion_links[row_idx] = link_url
                                                            break
                                                    if row_idx in notion_links:
                                                        break
                                                if row_idx in notion_links:
                                                    break
                                    
                                    # Check userEnteredFormat for hyperlink
                                    user_format = cell.get('userEnteredFormat', {})
                                    if user_format and 'link' in user_format:
                                        link_obj = user_format['link']
                                        if isinstance(link_obj, dict):
                                            link_url = link_obj.get('uri', '') or link_obj.get('url', '')
                                        elif isinstance(link_obj, str):
                                            link_url = link_obj
                                        else:
                                            link_url = str(link_obj)
                                        if link_url and link_url not in ['', 'None']:
                                            notion_links[row_idx] = link_url
                                    
                                    # Also check if hyperlink is a direct string in the cell
                                    if 'hyperlink' in cell:
                                        hyperlink_val = cell['hyperlink']
                                        if isinstance(hyperlink_val, str) and hyperlink_val:
                                            notion_links[row_idx] = hyperlink_val
                                        elif isinstance(hyperlink_val, dict):
                                            link_url = hyperlink_val.get('uri', '') or hyperlink_val.get('url', '')
                                            if link_url:
                                                notion_links[row_idx] = link_url
                                    
                                    # Check effectiveValue for HYPERLINK formulas
                                    effective_value = cell.get('effectiveValue', {})
                                    if effective_value:
                                        # Check if it's a formula value with HYPERLINK
                                        formula_value = effective_value.get('formulaValue', '')
                                        if formula_value and 'HYPERLINK' in formula_value.upper():
                                            # Extract URL from HYPERLINK formula: HYPERLINK("url","text")
                                            import re
                                            match = re.search(r'HYPERLINK\s*\(\s*"([^"]+)"', formula_value, re.IGNORECASE)
                                            if match:
                                                notion_links[row_idx] = match.group(1)
                elif response.status_code == 429:
                    print(f"  Rate limit hit, waiting before retrying batch {batch_start}-{batch_end}...")
                    import time
                    time.sleep(2)
                    # Retry once
                    response = requests.get(url, headers=headers, params=params, timeout=30)
                    if response.status_code == 200:
                        # Process response same as above
                        data = response.json()
                        sheets = data.get('sheets', [])
                        for sheet in sheets:
                            sheet_data = sheet.get('data', [])
                            for data_range in sheet_data:
                                row_data = data_range.get('rowData', [])
                                for idx, row in enumerate(row_data):
                                    row_idx = batch_start + idx
                                    values = row.get('values', [])
                                    if values and len(values) > 0:
                                        cell = values[0]
                                        if 'hyperlink' in cell and cell['hyperlink']:
                                            notion_links[row_idx] = cell['hyperlink']
                                            continue
                                        text_format_runs = cell.get('textFormatRuns', [])
                                        if text_format_runs:
                                            for run in text_format_runs:
                                                run_format = run.get('format', {})
                                                if 'link' in run_format:
                                                    link_obj = run_format['link']
                                                    link_url = link_obj.get('uri', '') if isinstance(link_obj, dict) else str(link_obj)
                                                    if link_url:
                                                        notion_links[row_idx] = link_url
                                                        break
                                        user_format = cell.get('userEnteredFormat', {})
                                        if 'link' in user_format:
                                            link_obj = user_format['link']
                                            link_url = link_obj.get('uri', '') if isinstance(link_obj, dict) else str(link_obj)
                                            if link_url:
                                                notion_links[row_idx] = link_url
                else:
                    print(f"  Warning: API request failed for batch {batch_start}-{batch_end}: {response.status_code}")
                    if response.status_code != 200:
                        print(f"  Response: {response.text[:200]}")
                
                # Small delay between batches to avoid rate limits
                import time
                time.sleep(0.1)
                
            except Exception as e:
                print(f"  Error processing batch {batch_start}-{batch_end}: {e}")
                continue
        
    except Exception as e:
        print(f"Warning: Could not retrieve hyperlinks from Notes in Notion column: {e}")
        import traceback
        traceback.print_exc()
    
    return notion_links

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
    
    # Extract Notion hyperlinks from "Notes in Notion" column
    notion_col_idx = col_map.get('Notes in Notion', None)
    notion_links = {}
    if notion_col_idx is not None:
        data_start_row = header_row_idx + 2
        data_end_row = len(all_values)
        if data_end_row >= data_start_row:
            print(f"Extracting Notion hyperlinks from column {notion_col_idx} (rows {data_start_row}-{data_end_row})...")
            notion_links = get_notion_hyperlinks(notion_col_idx, data_start_row, data_end_row, gid=2)
            print(f"✓ Extracted {len(notion_links)} Notion hyperlinks")
    
    # Second pass: build book dicts with converted dates and Notion links
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
        
        # Add Notion link if available
        if row_idx in notion_links:
            book['Notion Link'] = notion_links[row_idx]
        
        books.append(book)
    
    return books

def get_films_data() -> List[Dict[str, Any]]:
    """
    Get all films data from Google Sheets with exact dates
    
    Returns:
        List of dictionaries with film data
    """
    sheet = get_sheet(sheet_name=FILMS_SHEET_NAME, gid=0)
    
    # Get all values (handles empty first column)
    all_values = sheet.get_all_values()
    
    if not all_values or len(all_values) < 2:
        return []
    
    # Find header row (skip empty rows at top)
    header_row_idx = None
    headers = []
    col_map = {}
    
    for idx, row in enumerate(all_values):
        if row and any(cell.strip() for cell in row):
            # Found header row
            header_row_idx = idx
            # Skip empty first column
            headers = [h.strip() for h in row[1:]] if row[0].strip() == '' else [h.strip() for h in row]
            break
    
    if header_row_idx is None:
        return []
    
    # Build column map (adjust for empty first column)
    start_col = 1 if all_values[header_row_idx][0].strip() == '' else 0
    for idx, header in enumerate(headers):
        col_map[header] = idx + start_col
    
    # Get date column index (adjust for empty first column)
    date_col_name = 'Date Film Seen'
    date_col_idx = col_map.get(date_col_name)
    if date_col_idx is None:
        date_col_name = 'Date Seen'
        date_col_idx = col_map.get(date_col_name)
    
    # Get all data rows
    films = []
    data_start_row = header_row_idx + 1
    
    # Use batch_get to get unformatted date values (date serial numbers)
    if date_col_idx is not None:
        # Get date column with unformatted values
        date_range = f"{chr(65 + date_col_idx)}{data_start_row + 1}:{chr(65 + date_col_idx)}{len(all_values)}"
        try:
            date_values = sheet.batch_get([date_range], value_render_option='UNFORMATTED_VALUE')
            date_serials = date_values[0] if date_values else []
        except Exception as e:
            print(f"Warning: Could not get unformatted dates: {e}")
            date_serials = []
    else:
        date_serials = []
    
    # Process each data row
    for row_idx, row in enumerate(all_values[data_start_row:], start=data_start_row + 1):
        # Skip empty rows
        if not row or (len(row) > 0 and not row[0].strip() and not any(cell.strip() for cell in row[1:] if len(row) > 1)):
            continue
        
        # Adjust for empty first column
        row_data = row[1:] if len(row) > 0 and row[0].strip() == '' else row
        
        # Build film dict
        film = {}
        for header, col_idx in col_map.items():
            adjusted_idx = col_idx - (1 if len(row) > 0 and row[0].strip() == '' else 0)
            if adjusted_idx >= 0 and adjusted_idx < len(row_data):
                value = row_data[adjusted_idx].strip() if row_data[adjusted_idx] else ''
                film[header] = value
        
        # Convert date serial number to "Month Day, YYYY" format
        if date_col_idx is not None:
            date_row_idx = row_idx - data_start_row - 1
            if date_row_idx >= 0 and date_row_idx < len(date_serials):
                date_row = date_serials[date_row_idx]
                if date_row and len(date_row) > 0:
                    date_serial = date_row[0]
                    if isinstance(date_serial, (int, float)) and date_serial > 0:
                        # Convert Excel/Sheets date serial to datetime
                        # Excel epoch is December 30, 1899
                        excel_epoch = datetime(1899, 12, 30)
                        try:
                            date_obj = excel_epoch + timedelta(days=int(date_serial))
                            month_name = date_obj.strftime('%B')  # Full month name
                            day = date_obj.day
                            year = date_obj.year
                            film[date_col_name] = f"{month_name} {day}, {year}"
                        except Exception as e:
                            # If conversion fails, use the original value
                            pass
        
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

