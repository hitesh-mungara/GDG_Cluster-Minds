# Quick Start - Deploy to Google Cloud

Follow these steps to deploy your Security Scanner backend to Google Cloud Run.

## 🚀 One-Command Deployment

If you already have gcloud CLI installed and configured:

```bash
./deploy.sh
```

## 📋 Step-by-Step Instructions

### 1. Install Google Cloud SDK

**macOS (Homebrew):**
```bash
brew install --cask google-cloud-sdk
```

**macOS/Linux (Installer):**
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

### 2. Initialize gcloud

```bash
# Login to Google Cloud
gcloud auth login

# Set up application default credentials
gcloud auth application-default login

# Set your project
gcloud config set project twistlock-497205

# Verify
gcloud config get-value project
```

### 3. Deploy Using the Script

```bash
# Make the script executable (if not already)
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

### 4. Set Environment Variables

After deployment, set your secrets:

```bash
gcloud run services update security-scanner \
  --update-env-vars GITHUB_TOKEN=ghp_your_token_here \
  --update-env-vars GOOGLE_API_KEY=AIzaSy_your_key_here \
  --region asia-south1
```

**Or use Secret Manager (Recommended):**

```bash
# Create secrets
echo -n "ghp_your_token" | gcloud secrets create github-token --data-file=-
echo -n "AIzaSy_your_key" | gcloud secrets create google-api-key --data-file=-

# Grant Cloud Run access to secrets
gcloud secrets add-iam-policy-binding github-token \
  --member=serviceAccount:$(gcloud projects describe twistlock-497205 --format="value(projectNumber)")-compute@developer.gserviceaccount.com \
  --role=roles/secretmanager.secretAccessor

gcloud secrets add-iam-policy-binding google-api-key \
  --member=serviceAccount:$(gcloud projects describe twistlock-497205 --format="value(projectNumber)")-compute@developer.gserviceaccount.com \
  --role=roles/secretmanager.secretAccessor

# Update service to use secrets
gcloud run services update security-scanner \
  --set-secrets GITHUB_TOKEN=github-token:latest \
  --set-secrets GOOGLE_API_KEY=google-api-key:latest \
  --region asia-south1
```

### 5. Test Your Deployment

```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe security-scanner --region asia-south1 --format 'value(status.url)')

# Test the endpoint
curl -X POST "$SERVICE_URL/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/owner/repo.git",
    "severity": "CRITICAL,HIGH",
    "scanners": "vuln,secret,misconfig"
  }'
```

## 🔍 View Logs

```bash
# Real-time logs
gcloud run services logs read security-scanner --region asia-south1 --follow

# Or view in Console
# https://console.cloud.google.com/run/detail/asia-south1/security-scanner/logs
```

## 🛠️ Manual Deployment (Alternative)

If you prefer manual deployment:

```bash
# Enable APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# Deploy
gcloud run deploy security-scanner \
  --source . \
  --region asia-south1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 900 \
  --max-instances 10 \
  --min-instances 0 \
  --port 8080
```

## 📚 Additional Resources

- **Full Deployment Guide**: See `DEPLOYMENT_GUIDE.md` for detailed instructions
- **GCP Console**: https://console.cloud.google.com/run
- **Cloud Run Docs**: https://cloud.google.com/run/docs

## ⚠️ Important Notes

1. **Never commit `.env` file** - It contains sensitive credentials
2. **Use Secret Manager** for production deployments
3. **Monitor costs** - Cloud Run charges for usage
4. **Set up alerts** - Configure monitoring for production

## 🆘 Troubleshooting

**gcloud not found:**
```bash
# Install gcloud SDK (see step 1)
```

**Permission denied:**
```bash
gcloud auth login
gcloud auth application-default login
```

**Deployment fails:**
```bash
# Check logs
gcloud run services logs read security-scanner --region asia-south1 --tail 100
```

**Environment variables not working:**
```bash
# Update after deployment
gcloud run services update security-scanner \
  --update-env-vars KEY=VALUE \
  --region asia-south1
```

## 🎉 Success!

Once deployed, your service will be available at:
```
https://security-scanner-[hash]-uc.a.run.app
```

The URL will be displayed after successful deployment.