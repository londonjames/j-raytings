# Setting Up Movie Posters

This guide will help you set up automatic movie poster fetching from The Movie Database (TMDB).

## Step 1: Get a Free TMDB API Key

1. Go to https://www.themoviedb.org/
2. Click "Join TMDB" and create a free account
3. Verify your email address
4. Go to your account Settings → API
5. Click "Request an API Key"
6. Choose "Developer" (not commercial)
7. Fill out the form:
   - **Application Name**: "Personal Film Tracker" (or anything you like)
   - **Application URL**: http://localhost:5173
   - **Application Summary**: "Personal film tracking application"
8. Accept the terms and submit
9. You'll instantly receive your API Key (v3 auth)

## Step 2: Configure Your API Key

In your terminal, set the environment variable:

```bash
export TMDB_API_KEY='your_api_key_here'
```

**To make it permanent**, add it to your shell profile:

```bash
# For bash
echo "export TMDB_API_KEY='your_api_key_here'" >> ~/.bash_profile

# For zsh (macOS default)
echo "export TMDB_API_KEY='your_api_key_here'" >> ~/.zshrc
```

Then reload your terminal or run:
```bash
source ~/.zshrc  # or ~/.bash_profile
```

## Step 3: Install Additional Dependencies

```bash
cd backend
source venv/bin/activate  # if not already activated
pip install -r requirements.txt
```

## Step 4: Fetch Posters for Your Films

### Test with a few films first:

```bash
cd backend
python fetch_posters.py --limit 10
```

### Fetch all posters:

```bash
python fetch_posters.py
```

This will:
- Fetch posters for all 1,855 films
- Take approximately 7-8 minutes (rate-limited to respect TMDB's API limits)
- Save poster URLs directly to your database

### Only fetch missing posters (if you run it again later):

```bash
python fetch_posters.py --missing-only
```

## Step 5: Start Your App

Now when you run your app, all films will display their movie posters!

```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate
export TMDB_API_KEY='your_key_here'  # if not in profile
python app.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

## How It Works

- **Existing films**: The `fetch_posters.py` script searches TMDB for each film by title and year, then saves the poster URL
- **New films**: When you add a film through the UI, the backend automatically fetches its poster
- **Posters are cached**: Once fetched, poster URLs are stored in your database, so no repeated API calls needed

## Troubleshooting

**"TMDB_API_KEY not set" error:**
- Make sure you've exported the environment variable in the same terminal window
- Check that you've reloaded your shell profile if you added it there

**"No poster found" for some films:**
- Some obscure films may not have posters in TMDB
- Try searching manually on themoviedb.org to verify
- The film may be listed under a different title

**Rate limiting:**
- TMDB allows 40 requests per 10 seconds
- The script automatically paces requests at 4 per second
- If you see errors, wait a minute and try again

## API Limits

TMDB's free tier includes:
- **40 requests per 10 seconds**
- **Unlimited total requests per day**
- This is more than enough for personal use!

Enjoy your film collection with beautiful posters! 🎬
