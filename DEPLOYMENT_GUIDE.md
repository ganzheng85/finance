# Web App Deployment Guide

## Overview

Deploy your Stock Analysis Web App so others can access it online. This guide covers multiple deployment options from easiest (free tier) to advanced (full control).

---

## Quick Comparison

| Platform | Difficulty | Cost | Best For |
|----------|-----------|------|----------|
| **Render** | ⭐ Easy | Free tier available | Quickest deployment |
| **Railway** | ⭐ Easy | Free $5 credit/month | Modern, simple |
| **Heroku** | ⭐⭐ Medium | $7/month minimum | Established platform |
| **Google Cloud Run** | ⭐⭐⭐ Advanced | Pay per use (~$5-20/mo) | Scalable, professional |
| **DigitalOcean** | ⭐⭐⭐ Advanced | $6/month | Full control |

---

## Option 1: Render.com (RECOMMENDED - Easiest)

**Pros:**
- ✅ Free tier (750 hours/month)
- ✅ Automatic deployments from GitHub
- ✅ SSL certificates included
- ✅ Zero configuration needed

**Cons:**
- ⚠️ Spins down after 15 min inactivity (takes 30s to wake up)
- ⚠️ Limited to 512MB RAM on free tier

### Step-by-Step Deployment on Render

#### 1. Prepare Your Project

Create these files in your project root:

**`requirements.txt`** (if not exists):
```bash
cd c:\Users\ZJGan\Projects\finance
pip freeze > requirements.txt
```

**`render.yaml`** (create new file):
```yaml
services:
  - type: web
    name: stock-analysis-app
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn --bind 0.0.0.0:$PORT stock_analysis_app.app:app
    envVars:
      - key: PYTHON_VERSION
        value: 3.13
      - key: PORT
        value: 5000
```

**Update `requirements.txt`** to include `gunicorn`:
```bash
echo "gunicorn==21.2.0" >> requirements.txt
```

**Update `stock_analysis_app/app.py`** - Change the last line:
```python
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
```

#### 2. Push to GitHub

```bash
cd c:\Users\ZJGan\Projects\finance

# Initialize git (if not already)
git init
git add .
git commit -m "Prepare for deployment"

# Create GitHub repo and push
git remote add origin https://github.com/YOUR_USERNAME/stock-analysis.git
git branch -M main
git push -u origin main
```

#### 3. Deploy on Render

1. Go to https://render.com
2. Sign up with GitHub
3. Click **"New +"** → **"Web Service"**
4. Connect your GitHub repository
5. Configure:
   - **Name:** stock-analysis-app
   - **Region:** Choose closest to you
   - **Branch:** main
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn --bind 0.0.0.0:$PORT stock_analysis_app.app:app`
   - **Instance Type:** Free
6. Click **"Create Web Service"**

**Your app will be live at:** `https://stock-analysis-app.onrender.com`

---

## Option 2: Railway.app (Modern & Clean)

**Pros:**
- ✅ $5 free credit per month
- ✅ Doesn't spin down
- ✅ Very fast deployments
- ✅ Clean UI

**Cons:**
- ⚠️ Free credit may not last full month with heavy use

### Deployment on Railway

#### 1. Prepare Project

Same as Render (requirements.txt + gunicorn)

**Create `Procfile`:**
```
web: gunicorn --bind 0.0.0.0:$PORT stock_analysis_app.app:app
```

#### 2. Deploy

1. Go to https://railway.app
2. Sign up with GitHub
3. Click **"New Project"** → **"Deploy from GitHub repo"**
4. Select your repository
5. Railway auto-detects Python and deploys
6. Click **"Settings"** → **"Generate Domain"**

**Your app will be live at:** `https://your-app.up.railway.app`

---

## Option 3: Google Cloud Run (Professional)

**Pros:**
- ✅ Only pay for actual usage
- ✅ Auto-scales (0 to millions of users)
- ✅ Professional infrastructure
- ✅ Free tier: 2M requests/month

**Cons:**
- ⚠️ More complex setup
- ⚠️ Requires credit card

### Deployment on Google Cloud Run

#### 1. Install Google Cloud CLI

Download from: https://cloud.google.com/sdk/docs/install

#### 2. Create Dockerfile

**`Dockerfile`** (create in project root):
```dockerfile
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY . .

# Expose port
EXPOSE 8080

# Run app
CMD exec gunicorn --bind :8080 --workers 1 --threads 8 --timeout 0 stock_analysis_app.app:app
```

#### 3. Deploy

```bash
# Login to Google Cloud
gcloud auth login

# Set project (create one at console.cloud.google.com)
gcloud config set project YOUR_PROJECT_ID

# Build and deploy
gcloud run deploy stock-analysis \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 900
```

**Your app will be live at:** `https://stock-analysis-xxxxx-uc.a.run.app`

---

## Option 4: Heroku (Traditional)

**Note:** Heroku eliminated free tier in 2022. Minimum $7/month.

### Deployment on Heroku

#### 1. Install Heroku CLI

Download from: https://devcenter.heroku.com/articles/heroku-cli

#### 2. Prepare Project

**Create `Procfile`:**
```
web: gunicorn stock_analysis_app.app:app
```

**Create `runtime.txt`:**
```
python-3.13.0
```

#### 3. Deploy

```bash
# Login
heroku login

# Create app
heroku create your-stock-analysis-app

# Deploy
git push heroku main

# Open app
heroku open
```

