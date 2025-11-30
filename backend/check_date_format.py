#!/usr/bin/env python3
"""Check what the actual date format is in Google Sheets"""
import os
import gspread
from google.oauth2.service_account import Credentials

SHEET_ID = "1G4v10KupkEqA7gn6KZ1yZmXxc07-ymPPTDX4gxfudiA"

def main():
    creds_path = os.getenv('GOOGLE_SHEETS_CREDENTIALS')
    if not creds_path:
        print("Error: GOOGLE_SHEETS_CREDENTIALS not set")
        return
    
    creds = Credentials.from_service_account_file(creds_path, scopes=[
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ])
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(SHEET_ID)
    sheet = spreadsheet.worksheet("all books")
    
    # Check first few date cells
    print("Checking date cells for 'The Right Stuff' (row 3)...")
    
    # Row 3, column B (Date Read) - gspread is 1-indexed
    cell = sheet.cell(3, 2)  # Row 3, Column B
    
    print(f"Cell value: {cell.value}")
    print(f"Cell formatted_value: {getattr(cell, 'formatted_value', 'N/A')}")
    print(f"Cell number_format: {getattr(cell, 'number_format', 'N/A')}")
    
    # Try getting the cell with more details
    print("\nTrying to get cell with user_entered_value...")
    try:
        # Use batch_get to get more cell details
        result = sheet.batch_get(['B3'], value_render_option='FORMATTED_VALUE')
        print(f"FORMATTED_VALUE: {result}")
        
        result = sheet.batch_get(['B3'], value_render_option='UNFORMATTED_VALUE')
        print(f"UNFORMATTED_VALUE: {result}")
        
        result = sheet.batch_get(['B3'], value_render_option='FORMULA')
        print(f"FORMULA: {result}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Check a few more rows
    print("\nChecking a few more date cells:")
    for row in [3, 4, 5]:
        cell = sheet.cell(row, 2)
        print(f"Row {row}: {cell.value}")

if __name__ == '__main__':
    main()

