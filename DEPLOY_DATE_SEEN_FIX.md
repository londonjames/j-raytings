# How to Deploy the date_seen Fix - Beginner Guide

## What Does "Deploy" Mean?

**Deploying** means uploading your updated code to the cloud so your live website uses the new version. Think of it like updating an app on your phone - you make changes, then upload them so everyone sees the update.

## Step-by-Step Instructions

### Step 1: Open Terminal

1. On your Mac, press `Command + Space` to open Spotlight
2. Type "Terminal" and press Enter
3. A black window will open - this is where you'll type commands

### Step 2: Navigate to Your Project Folder

Type this command and press Enter:

```bash
cd /Users/jamesraybould/Documents/film-tracker
```

This tells Terminal to go to your project folder.

### Step 3: Check What Files Changed

Type this to see what files you've modified:

```bash
git status
```

You should see `backend/app.py` listed as modified (in red). This is the file we updated to add the `date_seen` column fix.

### Step 4: Save Your Changes to Git

Type these commands one at a time, pressing Enter after each:

```bash
git add backend/app.py
```

```bash
git commit -m "Add date_seen column auto-creation for PostgreSQL"
```

**What this does:**
- `git add` tells Git to track the changes to `app.py`
- `git commit` saves those changes with a message describing what you did

### Step 5: Push to GitHub

Type this command:

```bash
git push
```

**What this does:**
- Uploads your changes to GitHub
- Railway (your hosting service) will automatically detect the changes
- Railway will rebuild and redeploy your backend with the new code

### Step 6: Wait for Railway to Deploy

1. Go to https://railway.app in your web browser
2. Sign in if needed
3. Click on your project (probably called "film-tracker" or similar)
4. You'll see a deployment in progress - wait 2-5 minutes
5. When it says "Deployed" or "Active", you're done!

### Step 7: Verify It Worked

The updated `app.py` will automatically:
- Check if the `date_seen` column exists when the app starts
- Add it if it's missing
- This happens automatically - no manual steps needed!

## Troubleshooting

### If `git push` asks for a password:
- You might need to set up a GitHub Personal Access Token
- Or use GitHub Desktop app instead (easier for beginners)

### If Railway shows an error:
- Check the "Logs" tab in Railway
- Look for any red error messages
- The most common issue is a typo, but we've tested the code

### If you're not sure if it worked:
- The app will still work even if the column already exists
- The code just makes sure it exists - it won't break anything

## What Happens Next?

After Railway finishes deploying:
1. Your production database will automatically get the `date_seen` column (if missing)
2. Then you can run the sync script (Step 2) to populate the dates

## Need Help?

If you get stuck at any step, just tell me:
- What command you ran
- What error message you saw (if any)
- What step you're on

I'll help you fix it!

