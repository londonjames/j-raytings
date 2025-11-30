#!/bin/bash

echo "=========================================="
echo "Google Sheets API Setup Guide"
echo "=========================================="
echo ""
echo "This script will guide you through setting up Google Sheets API."
echo ""

# Step 1: Check if they want to proceed
read -p "Do you want to proceed with the setup? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Setup cancelled."
    exit 1
fi

echo ""
echo "STEP 1: Create Google Cloud Project"
echo "-----------------------------------"
echo "1. Open: https://console.cloud.google.com/"
echo "2. Click 'Select a project' at the top"
echo "3. Click 'New Project'"
echo "4. Enter project name: 'film-tracker'"
echo "5. Click 'Create'"
echo ""
read -p "Press Enter when you've created the project..."

echo ""
echo "STEP 2: Enable Google Sheets API"
echo "---------------------------------"
echo "1. In Google Cloud Console, go to: APIs & Services > Library"
echo "2. Search for 'Google Sheets API'"
echo "3. Click on it and click 'Enable'"
echo ""
read -p "Press Enter when API is enabled..."

echo ""
echo "STEP 3: Create Service Account"
echo "-------------------------------"
echo "1. Go to: APIs & Services > Credentials"
echo "2. Click 'Create Credentials' > 'Service Account'"
echo "3. Service account name: 'film-tracker-sheets'"
echo "4. Click 'Create and Continue'"
echo "5. Skip role assignment (click 'Continue')"
echo "6. Click 'Done'"
echo ""
read -p "Press Enter when service account is created..."

echo ""
echo "STEP 4: Create Service Account Key"
echo "----------------------------------"
echo "1. Click on the service account you just created"
echo "2. Go to 'Keys' tab"
echo "3. Click 'Add Key' > 'Create new key'"
echo "4. Choose 'JSON' format"
echo "5. Click 'Create' - this downloads a JSON file"
echo ""
read -p "Press Enter when you've downloaded the JSON key file..."

echo ""
echo "STEP 5: Locate the JSON Key File"
echo "---------------------------------"
read -p "Enter the full path to the downloaded JSON file: " JSON_PATH

if [ ! -f "$JSON_PATH" ]; then
    echo "Error: File not found at $JSON_PATH"
    exit 1
fi

echo ""
echo "STEP 6: Share Google Sheet with Service Account"
echo "------------------------------------------------"
echo "1. Open the JSON file you downloaded"
echo "2. Find the 'client_email' field (looks like: film-tracker-sheets@...iam.gserviceaccount.com)"
echo "3. Copy that email address"
echo ""
read -p "Press Enter when you have the email copied..."

echo ""
echo "4. Open your Google Sheet:"
echo "   https://docs.google.com/spreadsheets/d/1G4v10KupkEqA7gn6KZ1yZmXxc07-ymPPTDX4gxfudiA"
echo "5. Click 'Share' button"
echo "6. Paste the service account email"
echo "7. Give it 'Editor' permissions"
echo "8. Click 'Send'"
echo ""
read -p "Press Enter when sheet is shared..."

echo ""
echo "STEP 7: Configure Credentials"
echo "-----------------------------"
echo "Choose how to store credentials:"
echo "1. Environment variable (file path)"
echo "2. Environment variable (JSON content)"
read -p "Enter choice (1 or 2): " CRED_CHOICE

if [ "$CRED_CHOICE" == "1" ]; then
    echo ""
    echo "Setting GOOGLE_SHEETS_CREDENTIALS environment variable..."
    export GOOGLE_SHEETS_CREDENTIALS="$JSON_PATH"
    echo "export GOOGLE_SHEETS_CREDENTIALS=\"$JSON_PATH\"" >> ~/.zshrc
    echo "✓ Credentials configured (added to ~/.zshrc)"
elif [ "$CRED_CHOICE" == "2" ]; then
    echo ""
    echo "Setting GOOGLE_SHEETS_CREDENTIALS_JSON environment variable..."
    export GOOGLE_SHEETS_CREDENTIALS_JSON="$(cat $JSON_PATH)"
    echo "export GOOGLE_SHEETS_CREDENTIALS_JSON='$(cat $JSON_PATH)'" >> ~/.zshrc
    echo "✓ Credentials configured (added to ~/.zshrc)"
else
    echo "Invalid choice"
    exit 1
fi

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Testing connection..."
cd "$(dirname "$0")"
python3 test_google_sheets.py

