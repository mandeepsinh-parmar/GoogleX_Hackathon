# 🚀 Google Cloud Run Deployment Guide

## Multi-Agent Industrial Geolocation Engine — GoogleX Hackathon × DeepStation

Follow these steps **in order** on the system where you want to deploy from.

---

## Step 1: Install Google Cloud CLI

### macOS
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

### Ubuntu / Debian
```bash
sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates gnupg curl
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg
echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee /etc/apt/sources.list.d/google-cloud-sdk.list
sudo apt-get update
sudo apt-get install -y google-cloud-cli
```

### Windows
Download installer from: https://cloud.google.com/sdk/docs/install
Run the `.exe` and follow the wizard. Then **open a new terminal**.

---

## Step 2: Clone the Repository

```bash
git clone https://github.com/mandeepsinh-parmar/GoogleX_Hackathon.git
cd GoogleX_Hackathon
```

---

## Step 3: Authenticate with Google Cloud

```bash
gcloud auth login
```

A browser window will open — sign in with your Google account.

---

## Step 4: Create or Select a Project

### Option A: Create a new project
```bash
gcloud projects create industrial-finder-2026 --name="Industrial Finder"
gcloud config set project industrial-finder-2026
```

### Option B: Use an existing project
```bash
gcloud config set project YOUR_PROJECT_ID
```

> 💡 Find your project ID at: https://console.cloud.google.com

---

## Step 5: Enable Billing

Cloud Run requires billing enabled (it has a generous free tier).

Go to: https://console.cloud.google.com/billing

Link a billing account to your project.

---

## Step 6: Enable Required APIs

```bash
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

---

## Step 7: Deploy to Cloud Run 🚀

Replace `YOUR_GEMINI_KEY` and `YOUR_MAPS_KEY` with your actual API keys, then run:

```bash
gcloud run deploy industrial-finder \
  --source . \
  --region asia-south1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --timeout 300 \
  --set-env-vars "GOOGLE_API_KEY=YOUR_GEMINI_KEY,GOOGLE_MAPS_API_KEY=YOUR_MAPS_KEY"
```

### Windows (PowerShell) — use backtick for line continuation:
```powershell
gcloud run deploy industrial-finder `
  --source . `
  --region asia-south1 `
  --allow-unauthenticated `
  --memory 512Mi `
  --timeout 300 `
  --set-env-vars "GOOGLE_API_KEY=YOUR_GEMINI_KEY,GOOGLE_MAPS_API_KEY=YOUR_MAPS_KEY"
```

> ⏱️ First deploy takes ~3-5 minutes (building Docker image in the cloud).

---

## Step 8: Access Your App

After deployment completes, you will see:

```
Service URL: https://industrial-finder-xxxxx-el.a.run.app
```

Open that URL in your browser — your app is live! 🎉

---

## 🔄 Updating the Deployment

After making changes, just push and redeploy:

```bash
git add .
git commit -m "your changes"
git push

gcloud run deploy industrial-finder --source . --region asia-south1
```

---

## 🔧 Useful Commands

### Check deployment status
```bash
gcloud run services describe industrial-finder --region asia-south1
```

### View live logs
```bash
gcloud run services logs read industrial-finder --region asia-south1
```

### Delete the service (if needed)
```bash
gcloud run services delete industrial-finder --region asia-south1
```

---

## ⚠️ Important Notes

1. **API Keys**: Never hardcode keys in code. Use `--set-env-vars` during deploy.
2. **Free Tier**: Cloud Run offers 2 million requests/month free.
3. **Region**: `asia-south1` = Mumbai, India (lowest latency for Indian users).
4. **Memory**: 512Mi is enough. Increase to `1Gi` if you see out-of-memory errors.
5. **Timeout**: Set to 300s (5 min) because the full pipeline can take 2-3 minutes.
6. **Google Maps API**: Make sure Places API, Geocoding API, Distance Matrix API, and Maps JavaScript API are enabled in your Cloud Console for the Maps key.
