# Render Deployment Quick Start

## 🚀 Deploy in 3 Steps

### 1. Push to GitHub
```bash
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

### 2. Go to Render Dashboard
Visit https://dashboard.render.com and click **"New"** → **"Blueprint"**

### 3. Select Your Repository
- Connect GitHub account
- Select `House_Price_Prediction` repository
- Click **"Deploy"**

## ✅ That's It!

Render automatically:
- ✅ Installs dependencies  
- ✅ Trains the model
- ✅ Deploys API at: **https://housetoupredictapi.onrender.com**
- ✅ Deploys Dashboard at: **https://housepricepredictor.onrender.com**

## 📝 What Changed

| File | Purpose |
|------|---------|
| `render.yaml` | ⚙️ Defines both services & environment variables |
| `.streamlit/config.toml` | 🎨 Streamlit appearance & server settings |
| `dashboard.py` | 📡 Updated to read API URL from environment variable |
| `RENDER_DEPLOYMENT.md` | 📖 Full deployment guide (you are here!) |

## 🔗 API URLs

After deployment, you can:

- **View API Docs**: https://housetoupredictapi.onrender.com/docs
- **Access Dashboard**: https://housepricepredictor.onrender.com
- **Make API Calls**: 
  ```bash
  curl https://housetoupredictapi.onrender.com/v1/health
  ```

## 🛠️ Updating Your App

Push changes → Render auto-deploys (3-5 minutes)

```bash
git add .
git commit -m "Update something"
git push origin main
```

## 📊 Monitor Deployments

1. Go to https://dashboard.render.com
2. Click service name (house-price-api or house-price-dashboard)
3. View **Logs** and **Monitoring** tabs

## ⚠️ Important Notes

- **First deployment takes 10-15 minutes** (model training included)
- **Free tier services sleep after 15 min inactivity** (first request wakes them up)
- **Dashboard auto-connects to API** via `API_BASE_URL` environment variable
- **Hard drive limited** - SQLite database in ephemeral storage (ok for demo)

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| API not starting | Check logs for model training errors |
| Dashboard won't load | Verify `API_BASE_URL` env var is set |
| Slow first request | Free tier services sleep - normal behavior |
| Need always-on? | Upgrade to Render's paid tier |

For more details: See [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md)
