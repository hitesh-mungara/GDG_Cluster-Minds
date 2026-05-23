# Google Cloud Deployment Guide

This guide will help you deploy the Security Scanner backend to Google Cloud Platform.

## Prerequisites

- Google Cloud account
- Project ID: `twistlock-497205` (or your project ID)
- Billing enabled on your GCP project

## Step 1: Install Google Cloud SDK

### macOS (using Homebrew)
```bash
brew install --cask google-cloud-sdk
```

### macOS (using installer)
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

### Linux
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

### Verify Installation
```bash
gcloud version
```

## Step 2: Initialize and Authenticate

```bash
# Initialize gcloud
gcloud init

# Or authenticate directly
gcloud auth login

# Set up application default credentials
gcloud auth application-default login

# Set your project
gcloud config set project twistlock-497205

# Verify project is set
gcloud config get-value project
```

## Step 3: Enable Required APIs

```bash
# Enable Cloud Run API
gcloud services enable run.googleapis.com

# Enable Cloud Build API (for automated builds)
gcloud services enable cloudbuild.googleapis.com

# Enable Container Registry API
gcloud services enable containerregistry.googleapis.com

# Enable Artifact Registry API
gcloud services enable artifactregistry.googleapis.com
```

## Step 4: Set Environment Variables

**IMPORTANT**: Never commit secrets to the repository!

```bash
# Set environment variables for Cloud Run
gcloud run services update security-scanner \
  --set-env-vars GITHUB_TOKEN=your_github_token_here \
  --set-env-vars GOOGLE_API_KEY=your_google_api_key_here \
  --region asia-south1

# Or use Secret Manager (recommended for production)
# First, create secrets
echo -n "your_github_token" | gcloud secrets create github-token --data-file=-
echo -n "your_google_api_key" | gcloud secrets create google-api-key --data-file=-

# Then reference them in Cloud Run
gcloud run services update security-scanner \
  --set-secrets GITHUB_TOKEN=github-token:latest \
  --set-secrets GOOGLE_API_KEY=google-api-key:latest \
  --region asia-south1
```

## Step 5: Deploy to Cloud Run

### Option A: Deploy using Docker (Recommended)

```bash
# Build and deploy in one command
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

### Option B: Deploy using Cloud Build

```bash
# Submit build to Cloud Build
gcloud builds submit --config cloudbuild.yaml

# The cloudbuild.yaml will automatically deploy to Cloud Run
```

### Option C: Deploy using pre-built Docker image

```bash
# Build Docker image locally
docker build -t gcr.io/twistlock-497205/security-scanner:latest .

# Push to Google Container Registry
docker push gcr.io/twistlock-497205/security-scanner:latest

# Deploy to Cloud Run
gcloud run deploy security-scanner \
  --image gcr.io/twistlock-497205/security-scanner:latest \
  --region asia-south1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 900 \
  --max-instances 10 \
  --min-instances 0
```

## Step 6: Configure Environment Variables (After Deployment)

```bash
# Update environment variables
gcloud run services update security-scanner \
  --update-env-vars GITHUB_TOKEN=ghp_your_token_here \
  --update-env-vars GOOGLE_API_KEY=AIzaSy_your_key_here \
  --region asia-south1
```

## Step 7: Verify Deployment

```bash
# Get service URL
gcloud run services describe security-scanner \
  --region asia-south1 \
  --format 'value(status.url)'

# Test the endpoint
SERVICE_URL=$(gcloud run services describe security-scanner --region asia-south1 --format 'value(status.url)')

curl -X POST "$SERVICE_URL/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/owner/repo.git",
    "severity": "CRITICAL,HIGH",
    "scanners": "vuln,secret,misconfig"
  }'
```

## Step 8: View Logs

```bash
# View logs in real-time
gcloud run services logs read security-scanner \
  --region asia-south1 \
  --follow

# View logs in Cloud Console
# https://console.cloud.google.com/run/detail/asia-south1/security-scanner/logs
```

## Deployment Configuration

### Resource Limits
- **Memory**: 2Gi (adjustable based on workload)
- **CPU**: 2 vCPUs (adjustable)
- **Timeout**: 900 seconds (15 minutes)
- **Max Instances**: 10 (auto-scales based on traffic)
- **Min Instances**: 0 (scales to zero when idle)

### Region
- **Primary**: asia-south1 (Mumbai, India)
- Can be changed to any supported region

### Cost Optimization
- Scales to zero when not in use
- Pay only for actual usage
- First 2 million requests per month are free

## Troubleshooting

### Issue: "gcloud: command not found"
**Solution**: Install Google Cloud SDK (see Step 1)

### Issue: "Permission denied"
**Solution**: 
```bash
gcloud auth login
gcloud auth application-default login
```

### Issue: "API not enabled"
**Solution**: Enable required APIs (see Step 3)

### Issue: "Deployment timeout"
**Solution**: Increase timeout or optimize dependencies
```bash
gcloud run deploy security-scanner \
  --timeout 900 \
  --region asia-south1
```

### Issue: "Out of memory"
**Solution**: Increase memory allocation
```bash
gcloud run services update security-scanner \
  --memory 4Gi \
  --region asia-south1
```

### Issue: "Environment variables not set"
**Solution**: Update environment variables after deployment
```bash
gcloud run services update security-scanner \
  --update-env-vars KEY=VALUE \
  --region asia-south1
```

## Security Best Practices

1. **Use Secret Manager** for sensitive data instead of environment variables
2. **Enable authentication** for production deployments
3. **Set up VPC** for private networking
4. **Enable Cloud Armor** for DDoS protection
5. **Use IAM roles** for fine-grained access control

## Monitoring and Alerts

```bash
# Set up uptime checks
gcloud monitoring uptime-check-configs create security-scanner-check \
  --display-name="Security Scanner Health Check" \
  --resource-type=uptime-url \
  --monitored-resource=url \
  --host=$(gcloud run services describe security-scanner --region asia-south1 --format 'value(status.url)' | sed 's|https://||')

# View metrics in Cloud Console
# https://console.cloud.google.com/run/detail/asia-south1/security-scanner/metrics
```

## Continuous Deployment

To set up automatic deployment on git push:

1. Connect your repository to Cloud Build
2. Create a trigger in Cloud Build Console
3. Use the provided `cloudbuild.yaml` configuration

```bash
# Create a Cloud Build trigger
gcloud builds triggers create github \
  --repo-name=security \
  --repo-owner=your-github-username \
  --branch-pattern="^main$" \
  --build-config=cloudbuild.yaml
```

## Cleanup

To delete the deployment:

```bash
# Delete Cloud Run service
gcloud run services delete security-scanner --region asia-south1

# Delete container images
gcloud container images delete gcr.io/twistlock-497205/security-scanner:latest
```

## Support

For issues or questions:
- GCP Documentation: https://cloud.google.com/run/docs
- Cloud Run Pricing: https://cloud.google.com/run/pricing
- Support: https://cloud.google.com/support

## Next Steps

1. Set up custom domain
2. Configure Cloud CDN
3. Enable Cloud Armor
4. Set up monitoring and alerting
5. Implement CI/CD pipeline