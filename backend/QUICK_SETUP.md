# Quick Google Sheets API Setup

## Prerequisites
- A Google account
- Access to the Google Sheet: https://docs.google.com/spreadsheets/d/1G4v10KupkEqA7gn6KZ1yZmXxc07-ymPPTDX4gxfudiA

## Automated Setup (Recommended)

Run the interactive setup script:
```bash
cd backend
./setup_google_sheets.sh
```

## Manual Setup Steps

### 1. Create Google Cloud Project
- Go to: https://console.cloud.google.com/
- Click "Select a project" → "New Project"
- Name: `film-tracker`
- Click "Create"

### 2. Enable Google Sheets API
- Go to: APIs & Services > Library
- Search: "Google Sheets API"
- Click "Enable"

### 3. Create Service Account
- Go to: APIs & Services > Credentials
- Click "Create Credentials" → "Service Account"
- Name: `film-tracker-sheets`
- Click "Create and Continue"
- Skip role assignment → "Continue" → "Done"

### 4. Create Service Account Key
- Click on the service account you created
- Go to "Keys" tab
- Click "Add Key" → "Create new key"
- Choose "JSON" → Click "Create"
- **Save the downloaded JSON file** (you'll need it!)

### 5. Share Google Sheet
1. Open the JSON file you downloaded
2. Find `"client_email"` (e.g., `film-tracker-sheets@project.iam.gserviceaccount.com`)
3. Open your Google Sheet
4. Click "Share" button
5. Paste the `client_email` address
6. Give it "Editor" permissions
7. Click "Send"

### 6. Configure Credentials

**Option A: Environment Variable (File Path)**
```bash
export GOOGLE_SHEETS_CREDENTIALS="/path/to/your/service-account-key.json"
```

**Option B: Environment Variable (JSON Content)**
```bash
export GOOGLE_SHEETS_CREDENTIALS_JSON='{"type":"service_account",...}'
```

To make it permanent, add to `~/.zshrc`:
```bash
echo 'export GOOGLE_SHEETS_CREDENTIALS="/path/to/key.json"' >> ~/.zshrc
source ~/.zshrc
```

### 7. Test Setup
```bash
cd backend
python3 test_google_sheets.py
```

## For Railway (Production)

1. Go to Railway project settings
2. Add environment variable:
   - Name: `GOOGLE_SHEETS_CREDENTIALS_JSON`
   - Value: Copy the entire contents of your JSON key file

## Troubleshooting

**Error: "Credentials not found"**
- Make sure you've set the environment variable
- Check the file path is correct
- Restart your terminal after setting environment variables

**Error: "Permission denied"**
- Make sure you shared the Google Sheet with the service account email
- Check the service account has "Editor" permissions

**Error: "API not enabled"**
- Go back to Google Cloud Console
- Make sure Google Sheets API is enabled

