# 🎬 Film Tracker - Quick Start

## Step 1: Open TWO Terminal Windows

### Terminal 1 - Start Backend
```bash
cd ~/Documents/film-tracker
./start-backend.sh
```

Wait until you see: `Running on http://127.0.0.1:5001`

### Terminal 2 - Start Frontend
```bash
cd ~/Documents/film-tracker
./start-frontend.sh
```

Wait until you see: `Local: http://localhost:5173/`

## Step 2: Open Your Browser

Go to: **http://localhost:5173**

You should see your 1,855 films!

## Troubleshooting

**"Permission denied" when running scripts?**
```bash
chmod +x ~/Documents/film-tracker/start-backend.sh
chmod +x ~/Documents/film-tracker/start-frontend.sh
```

**Backend won't start?**
- Check if Python 3 is installed: `python3 --version`
- Try manually:
  ```bash
  cd ~/Documents/film-tracker/backend
  python3 -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  python app.py
  ```

**Frontend won't start?**
- Check if Node.js is installed: `node --version`
- Try manually:
  ```bash
  cd ~/Documents/film-tracker/frontend
  npm install
  npm run dev
  ```

**Still getting "site can't be reached"?**
1. Make sure BOTH terminals are running (backend AND frontend)
2. Check Terminal 1 shows `Running on http://127.0.0.1:5001`
3. Check Terminal 2 shows `Local: http://localhost:5173/`
4. Try http://127.0.0.1:5173 instead of localhost
5. Clear your browser cache or try incognito mode

## Stop the App

Press `Ctrl+C` in both terminal windows.
