# Railway Deployment Guide

## Why Railway?

Railway offers better memory management and easier configuration than Render's free tier:
- **Better Memory**: 8GB RAM on free trial ($5 credit)
- **Faster Deployments**: Better build caching
- **Simpler Configuration**: Auto-detects settings
- **MongoDB Support**: Easy integration with MongoDB Atlas

---

## Deployment Steps

### 1. Create Railway Account
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. You get $5 free credit (no credit card required initially)

### 2. Create New Project
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose `Ashish6312/hair-scalp-detector`
4. Railway will auto-detect it's a Python app

### 3. Configure Environment Variables

In Railway dashboard, add these variables:

```
SECRET_KEY=your-secret-key-here
DJANGO_SETTINGS_MODULE=minor.settings_production
MONGODB_URI=mongodb+srv://ashishsharma120512_db_user:g853JPKKNd5g4QOz@cluster0.sohqiaa.mongodb.net/?appName=Cluster0
MONGODB_NAME=hairscalp_db
ALLOWED_HOSTS=*.railway.app
```

### 4. Configure MongoDB Atlas Network Access

1. Go to [MongoDB Atlas](https://cloud.mongodb.com)
2. Navigate to **Network Access**
3. Click **Add IP Address**
4. Select **"Allow Access from Anywhere"** (0.0.0.0/0)
5. Click **Confirm**

### 5. Deploy

Railway will automatically:
- Detect Python 3.11
- Install dependencies from requirements.txt
- Run build.sh (migrations, static files)
- Start gunicorn with 2 workers
- Assign a public URL

---

## Configuration Details

### Workers & Memory
- **Workers**: 2 (Railway has more RAM)
- **Threads**: 2 per worker
- **Timeout**: 120 seconds
- **Max Requests**: 1000 (worker recycling)

### Database
- **Production**: MongoDB Atlas
- **Local**: SQLite (automatic fallback)

### Static Files
- Served via WhiteNoise
- Automatically collected during build

---

## Railway vs Render

| Feature | Railway | Render Free |
|---------|---------|-------------|
| RAM | 8GB | 512MB |
| Workers | 2-4 | 1 (max) |
| Cold Start | Faster | 50+ seconds |
| Build Time | Faster | Slower |
| Free Credit | $5 | Unlimited (with limits) |
| MongoDB | ✓ Works | ✗ Memory issues |

---

## Monitoring

### Check Deployment Status
1. Go to Railway dashboard
2. Click on your service
3. View "Deployments" tab
4. Check logs for:
   - ✓ `Booting worker with pid: xxx`
   - ✓ `Listening at: http://0.0.0.0:xxxx`
   - ✓ No timeout errors

### View Logs
```bash
# Install Railway CLI (optional)
npm install -g @railway/cli

# Login
railway login

# View logs
railway logs
```

---

## Custom Domain (Optional)

1. Go to Railway dashboard → Settings
2. Click "Generate Domain"
3. Or add your custom domain

---

## Cost Estimate

Railway charges based on usage:
- **Free Trial**: $5 credit (lasts ~1-2 months for small apps)
- **After Trial**: ~$5-10/month for this app
- **Pay as you go**: Only pay for what you use

---

## Troubleshooting

### Build Fails
- Check build logs in Railway dashboard
- Verify requirements.txt is correct
- Ensure build.sh has execute permissions

### Worker Timeout
- Increase timeout in railway.toml
- Reduce number of workers
- Check memory usage

### MongoDB Connection Error
- Verify MONGODB_URI is correct
- Check MongoDB Atlas network access (0.0.0.0/0)
- Verify database user credentials

### Static Files Not Loading
- Check ALLOWED_HOSTS includes Railway domain
- Verify WhiteNoise is in MIDDLEWARE
- Run collectstatic manually if needed

---

## Migration from Render

Your data on Render (SQLite) won't automatically transfer. You'll need to:

1. **Export data from Render** (if any):
   ```bash
   python manage.py dumpdata > data.json
   ```

2. **Import to Railway**:
   ```bash
   python manage.py loaddata data.json
   ```

Or start fresh with MongoDB Atlas (recommended).

---

## Next Steps After Deployment

1. **Create Superuser**:
   ```bash
   # In Railway CLI or dashboard shell
   python manage.py createsuperuser
   ```

2. **Test Your App**:
   - Visit your Railway URL
   - Test image upload
   - Check predictions work

3. **Monitor Usage**:
   - Check Railway dashboard for memory/CPU usage
   - Monitor MongoDB Atlas connections
   - Watch for any errors in logs

---

## Your app is ready for Railway! 🚀

Railway will handle the PyTorch model + MongoDB much better than Render's free tier.
