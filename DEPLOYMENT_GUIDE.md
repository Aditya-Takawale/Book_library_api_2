# Railway Deployment Guide

## 🚆 Deploy to Railway (Recommended)

Railway is perfect for your full-stack app because it provides:
- ✅ **Free MySQL database**
- ✅ **Automatic FastAPI detection** 
- ✅ **React frontend hosting**
- ✅ **GitHub integration**
- ✅ **Environment variables management**
- ✅ **Auto-deployments on git push**

### Quick Deploy Steps:

#### 1. Prepare for Deployment
```bash
# Run the preparation script
chmod +x deploy-railway.sh
./deploy-railway.sh
```

#### 2. Push to GitHub
```bash
git add .
git commit -m "Add Railway deployment config"
git push origin main
```

#### 3. Deploy on Railway
1. Go to [railway.app](https://railway.app)
2. Sign in with GitHub
3. Click **"New Project"** → **"Deploy from GitHub repo"**
4. Select your `Book_library_api_2` repository
5. Railway auto-detects your FastAPI backend

#### 4. Add MySQL Database
1. In your Railway project dashboard
2. Click **"New"** → **"Database"** → **"MySQL"**
3. Copy the `DATABASE_URL` connection string

#### 5. Configure Environment Variables
Go to your backend service → **"Variables"** tab:
```env
DATABASE_URL=mysql+pymysql://root:password@mysql.railway.internal:3306/railway
SECRET_KEY=IIXjU0qJlMMhoMENVEy6V_y3I4UQdjqamVK-XIeKjtY
LOG_LEVEL=INFO
UPLOAD_DIR=/tmp/uploads
```

#### 6. Deploy Frontend
1. Click **"New"** → **"GitHub Repo"** → **"Deploy from GitHub repo"**
2. Select same repository
3. Set **"Root Directory"** to `frontend`
4. Railway auto-detects React app

#### 7. Update CORS Settings
After deployment, update your backend environment with frontend URL:
```env
CORS_ORIGINS=https://your-frontend-railway.app,https://your-backend-railway.app
```

---

## 🌟 Alternative: Render + PlanetScale

### Backend on Render
1. Go to [render.com](https://render.com)
2. Connect GitHub → Select repository
3. Choose **"Web Service"**
4. Set build command: `cd backend && pip install -r requirements.txt`
5. Set start command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Database on PlanetScale
1. Go to [planetscale.com](https://planetscale.com)
2. Create free database (1GB limit)
3. Copy connection string to Render environment variables

### Frontend on Render
1. Add another service from same repo
2. Choose **"Static Site"**
3. Set build command: `cd frontend && npm install && npm run build`
4. Set publish directory: `frontend/build`

---

## 🔥 Alternative: Vercel + Railway

### Frontend on Vercel (Lightning Fast)
1. Go to [vercel.com](https://vercel.com)
2. Import your GitHub repository
3. Set **"Root Directory"** to `frontend`
4. Deploy automatically

### Backend on Railway
1. Deploy backend only on Railway
2. Add MySQL database
3. Update frontend API URL to point to Railway backend

---

## 💰 **Cost Breakdown**

| Platform | Free Tier Limits | Cost After |
|----------|------------------|------------|
| **Railway** | $5 credit/month | $0.01/minute runtime |
| **Render** | 750 hours/month | $7/month per service |
| **Vercel** | Unlimited frontend | $20/month for backend |
| **PlanetScale** | 1GB database | $29/month |

**Recommendation**: Start with **Railway** - it's the most cost-effective for your full-stack app!

---

## 🚀 **Production URLs After Deployment**

After successful deployment, you'll have:
- **Frontend**: `https://your-app-frontend.railway.app`
- **Backend API**: `https://your-app-backend.railway.app`
- **API Docs**: `https://your-app-backend.railway.app/docs`
- **Database**: Managed MySQL on Railway

## 🔧 **Zero Code Changes Required**

Your project is already configured for deployment! The preparation script creates:
- ✅ `Procfile` for Railway
- ✅ `railway.json` for configuration
- ✅ Environment variables template
- ✅ Requirements.txt update

**Just run the script and follow the steps - your app will be live in 10 minutes!** 🎉
