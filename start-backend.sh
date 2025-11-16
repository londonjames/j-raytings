#!/bin/bash

echo "🎬 Starting Film Tracker Backend..."
echo ""

cd ~/Documents/film-tracker/backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Check if port 5000 is in use
if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  Port 5000 is already in use. Using port 5001 instead..."
    export FLASK_RUN_PORT=5001
    PORT=5001
else
    PORT=5000
fi

# Start the server
echo ""
echo "✅ Backend starting on http://localhost:$PORT"
echo ""
python app.py
