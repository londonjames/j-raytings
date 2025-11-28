import requests
import json
import sqlite3
from datetime import datetime

# Google Sheets API endpoint for getting cell data including hyperlinks
SHEET_ID = "1G4v10KupkEqA7gn6KZ1yZmXxc07-ymPPTDX4gxfudiA"
API_KEY = "AIzaSyDummy"  # We'll try without API key first for public sheets

# Try to get the sheet data with hyperlinks using the Sheets API
url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}?includeGridData=true&ranges=A:N"

print("Attempting to access Google Sheets API...")
print(f"URL: {url}")

# Try without API key first (works for some public sheets)
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    print("\n✓ Successfully accessed Google Sheets!")

    # Save raw response for inspection
    with open('sheets_api_response.json', 'w') as f:
        json.dump(data, f, indent=2)

    print("Response saved to sheets_api_response.json")

    # Try to extract hyperlinks
    sheets = data.get('sheets', [])
    if sheets:
        sheet_data = sheets[0].get('data', [])
        if sheet_data:
            row_data = sheet_data[0].get('rowData', [])

            hyperlinks = []
            for row_idx, row in enumerate(row_data):
                cells = row.get('values', [])
                for col_idx, cell in enumerate(cells):
                    # Check for hyperlink
                    if 'hyperlink' in cell:
                        hyperlink_url = cell.get('hyperlink')
                        cell_value = cell.get('formattedValue', '')
                        hyperlinks.append({
                            'row': row_idx,
                            'col': col_idx,
                            'value': cell_value,
                            'url': hyperlink_url
                        })

            print(f"\nFound {len(hyperlinks)} hyperlinks in sheet")

            # Show first 20
            for h in hyperlinks[:20]:
                print(f"Row {h['row']}, Col {h['col']}: {h['value']} -> {h['url']}")

else:
    print(f"\n✗ Failed to access sheet: {response.status_code}")
    print(f"Response: {response.text[:500]}")

    print("\n" + "=" * 80)
    print("The Google Sheets API requires authentication.")
    print("Even though the sheet is 'Anyone with link', the API endpoint is different.")
    print("=" * 80)
    print("\nAlternative: Please download the sheet as HTML")
    print("  1. File → Download → Web Page (.html, zipped)")
    print("  2. Unzip and move the .html file to this directory")
    print("  3. Run the HTML parser script")
