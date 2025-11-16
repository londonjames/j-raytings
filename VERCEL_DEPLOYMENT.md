# Deploy to Vercel - Complete Guide

Simple step-by-step guide to deploy your entire film tracker to Vercel (frontend + backend together).

---

## STEP 1: Push to GitHub (5 minutes)

### 1.1 Create GitHub Repository

1. Go to https://github.com
2. Click **"+"** button (top right) → **"New repository"**
3. Repository name: **film-tracker**
4. Make it **Public** (required for free deployment)
5. **DON'T** check any boxes (no README, no .gitignore)
6. Click **"Create repository"**

### 1.2 Push Your Code

After creating the repo, GitHub shows commands. Copy the section under **"…or push an existing repository from the command line"**.

It will look like this (but with YOUR username):

```bash
git remote add origin https://github.com/YOUR-USERNAME/film-tracker.git
git branch -M main
git push -u origin main
```

**Open Terminal and run those commands** (paste them in). Enter GitHub credentials if prompted.

---

## STEP 2: Deploy to Vercel (10 minutes)

### 2.1 Sign Up for Vercel

1. Go to https://vercel.com
2. Click **"Sign Up"**
3. Choose **"Continue with GitHub"**
4. Click **"Authorize Vercel"** when prompted

### 2.2 Import Your Project

1. On Vercel dashboard, click **"Add New..."** → **"Project"**
2. Find your **"film-tracker"** repository in the list
3. Click **"Import"**

### 2.3 Configure Project Settings

Vercel will auto-detect most settings, but verify these:

**Build & Development Settings:**
- **Framework Preset:** Should auto-detect as "Other" or "Vite" - this is fine!
- **Root Directory:** Leave as `./` (the default)
- **Build Command:** `cd frontend && npm install && npm run build`
- **Output Directory:** `frontend/dist`
- **Install Command:** `npm install`

You can leave these as default or enter manually if needed.

### 2.4 Deploy!

1. Click **"Deploy"** button at the bottom
2. **First deployment:** Wait 2-4 minutes while Vercel builds your app from scratch
3. **Subsequent deployments:** Usually only 5-30 seconds! Vercel uses caching and incremental builds
4. You'll see logs streaming - don't worry if you see warnings
5. When done, you'll see confetti! 🎉
6. Click **"Visit"** to see your live site

---

## STEP 3: Connect Your Domain (Optional, 10 minutes)

### 3.1 Add Domain in Vercel

1. Go to your project → **Settings** → **"Domains"**
2. Enter your domain name (the one you bought)
3. Click **"Add"**
4. Vercel will show you DNS records

### 3.2 Update DNS at Your Domain Registrar

1. Log in to where you bought your domain (GoDaddy, Namecheap, etc.)
2. Find **"DNS Settings"** or **"Manage DNS"**
3. Add the records Vercel showed you:
   - Usually an **A record** pointing to Vercel's IP
   - And a **CNAME record** for www
4. **Save** changes
5. Wait 10-60 minutes for DNS to update

Done! Your domain will point to your Vercel site.

---

## TROUBLESHOOTING

### "Build Failed" Error

**Check the build logs** - they'll show what went wrong. Common issues:

1. **Missing dependencies:** Make sure `frontend/package.json` has all packages
2. **Wrong build command:** Should be `cd frontend && npm install && npm run build`
3. **Database not found:** Make sure `backend/films.db` is committed to git

### Films Not Loading

1. Open browser DevTools (F12) → Console tab
2. Look for errors
3. Check Network tab → see if `/api/films` request is failing
4. Make sure the `api/` folder was included in your git commit

### "Application Error" or 500 Error

1. **To see the actual Python error:**
   - Go to Vercel dashboard → Your project → **Deployments** tab
   - Click on the failed deployment
   - Click **"Runtime Logs"** tab (NOT "Build Logs")
   - Look for entries with red X icons
   - **Click on a red error entry** to expand it
   - The full Python traceback should be visible in the expanded view
   - Copy the complete error message

2. **Alternative: Check Function Logs**
   - Go to **Logs** tab (in project, not deployment)
   - Filter by "Error" or "Fatal"
   - Click on error entries to see full details

3. Make sure `requirements.txt` is in the root directory AND in the `api/` directory
4. Verify `api/index.py` exists and exports a `handler` function
5. Check that Python runtime is configured in `vercel.json`

---

## UPDATING YOUR SITE

After deployment, any time you want to update your site:

```bash
# Make your changes to the code
git add .
git commit -m "Describe your changes"
git push
```

**That's it!** Vercel will automatically detect the push and redeploy. 
- **First deployment:** Takes 2-4 minutes
- **Subsequent deployments:** Usually 5-30 seconds (thanks to Vercel's smart caching!)

---

## IMPORTANT NOTES

✅ **What's Included:**
- Frontend (React app)
- Backend (API as serverless functions)
- Database (SQLite file)

⚠️ **Limitations:**
- **Database is read-only in production** - You can't add/edit/delete films through the live site
- Database updates must be done locally, then committed and pushed to GitHub
- Free tier has bandwidth limits (but plenty for personal use)

💡 **To Update Films:**
1. Make changes to your local database
2. Commit the updated `backend/films.db` file
3. Push to GitHub
4. Vercel will redeploy with updated data

---

## YOUR SITE IS LIVE! 🎬

Once deployed, you can:
- Share the URL with anyone
- Access it from any device
- Connect your custom domain

Enjoy your film tracker!