**Your app will be live at:** `https://your-stock-analysis-app.herokuapp.com`

---

## Important Considerations

### 1. **Performance Optimization**

Your app fetches live data from Yahoo Finance, which can be slow. Consider:

**Add caching** to `stock_analysis_app/app.py`:
```python
from functools import lru_cache
from datetime import datetime, timedelta

# Cache sector data for 1 hour
_sector_cache = {}
_cache_time = None

@app.route('/api/sector/generate', methods=['POST'])
def generate_sector():
    global _sector_cache, _cache_time
    
    # Check cache
    if _cache_time and (datetime.now() - _cache_time) < timedelta(hours=1):
        return jsonify(_sector_cache)
    
    # Generate fresh data
    result = generate_sector_analysis()
    
    # Update cache
    _sector_cache = result
    _cache_time = datetime.now()
    
    return jsonify(result)
```

### 2. **Environment Variables**

Keep sensitive data out of code. Create `.env` file:

```bash
SECRET_KEY=your-secret-key-here
FLASK_ENV=production
```

Add to `.gitignore`:
```
.env
__pycache__/
*.pyc
*.pyo
reports/
analyses/
```

Update `app.py`:
```python
import os
from dotenv import load_dotenv

load_dotenv()

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key')
```

### 3. **Security Considerations**

**Add rate limiting** to prevent abuse:

```bash
pip install Flask-Limiter
```

Update `app.py`:
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)

@app.route('/api/sector/generate', methods=['POST'])
@limiter.limit("5 per hour")  # Max 5 sector analyses per hour
def generate_sector():
    ...
```

### 4. **Cost Management**

**Expected costs (for ~100 users/day):**

| Platform | Monthly Cost |
|----------|--------------|
| Render Free | $0 (with spin-down) |
| Railway | $5-10 |
| Google Cloud Run | $5-15 |
| Heroku | $7+ |
| DigitalOcean | $6+ |

**Tips to reduce costs:**
- ✅ Cache sector analysis results
- ✅ Limit API requests per user
- ✅ Use CDN for static files
- ✅ Compress responses

### 5. **Monitoring**

Add basic logging:

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/api/sector/generate', methods=['POST'])
def generate_sector():
    logger.info(f"Sector analysis requested from {request.remote_addr}")
    try:
        result = generate_sector_analysis()
        logger.info("Sector analysis completed successfully")
        return jsonify(result)
    except Exception as e:
        logger.error(f"Sector analysis failed: {str(e)}")
        return jsonify({'error': str(e)}), 500
```

---

## Recommended Setup for Your App

**Best option: Render.com (Free Tier)**

### Complete Deployment Checklist

- [ ] Install required packages
  ```bash
  pip install gunicorn python-dotenv Flask-Limiter Flask-Cors
  pip freeze > requirements.txt
  ```

- [ ] Create `render.yaml` (see above)

- [ ] Update `app.py` with:
  - [ ] Environment variable support
  - [ ] Rate limiting
  - [ ] Proper port binding
  - [ ] Production mode (`debug=False`)

- [ ] Create `.gitignore`:
  ```
  .env
  __pycache__/
  *.pyc
  reports/
  analyses/
  .vscode/
  ```

- [ ] Push to GitHub
  ```bash
  git add .
  git commit -m "Deploy to production"
  git push origin main
  ```

- [ ] Deploy on Render.com
  - Connect GitHub repo
  - Configure settings
  - Deploy!

- [ ] Test your live app

- [ ] Share URL: `https://your-app.onrender.com`

---

## Custom Domain (Optional)

After deployment, you can add your own domain:

1. **Buy domain** (e.g., from Namecheap, GoDaddy)
2. **In Render/Railway/etc:**
   - Go to Settings → Custom Domain
   - Add your domain: `www.yourapp.com`
3. **Update DNS** at your domain registrar:
   - Add CNAME record: `www` → `your-app.onrender.com`
4. **SSL certificate** auto-generated

---

## Next Steps

1. **Start with Render.com** (free, easiest)
2. **Add caching** to improve performance
3. **Monitor usage** for first few weeks
4. **Upgrade if needed** (Railway or Google Cloud Run)

---

## Troubleshooting

**App crashes on startup:**
- Check logs in platform dashboard
- Verify `requirements.txt` includes all packages
- Test locally first: `gunicorn stock_analysis_app.app:app`

**Slow sector analysis:**
- Add caching (see Performance section)
- Increase memory/CPU on platform
- Consider pre-computing daily and storing results

**Rate limit errors:**
- Yahoo Finance may block too many requests
- Add delays between API calls
- Cache results for 1 hour minimum

**Out of memory:**
- Reduce lookback days in analysis
- Clear old report files
- Upgrade to paid tier (1GB+ RAM)

---

## Summary

**Recommended Path:**

1. ✅ **Free Tier:** Start with Render.com
2. ✅ **Add caching:** 1-hour cache for sector data
3. ✅ **Monitor usage:** Check logs and performance
4. ✅ **Upgrade if needed:** Railway or Google Cloud Run for better performance

**Estimated Timeline:**
- Setup: 30 minutes
- First deployment: 15 minutes
- Testing: 30 minutes
- **Total: ~1.5 hours** to go live!

**Cost:** $0-10/month (depending on usage)

Good luck with your deployment! 🚀
