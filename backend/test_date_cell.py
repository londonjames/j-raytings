#!/usr/bin/env python3
"""Test getting actual date values from Google Sheets cells"""
import os
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta

SHEET_ID = "1G4v10KupkEqA7gn6KZ1yZmXxc07-ymPPTDX4gxfudiA"

def excel_date_to_python_date(excel_date):
    """Convert Excel/Google Sheets date serial number to Python date"""
    if isinstance(excel_date, (int, float)):
        # Excel/Sheets epoch is December 30, 1899
        base_date = datetime(1899, 12, 30)
        return base_date + timedelta(days=int(excel_date))
    return None

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
    
    # Test row 3 (The Right Stuff)
    print("Testing date cell B3 (The Right Stuff)...")
    
    # Method 1: Get cell directly
    cell = sheet.cell(3, 2)  # Row 3, Column B
    print(f"\nMethod 1 - Direct cell access:")
    print(f"  cell.value: {cell.value}")
    print(f"  cell.numeric_value: {getattr(cell, 'numeric_value', 'N/A')}")
    
    # Method 2: Get with different value render options
    print(f"\nMethod 2 - Batch get with different render options:")
    
    # FORMATTED_VALUE - what user sees
    try:
        formatted = sheet.batch_get(['B3'], value_render_option='FORMATTED_VALUE')
        print(f"  FORMATTED_VALUE: {formatted}")
    except Exception as e:
        print(f"  FORMATTED_VALUE error: {e}")
    
    # UNFORMATTED_VALUE - raw value (might be date serial)
    try:
        unformatted = sheet.batch_get(['B3'], value_render_option='UNFORMATTED_VALUE')
        print(f"  UNFORMATTED_VALUE: {unformatted}")
        if unformatted and unformatted[0] and len(unformatted[0]) > 0:
            val = unformatted[0][0]
            print(f"    Type: {type(val)}, Value: {val}")
            if isinstance(val, (int, float)) and val > 0:
                date_obj = excel_date_to_python_date(val)
                if date_obj:
                    print(f"    Converted to date: {date_obj.strftime('%B %d, %Y')}")
    except Exception as e:
        print(f"  UNFORMATTED_VALUE error: {e}")
    
    # Method 3: Get cell with user_entered_value
    print(f"\nMethod 3 - Get all cell data:")
    try:
        # Use the raw API to get cell formatting info
        from googleapiclient.discovery import build
        service = build('sheets', 'v4', credentials=creds)
        result = service.spreadsheets().values().get(
            spreadsheetId=SHEET_ID,
            range='all books!B3',
            valueRenderOption='FORMATTED_VALUE'
        ).execute()
        values = result.get('values', [])
        print(f"  API FORMATTED_VALUE: {values}")
        
        result = service.spreadsheets().values().get(
            spreadsheetId=SHEET_ID,
            range='all books!B3',
            valueRenderOption='UNFORMATTED_VALUE'
        ).execute()
        values = result.get('values', [])
        print(f"  API UNFORMATTED_VALUE: {values}")
        if values and values[0] and len(values[0]) > 0:
            val = values[0][0]
            if isinstance(val, (int, float)) and val > 0:
                date_obj = excel_date_to_python_date(val)
                if date_obj:
                    print(f"    Converted: {date_obj.strftime('%B %d, %Y')}")
    except Exception as e:
        print(f"  API method error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()

