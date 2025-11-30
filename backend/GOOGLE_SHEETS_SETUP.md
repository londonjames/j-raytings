# Google Sheets API Setup

This guide explains how to set up Google Sheets API integration for reading and writing data.

## Prerequisites

1. A Google Cloud Project
2. Google Sheets API enabled
3. Service Account credentials

## Setup Steps

### 1. Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Note your project ID

### 2. Enable Google Sheets API

1. In Google Cloud Console, go to "APIs & Services" > "Library"
2. Search for "Google Sheets API"
3. Click "Enable"

### 3. Create Service Account

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "Service Account"
3. Fill in:
   - Service account name: `film-tracker-sheets`
   - Service account ID: (auto-generated)
   - Description: "Service account for Film Tracker Google Sheets integration"
4. Click "Create and Continue"
5. Skip role assignment (click "Continue")
6. Click "Done"

### 4. Create Service Account Key

1. Click on the service account you just created
2. Go to "Keys" tab
3. Click "Add Key" > "Create new key"
4. Choose "JSON" format
5. Click "Create" - this downloads a JSON file

### 5. Share Google Sheet with Service Account

1. Open the JSON file you downloaded
2. Find the `client_email` field (e.g., `film-tracker-sheets@your-project.iam.gserviceaccount.com`)
3. Open your Google Sheet: https://docs.google.com/spreadsheets/d/1G4v10KupkEqA7gn6KZ1yZmXxc07-ymPPTDX4gxfudiA
4. Click "Share" button
5. Paste the `client_email` address
6. Give it "Editor" permissions
7. Click "Send"

### 6. Configure Credentials

**Option A: Environment Variable (File Path)**
```bash
export GOOGLE_SHEETS_CREDENTIALS="/path/to/your/service-account-key.json"
```

**Option B: Environment Variable (JSON String)**
```bash
export GOOGLE_SHEETS_CREDENTIALS_JSON='{"type":"service_account","project_id":"...","private_key_id":"...","private_key":"...","client_email":"...","client_id":"...","auth_uri":"...","token_uri":"...","auth_provider_x509_cert_url":"...","client_x509_cert_url":"..."}'
```

**For Railway (Production):**
1. Go to Railway project settings
2. Add environment variable:
   - Name: `GOOGLE_SHEETS_CREDENTIALS_JSON`
   - Value: Paste the entire JSON content from the service account key file

### 7. Install Dependencies

```bash
pip install -r requirements.txt
```

## Usage

Once set up, you can use the Google Sheets service:

```python
from google_sheets_service import get_books_data, update_book_in_sheet

# Read books with exact dates
books = get_books_data()

# Update a book in the sheet
update_book_in_sheet(
    order_number=1,
    updates={
        'Cover URL': 'https://example.com/cover.jpg',
        'Notes in Notion': 'YES'
    }
)
```

## Testing

Run the test script:
```bash
python test_google_sheets.py
```

