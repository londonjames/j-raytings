#!/usr/bin/env python3
"""Check what sheets are available in the spreadsheet"""
import os
import gspread
from google.oauth2.service_account import Credentials

SHEET_ID = "1G4v10KupkEqA7gn6KZ1yZmXxc07-ymPPTDX4gxfudiA"

def main():
    creds_path = os.getenv('GOOGLE_SHEETS_CREDENTIALS')
    if creds_path and os.path.exists(creds_path):
        creds = Credentials.from_service_account_file(creds_path, scopes=[
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ])
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(SHEET_ID)
        
        print("Available sheets:")
        for sheet in spreadsheet.worksheets():
            print(f"  - Name: '{sheet.title}' (ID: {sheet.id}, Rows: {sheet.row_count})")
        
        # Try to get books sheet
        print("\nTrying to access 'all books' sheet...")
        try:
            books_sheet = spreadsheet.worksheet("all books")
            print(f"✓ Found 'all books' sheet")
            print(f"  First few rows:")
            values = books_sheet.get_all_values()
            for i, row in enumerate(values[:5]):
                print(f"  Row {i+1}: {row[:5]}")
        except Exception as e:
            print(f"✗ Error accessing 'all books': {e}")
        
        # Try by gid=2
        print("\nTrying to access sheet by gid=2...")
        for sheet in spreadsheet.worksheets():
            if sheet.id == 2:
                print(f"✓ Found sheet with gid=2: '{sheet.title}'")
                values = sheet.get_all_values()
                print(f"  First few rows:")
                for i, row in enumerate(values[:5]):
                    print(f"  Row {i+1}: {row[:5]}")
                break
    else:
        print("Error: GOOGLE_SHEETS_CREDENTIALS not set")

if __name__ == '__main__':
    main()

