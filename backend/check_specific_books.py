#!/usr/bin/env python3
"""
Check specific books for Notion hyperlinks in Google Sheets
"""
import os
from google_sheets_service import get_notion_hyperlinks, get_sheet, BOOKS_SHEET_NAME

def check_books():
    # These are the 5 books with YES but no hyperlink in Excel
    # Row numbers in Google Sheets (header is row 2, so data starts at row 3)
    # Order numbers: 44, 51, 60, 62, 64
    # Excel rows: 46, 53, 62, 64, 66
    
    # Get the sheet to find actual row numbers
    sheet = get_sheet(sheet_name=BOOKS_SHEET_NAME, gid=2)
    all_values = sheet.get_all_values()
    
    # Find header row
    header_row_idx = None
    col_map = {}
    for idx, row in enumerate(all_values):
        if 'Order' in row:
            header_row_idx = idx
            for col_idx, header in enumerate(row):
                header_clean = header.strip()
                if header_clean:
                    col_map[header_clean] = col_idx
            break
    
    if not col_map:
        print("Could not find header row")
        return
    
    # Find rows for these order numbers
    order_col_idx = col_map.get('Order', 0)
    notion_col_idx = col_map.get('Notes in Notion', 12)  # Column M = index 12
    
    target_orders = [44, 51, 60, 62, 64]
    target_rows = {}
    
    for row_idx in range(header_row_idx + 1, len(all_values)):
        row = all_values[row_idx]
        if len(row) > order_col_idx:
            try:
                order_val = row[order_col_idx].strip()
                if order_val:
                    order_num = int(float(order_val))
                    if order_num in target_orders:
                        target_rows[order_num] = row_idx + 1  # 1-indexed row number
                        if len(target_rows) == len(target_orders):
                            break
            except (ValueError, IndexError):
                continue
    
    print(f"Found rows for orders: {target_rows}")
    print()
    
    # Check hyperlinks for these specific rows
    min_row = min(target_rows.values())
    max_row = max(target_rows.values())
    
    print(f"Checking rows {min_row}-{max_row} for Notion hyperlinks...")
    notion_links = get_notion_hyperlinks(notion_col_idx, min_row, max_row, gid=2)
    
    print(f"\nResults:")
    for order_num, row_num in sorted(target_rows.items()):
        if row_num in notion_links:
            link = notion_links[row_num]
            print(f"Order {order_num} (row {row_num}): ✓ HAS hyperlink")
            print(f"  {link[:80]}...")
        else:
            print(f"Order {order_num} (row {row_num}): ✗ NO hyperlink found")
        print()

if __name__ == '__main__':
    check_books()
