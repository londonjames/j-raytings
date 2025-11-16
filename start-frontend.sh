#!/bin/bash

echo "🎬 Starting Film Tracker Frontend..."
echo ""

cd ~/Documents/film-tracker/frontend

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Start the dev server
echo ""
echo "✅ Frontend starting on http://localhost:5173"
echo ""
npm run dev
