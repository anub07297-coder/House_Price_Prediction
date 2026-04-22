# Deploying to Render

This guide walks you through deploying the House Price Prediction application (API + Dashboard) to Render.

## Architecture

- **API Backend** (FastAPI): `https://housetoupredictapi.onrender.com`
- **Dashboard** (Streamlit): `https://housepricepredictor.onrender.com`

Both services are defined in `render.yaml` and automatically deploy together.

## Prerequisites

1. **GitHub Account** - Push your code to a GitHub repository
2. **Render Account** - Free account at https://render.com
3. **Git** - To push changes

## Step 1: Push Code to GitHub

```bash
# Initialize git (if not already done)
git init
git add .
git commit -m "Initial commit with Render config"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/House_Price_Prediction.git
git push -u origin main
```

## Step 2: Connect GitHub to Render

1. Go to https://dashboard.render.com
2. Click **"New"** → **"Blueprint"**
3. Select **"Connect a repository"**
4. Authorize GitHub and select your `House_Price_Prediction` repository
5. Click **"Connect"**

## Step 3: Review and Deploy

1. Render will detect `render.yaml` automatically
2. Review the services:
   - **house-price-api**: FastAPI backend
   - **house-price-dashboard**: Streamlit dashboard
3. Click **"Deploy"** to start the deployment process

The deployment will take 10-15 minutes:
- Dependencies are installed
- Training data is bootstrapped
- Model is trained
- Services are started

## Step 4: Access Your Application

Once deployed, you'll have:

- **API Dashboard**: `https://housetoupredictapi.onrender.com/docs` (Swagger UI)
- **Application Dashboard**: `https://housepricepredictor.onrender.com`

## Configuration

### Environment Variables

All critical variables are configured in `render.yaml`:

| Service | Variable | Value |
|---------|----------|-------|
| API | `APP_ENV` | `production` |
| API | `ENABLE_MOCK_PREDICTOR` | `true` |
| API | `GEOCODING_PROVIDER` | `free-fallback` |
| API | `PROPERTY_DATA_PROVIDER` | `free-fallback` |
| Dashboard | `API_BASE_URL` | `https://housetoupredictapi.onrender.com` |

The dashboard automatically reads `API_BASE_URL` from the environment and displays the deployment status in the sidebar.

## Updating Your Deployment

Push changes to GitHub, and Render will automatically redeploy:

```bash
git add .
git commit -m "Update feature X"
git push origin main
```

Render will:
1. Detect the push
2. Rebuild both services
3. Deploy the updated version (usually 3-5 minutes)

## Monitoring

1. Go to https://dashboard.render.com
2. Click on your service (API or Dashboard)
3. View **Logs** tab for real-time output
4. View **Deploys** tab for deployment history
5. View **Monitoring** tab for performance metrics

## Troubleshooting

### API Service Not Starting

Check the logs in the Render dashboard:
- Look for model training errors
- Verify database initialization succeeded
- Ensure all dependencies installed correctly

**Fix**: Update `buildCommand` in `render.yaml` if needed.

### Dashboard Can't Connect to API

1. Verify `API_BASE_URL` environment variable is set correctly
2. Check API service is running (Green status in Render dashboard)
3. Look for CORS or network errors in browser console

**Fix**: In dashboard, manually update the API URL field in the sidebar.

### Slow Cold Starts

- Render's free tier spins down after 15 minutes of inactivity
- First request after idle period will take 30-60 seconds
- Upgrade to Render's paid tier for Always-On services

## Database Persistence

Currently using SQLite stored in the service's ephemeral filesystem. For production:

1. **Recommended**: Use Render's PostgreSQL service
2. Update `DATABASE_URL` in `render.yaml` to PostgreSQL connection string
3. Update `requirements.txt` to include `psycopg2-binary`

```yaml
# Example PostgreSQL integration (not yet enabled)
- type: pserv  # PostgreSQL service
  name: house-price-db
  ipAllowList: []
  plan: free
  postgresVersion: 15
```

## Domain Names

Update custom domains in `render.yaml`:

```yaml
domains:
  - api.yourdomain.com    # Change from housetoupredictapi.onrender.com
  - dashboard.yourdomain.com  # Change from housepricepredictor.onrender.com
```

Then configure DNS settings with your domain registrar.

## Cost

**Free Tier** (Render's free plan):
- Services spin down after 15 minutes of inactivity
- Limited build time per month
- Suitable for development/demo

**Paid Tier**:
- Always-on services
- Unlimited build time
- Better performance

## Support

For Render-specific issues:
- Documentation: https://render.com/docs
- Status page: https://status.render.com
- Support: support@render.com

For application-specific issues:
- Check API logs: `housetoupredictapi.onrender.com`
- Check dashboard logs: `housepricepredictor.onrender.com`
- Run locally first: `streamlit run dashboard.py` + `python scripts/smoke_api.py`
