#!/usr/bin/env python3
"""
Debug script to inspect hyperlink extraction from Google Sheets
"""
import os
import requests
import json
from google.oauth2.service_account import Credentials
from google.auth.transport.requests import Request as GoogleRequest

SHEET_ID = "1G4v10KupkEqA7gn6KZ1yZmXxc07-ymPPTDX4gxfudiA"
BOOKS_SHEET_NAME = "all books"

def main():
    # Get credentials
    creds_path = os.getenv('GOOGLE_SHEETS_CREDENTIALS')
    creds_json = os.getenv('GOOGLE_SHEETS_CREDENTIALS_JSON')
    
    if creds_json:
        creds_info = json.loads(creds_json)
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
        print("Error: No credentials")
        return
    
    if not creds.valid:
        creds.refresh(GoogleRequest())
    
    # Test with a small range first (rows 3-10, column M which is index 12)
    range_name = f"'{BOOKS_SHEET_NAME}'!M3:M10"
    
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}"
    params = {
        'includeGridData': 'true',
        'ranges': range_name,
        'fields': 'sheets.data.rowData.values(hyperlink,textFormatRuns,userEnteredFormat,effectiveValue)'
    }
    
    headers = {
        'Authorization': f'Bearer {creds.token}',
        'Content-Type': 'application/json'
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("\nFull response structure:")
        print(json.dumps(data, indent=2)[:2000])  # First 2000 chars
        
        # Try to extract links
        sheets = data.get('sheets', [])
        for sheet in sheets:
            sheet_data = sheet.get('data', [])
            for data_range in sheet_data:
                row_data = data_range.get('rowData', [])
                print(f"\nFound {len(row_data)} rows")
                
                for idx, row in enumerate(row_data, start=3):
                    print(f"\nRow {idx}:")
                    values = row.get('values', [])
                    if values:
                        cell = values[0]
                        print(f"  Cell keys: {list(cell.keys())}")
                        if 'hyperlink' in cell:
                            print(f"  Direct hyperlink: {cell['hyperlink']}")
                        if 'textFormatRuns' in cell:
                            print(f"  textFormatRuns: {len(cell['textFormatRuns'])} runs")
                            for i, run in enumerate(cell['textFormatRuns'][:3]):  # First 3
                                print(f"    Run {i}: {json.dumps(run, indent=4)[:300]}")
                        if 'userEnteredFormat' in cell:
                            print(f"  userEnteredFormat: {json.dumps(cell['userEnteredFormat'], indent=2)[:300]}")
    else:
        print(f"Error: {response.text}")

if __name__ == '__main__':
    main()
