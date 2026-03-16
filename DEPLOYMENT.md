# Hubifyy Deployment Guide

This guide explains how to deploy Hubifyy to Vercel and other platforms.

## Project Structure for Vercel

```
Hubifyy/
├── api/
│   └── index.py              # ← Vercel entry point
├── app/
│   ├── core/
│   ├── db/
│   ├── routers/
│   ├── static/               # ← CSS, JS, images
│   ├── templates/            # ← Jinja2 HTML
│   ├── schemas.py
│   └── __init__.py
├── main.py                   # ← FastAPI app definition
├── requirements.txt          # ← Production dependencies
├── requirements-dev.txt      # ← Development dependencies
├── vercel.json              # ← Vercel configuration
├── .vercelignore            # ← Files to ignore in deployment
└── README.md
```

## Local Development

### Setup

```bash
# Clone repository
git clone https://github.com/parvgarg05/Hubifyy.git
cd Hubifyy

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dev dependencies (includes uvicorn for local server)
pip install -r requirements-dev.txt
```

### Running Locally

```bash
# Option 1: Using Uvicorn directly (development with hot reload)
uvicorn main:app --host 0.0.0.0 --port 3000 --reload

# Option 2: Using Python directly
python main.py
```

Then open http://localhost:3000

### Using SQLite Locally

The `.env` file is configured to use SQLite locally, which works great for development:

```env
DATABASE_URL=sqlite:///./college_hub.db
```

This creates a `.db` file in your project directory automatically.

## Production Deployment on Vercel

### Prerequisites

1. **GitHub Account** - Code is pushed to GitHub
2. **Vercel Account** - Free account at https://vercel.com
3. **Environment Variables** - Database connection string

### Step 1: Prepare Your Code

All Vercel-specific files are already in place:
- ✅ `/api/index.py` - Entry point
- ✅ `vercel.json` - Configuration
- ✅ `.vercelignore` - Ignore list
- ✅ `requirements.txt` - Production dependencies

### Step 2: Set Up Database on Neon

1. Go to https://neon.tech (free tier available)
2. Create a new project
3. Copy your connection string: `postgresql://user:password@host/dbname?sslmode=require`

### Step 3: Deploy to Vercel

**Option A: Using Vercel CLI**

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy
vercel --prod

# Add environment variable
vercel env add DATABASE_URL
# Paste your Neon connection string

# Redeploy to apply environment variables
vercel --prod
```

**Option B: Using Vercel Dashboard**

1. Go to https://vercel.com/dashboard
2. Click "Add New" → "Project"
3. Import your GitHub repository
4. Select project and click "Import"
5. Under "Environment Variables", add:
   - `DATABASE_URL` = Your Neon PostgreSQL connection string
6. Click "Deploy"

### Step 4: Verify Deployment

After deployment completes:

```bash
# Your app will be live at:
https://hubifyy.vercel.app  # (or your custom domain)

# Check API documentation:
https://hubifyy.vercel.app/docs

# Check ReDoc:
https://hubifyy.vercel.app/redoc
```

## Database Configuration

### For Local Development (SQLite)

```env
DATABASE_URL=sqlite:///./college_hub.db
```

✅ No setup needed, creates `.db` file automatically  
✅ Great for local testing  
❌ Not suitable for production (file-based, limited concurrency)

### For Production on Vercel (PostgreSQL with Neon)

```env
DATABASE_URL=postgresql://neondb_owner:YOUR_PASSWORD@ep-blue-frost-ane7wg6c-pooler.c-6.us-east-1.aws.neon.tech/neondb?sslmode=require
```

✅ Serverless PostgreSQL  
✅ Auto-scaling, reliable  
✅ Vercel-optimized  

### Switching Database Locally for Testing

To test PostgreSQL configuration locally:

1. Update `.env`:
```env
DATABASE_URL=postgresql://user:password@your-db-host/dbname
```

2. Install PostgreSQL driver (already in requirements.txt):
```bash
pip install psycopg2-binary
```

3. Run locally:
```bash
uvicorn main:app --reload
```

## Troubleshooting

### Error: `FUNCTION_INVOCATION_FAILED`

**Solution**: Ensure all files are committed to GitHub. Vercel deploys from Git, not your local file system.

```bash
git add .
git commit -m "Vercel deployment files"
git push
```

### Error: `500: INTERNAL_SERVER_ERROR`

**Possible causes**:
1. Missing `DATABASE_URL` environment variable → Add to Vercel dashboard
2. Database credentials incorrect → Test connection string on Neon
3. Routes not properly defined → Check `/api/index.py` imports correctly

**Check Vercel logs**:
- Go to Vercel Dashboard → Your Project → Deployments
- Click on the failed deployment
- View the build/function logs

### Static Files Not Loading

Vercel automatically handles static files. If they're not loading:

1. Verify `/app/static/` directory exists in git
2. Check `vercel.json` routes configuration
3. Clear Vercel cache and redeploy

### Template Not Found Error

The `/app/templates/` directory must contain files:
- Ensure files exist: `app/templates/index.html`, etc.
- Commit templates directory to GitHub

## Performance Optimization

### Cold Start Optimization

- Vercel serverless functions have cold start times
- Keep `/api/index.py` lightweight
- Move heavy initialization to startup event in main.py

### Database Connection Pooling

- PostgreSQL connection pooling configured in `database.py`
- Automatically manages connection lifecycle
- Vercel functions are stateless, connections expire after use

### Caching Headers

Add cache headers for static files in production:

```python
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app.mount("/static", StaticFiles(directory="app/static"), name="static")
```

## Monitoring & Logs

### View Vercel Logs

```bash
# Using Vercel CLI
vercel logs --follow

# Or through dashboard:
# https://vercel.com/dashboard → Project → Activity
```

### Monitor PostgreSQL Database

On Neon Dashboard:
- View query history
- Check database size
- Monitor connections

## Custom Domain

In Vercel Dashboard:
1. Go to Project Settings → Domains
2. Add your custom domain
3. Follow DNS configuration instructions

## Rollback & Redeployment

If deployment has issues:

```bash
# Redeploy previous working version
vercel --prod --force

# Or through dashboard:
# Deployments → Select previous deployment → Click "Promote to Production"
```

## Local Development with Production Database

For testing production setup locally:

```bash
# Update .env temporarily
DATABASE_URL=postgresql://...  # Neon string

# Run locally
uvicorn main:app --reload

# Test your app at http://localhost:3000
```

## Useful Files Reference

| File | Purpose |
|------|---------|
| `api/index.py` | Vercel entry point (don't modify unless needed) |
| `vercel.json` | Vercel build config (routes, env vars, functions) |
| `.vercelignore` | Files Vercel should ignore |
| `requirements.txt` | Production dependencies |
| `requirements-dev.txt` | Development dependencies |
| `main.py` | FastAPI app definition |
| `.env` | Local environment variables (not committed) |

## Questions?

- Check Vercel docs: https://vercel.com/docs
- Check FastAPI docs: https://fastapi.tiangolo.com/
- Check Neon docs: https://neon.tech/docs/
