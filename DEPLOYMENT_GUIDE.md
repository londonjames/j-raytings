# Film Tracker Deployment Guide

Complete step-by-step guide to deploy your film tracker to the cloud.

---

## OVERVIEW

Your app has two parts that need to be deployed separately:
1. **Backend** (Flask API + SQLite database) → Deploy to **Render** (free)
2. **Frontend** (React app) → Deploy to **Vercel** (free)

Total time: About 45 minutes

---

## PART 1: SET UP GIT & GITHUB (10 minutes)

### Step 1: Initialize Git Repository

Open Terminal and run these commands:

```bash
cd /Users/jamesraybould/Documents/film-tracker
git init
git add .
git commit -m "Initial commit - Film tracker app"
```

### Step 2: Create GitHub Repository

1. Go to https://github.com
2. Click the **"+"** button (top right) → **"New repository"**
3. Name it: `film-tracker`
4. Description: `My personal film ratings tracker`
5. Keep it **Public** (required for free deployment)
6. **DO NOT** check "Add a README" or ".gitignore" (we already have them)
7. Click **"Create repository"**

### Step 3: Push Code to GitHub

On the next page, GitHub will show commands. Copy the section under **"…or push an existing repository from the command line"**. It will look like:

```bash
git remote add origin https://github.com/YOUR-USERNAME/film-tracker.git
git branch -M main
git push -u origin main
```

Run those commands in your Terminal. Enter your GitHub credentials if prompted.

---

## PART 2: DEPLOY BACKEND TO RENDER (20 minutes)

### Step 1: Sign Up for Render

1. Go to https://render.com
2. Click **"Get Started for Free"**
3. Sign up with your GitHub account (easier for deployment)
4. Click **"Authorize Render"** when GitHub asks

### Step 2: Create New Web Service

1. On Render Dashboard, click **"New +"** → **"Web Service"**
2. Click **"Connect a repository"**
3. Find and select your **"film-tracker"** repository
4. Click **"Connect"**

### Step 3: Configure the Web Service

Fill in these settings:

- **Name:** `film-tracker-backend` (or any name you like)
- **Region:** Choose closest to you (e.g., Oregon USA)
- **Root Directory:** `backend`
- **Environment:** `Python 3`
- **Build Command:** `./build.sh`
- **Start Command:** `gunicorn app:app`
- **Instance Type:** Select **"Free"**

### Step 4: Add Environment Variable

Scroll down to **"Environment Variables"**:

1. Click **"Add Environment Variable"**
2. Key: `TMDB_API_KEY`
3. Value: `344237d3195825baa6555d87e38bef5f`
4. Click **"Add"**

### Step 5: Deploy!

1. Click **"Create Web Service"** at the bottom
2. Wait 3-5 minutes while Render builds and deploys your backend
3. You'll see logs streaming - wait for **"Your service is live"**
4. **SAVE THE URL!** It will look like: `https://film-tracker-backend-xxxx.onrender.com`

### Step 6: Test Your Backend

Open your backend URL in a browser and add `/api/films` to the end:
```
https://film-tracker-backend-xxxx.onrender.com/api/films
```

You should see JSON data with your films! If you see an error, check the Render logs.

---

## PART 3: DEPLOY FRONTEND TO VERCEL (15 minutes)

### Step 1: Update Frontend API URL

We need to tell the frontend where the deployed backend is.

**Option A: Create environment variable file**

Create a new file: `frontend/.env.production`

```
VITE_API_URL=https://your-backend-url.onrender.com
```

Replace `your-backend-url.onrender.com` with your actual Render URL from Part 2.

**Option B: I'll do this for you - just give me your Render backend URL**

### Step 2: Sign Up for Vercel

1. Go to https://vercel.com
2. Click **"Sign Up"**
3. Choose **"Continue with GitHub"**
4. Click **"Authorize Vercel"** when GitHub asks

### Step 3: Import Your Project

1. Click **"Add New..."** → **"Project"**
2. Find your **"film-tracker"** repository
3. Click **"Import"**

### Step 4: Configure the Project

- **Project Name:** `film-tracker` (or customize it)
- **Framework Preset:** Vercel should auto-detect **"Vite"**
- **Root Directory:** Click **"Edit"** and select **"frontend"**
- **Build Command:** Should auto-fill as `npm run build`
- **Output Directory:** Should auto-fill as `dist`

### Step 5: Add Environment Variable

1. Click **"Environment Variables"** (expand if collapsed)
2. Key: `VITE_API_URL`
3. Value: Your Render backend URL (e.g., `https://film-tracker-backend-xxxx.onrender.com`)
4. Click **"Add"**

### Step 6: Deploy!

1. Click **"Deploy"**
2. Wait 2-3 minutes while Vercel builds your frontend
3. When done, you'll see confetti and a **"Visit"** button
4. Click **"Visit"** to see your live site!

---

## PART 4: CONNECT YOUR CUSTOM DOMAIN (Optional, 5 minutes)

### On Vercel:

1. Go to your project Settings → **"Domains"**
2. Enter your domain name (the one you bought)
3. Click **"Add"**
4. Vercel will show you DNS records to add

### On Your Domain Registrar (where you bought the domain):

1. Log in to your domain provider (GoDaddy, Namecheap, etc.)
2. Find **"DNS Settings"** or **"Manage DNS"**
3. Add the records Vercel showed you (usually an A record and CNAME)
4. Save changes
5. Wait 10-60 minutes for DNS to propagate

---

## TROUBLESHOOTING

### Backend Issues:

**"Application failed to respond"**
- Check Render logs for errors
- Make sure `films.db` is in the `backend` folder
- Verify build command is `./build.sh`
- Verify start command is `gunicorn app:app`

**"No films showing"**
- Make sure `films.db` was committed to git
- Check that the database file isn't in .gitignore

### Frontend Issues:

**"Failed to fetch"** or API errors
- Check that VITE_API_URL is set correctly in Vercel
- Make sure it starts with `https://` and has no trailing slash
- Verify backend is working by visiting `/api/films` directly

**Blank page**
- Check Vercel deployment logs for build errors
- Make sure Root Directory is set to `frontend`
- Verify VITE_API_URL environment variable is set

---

## UPDATING YOUR APP AFTER DEPLOYMENT

### Making Changes:

1. Make your code changes locally
2. Test them with `npm run dev` (frontend) and `python app.py` (backend)
3. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Description of changes"
   git push
   ```
4. **Both Vercel and Render will automatically redeploy!**

That's it! Your changes will be live in a few minutes.

---

## IMPORTANT NOTES

- **Free tier limits:** Backend may sleep after 15 minutes of inactivity (first request after sleep takes ~30 seconds)
- **Database updates:** Any changes to `films.db` need to be committed and pushed to update the live site
- **Environment variables:** If you change API keys, update them in Render/Vercel settings

---

## NEXT STEPS

1. Share your live URL with friends!
2. Consider upgrading to paid tiers if you need faster performance
3. Set up a PostgreSQL database for production (instead of SQLite) if you plan to scale

Your film tracker is now live! 🎬
