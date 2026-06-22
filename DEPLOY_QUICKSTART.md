# Quick Start: Deploy to Render.com (FREE)

**Estimated Time:** 20 minutes  
**Cost:** FREE

---

## Step 1: Install Gunicorn

```bash
cd c:\Users\ZJGan\Projects\finance
pip install gunicorn==21.2.0
```

✅ Already added to `requirements.txt`

---

## Step 2: Create GitHub Repository

### Option A: Using GitHub Desktop (Easiest)
1. Download GitHub Desktop: https://desktop.github.com
2. Open GitHub Desktop
3. File → Add Local Repository → Browse to `c:\Users\ZJGan\Projects\finance`
4. Click "Publish Repository"
5. Uncheck "Keep this code private" (or keep it private, up to you)
6. Click "Publish Repository"

### Option B: Using Git Command Line
```bash
cd c:\Users\ZJGan\Projects\finance

# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - Stock Analysis App"

# Create repo on GitHub.com first, then:
git remote add origin https://github.com/YOUR_USERNAME/stock-analysis.git
git branch -M main
git push -u origin main
```

---

## Step 3: Deploy on Render

1. **Go to:** https://render.com
2. **Sign Up** with your GitHub account
3. Click **"New +"** (top right) → **"Web Service"**
4. Click **"Connect GitHub"** and authorize Render
5. Find your `stock-analysis` repository and click **"Connect"**

### Configure Settings:

**Basic Settings:**
- **Name:** `stock-analysis-app` (or your preferred name)
- **Region:** `Oregon (US West)` (or closest to you)
- **Branch:** `main`
- **Root Directory:** (leave blank)

**Build & Deploy:**
- **Runtime:** `Python 3`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 300 stock_analysis_app.app:app`

**Plan:**
- **Instance Type:** `Free` (select the free tier)

**Advanced (optional):**
- **Auto-Deploy:** `Yes` (deploys automatically on git push)
- **Health Check Path:** `/api/health`

6. Click **"Create Web Service"**

---

## Step 4: Wait for Deployment

Render will:
1. Pull your code from GitHub
2. Install all dependencies (2-3 minutes)
3. Start your app (1 minute)
4. Assign you a URL

**Watch the logs** to see progress.

---

## Step 5: Access Your App! 🎉

Your app will be live at:
```
https://stock-analysis-app.onrender.com
```
(Replace `stock-analysis-app` with whatever you named it)

**Share this URL** with anyone - they can now use your app!

---

## Usage Notes

### ⏱️ Free Tier Limitations:
- **Spin Down:** App sleeps after 15 min of no activity
- **Wake Up:** Takes 30-60 seconds on first request
- **Uptime:** 750 hours/month (enough for moderate use)

### 🔄 Updates:
Whenever you push code to GitHub:
```bash
git add .
git commit -m "Updated sector analysis"
git push
```
Render **automatically redeploys** in ~3 minutes.

### 📊 Performance:
- Sector analysis takes 30-60 seconds (fetching 13 ETFs)
- Company analysis faster (1 ticker)
- First load after spin-down is slower

---

## Optional: Add Custom Domain

After deployment:

1. Buy domain (e.g., `mystockapp.com` from Namecheap)
2. In Render Dashboard → Settings → **Custom Domain**
3. Add your domain: `www.mystockapp.com`
4. Update your domain's DNS:
   - Type: `CNAME`
   - Name: `www`
   - Value: `stock-analysis-app.onrender.com`
5. SSL certificate auto-generated

---

## Troubleshooting

### App Won't Start
- Check **Logs** tab in Render dashboard
- Common issue: Missing package in `requirements.txt`
- Fix: Add package, git push

### Sector Analysis Times Out
- Increase timeout in start command: `--timeout 600` (10 min)
- Or add caching (see DEPLOYMENT_GUIDE.md)

### Out of Memory
- Free tier has 512MB RAM
- Reduce lookback days in analysis
- Or upgrade to $7/month tier (512MB → 2GB)

---

## Monitoring Your App

**Render Dashboard:**
- View logs: Real-time app output
- Metrics: Memory, CPU usage
- Events: Deployment history

**Check Health:**
```bash
curl https://your-app.onrender.com/api/health
```

Should return:
```json
{
  "status": "healthy",
  "timestamp": "..."
}
```

---

## Next Steps

✅ **Your app is live!**

Now you can:
1. Share the URL with friends
2. Add to your resume/portfolio
3. Monitor usage in Render dashboard
4. Upgrade if you need more performance

**Upgrade Options:**
- **Starter ($7/mo):** No spin-down, 512MB RAM
- **Standard ($25/mo):** 2GB RAM, better performance

---

## Cost Estimate

**Free Tier (Current):**
- Monthly: $0
- Best for: Personal use, demos, portfolio

**If you outgrow free tier:**
- Light usage (< 100 users/day): $7/mo (Starter plan)
- Medium usage (100-1000 users/day): $25/mo (Standard plan)
- Heavy usage: Consider Google Cloud Run (~$10-30/mo)

---

## Security Tips

1. **Never commit `.env` files** (already in .gitignore)
2. **Add rate limiting** if you get too much traffic
3. **Monitor logs** for suspicious activity
4. **Keep dependencies updated:** `pip list --outdated`

---

## Support

**Questions?**
- Render Docs: https://render.com/docs
- Render Community: https://community.render.com

**Your App Issues?**
- Check Render logs first
- See full deployment guide: `DEPLOYMENT_GUIDE.md`

---

**Congratulations! Your app is now online! 🚀**

Share it: `https://your-app.onrender.com`
