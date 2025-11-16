# Film Tracker Deployment Instructions

## Architecture
- **Frontend**: Deployed to Vercel (static React app)
- **Backend**: Deployed to Railway (Flask API with SQLite)

## Step 1: Deploy Backend to Railway

1. Go to [railway.app](https://railway.app) and sign in with GitHub
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your `film-tracker` repository
4. Railway will auto-detect the configuration from `nixpacks.toml`
5. Add environment variable:
   - Key: `TMDB_API_KEY`
   - Value: `344237d3195825baa6555d87e38bef5f`
6. Wait for deployment to complete
7. **IMPORTANT**: Copy your Railway backend URL (e.g., `https://your-app.railway.app`)

## Step 2: Deploy Frontend to Vercel

1. Go to [vercel.com](https://vercel.com) and sign in with GitHub
2. Click "Add New..." → "Project"
3. Import your `film-tracker` repository
4. Vercel will auto-detect the configuration from `vercel.json`
5. **IMPORTANT**: Add environment variable:
   - Key: `VITE_API_URL`
   - Value: `https://your-app.railway.app/api` (your Railway URL from Step 1 + `/api`)
6. Click "Deploy"
7. Wait for deployment to complete

## Step 3: Test Your Deployment

1. Visit your Vercel URL
2. The app should load and display your films
3. Test adding/editing/deleting films
4. Check the analytics tab

## Troubleshooting

### Frontend shows "Failed to fetch"
- Check that `VITE_API_URL` in Vercel is set correctly
- Make sure it ends with `/api` (e.g., `https://your-app.railway.app/api`)
- Verify Railway backend is running

### Backend errors on Railway
- Check Railway logs for errors
- Verify `backend/films.db` exists in your repository
- Make sure `TMDB_API_KEY` environment variable is set

### Films not showing
- Verify `backend/films.db` is committed to git and pushed
- Check Railway logs to see if database is being found

## Updating Your App

After making changes:
```bash
git add .
git commit -m "Your changes"
git push
```

Both Vercel and Railway will automatically redeploy!

## Important Files

- `vercel.json` - Vercel configuration (frontend only)
- `nixpacks.toml` - Railway configuration (backend only)
- `railway.json` - Railway metadata
- `backend/requirements.txt` - Python dependencies
- `backend/films.db` - Your film database (must be committed)
