#!/bin/bash

# Deployment script for Google Cloud Run
# This script automates the deployment process

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Security Scanner - GCP Deployment${NC}"
echo -e "${GREEN}========================================${NC}\n"

# Configuration
PROJECT_ID="twistlock-497205"
SERVICE_NAME="security-scanner"
REGION="asia-south1"
MEMORY="2Gi"
CPU="2"
TIMEOUT="900"
MAX_INSTANCES="10"
MIN_INSTANCES="0"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}Error: gcloud CLI is not installed${NC}"
    echo -e "${YELLOW}Please install it using:${NC}"
    echo "  macOS: brew install --cask google-cloud-sdk"
    echo "  Linux: curl https://sdk.cloud.google.com | bash"
    exit 1
fi

echo -e "${GREEN}✓ gcloud CLI found${NC}\n"

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
    echo -e "${YELLOW}Authenticating with Google Cloud...${NC}"
    gcloud auth login
fi

echo -e "${GREEN}✓ Authenticated${NC}\n"

# Set project
echo -e "${YELLOW}Setting project to: $PROJECT_ID${NC}"
gcloud config set project $PROJECT_ID

echo -e "${GREEN}✓ Project set${NC}\n"

# Enable required APIs
echo -e "${YELLOW}Enabling required APIs...${NC}"
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com

echo -e "${GREEN}✓ APIs enabled${NC}\n"

# Check for environment variables
echo -e "${YELLOW}Checking environment variables...${NC}"
if [ -f .env ]; then
    echo -e "${GREEN}✓ .env file found${NC}"
    echo -e "${YELLOW}Note: Environment variables will need to be set manually after deployment${NC}"
else
    echo -e "${RED}Warning: .env file not found${NC}"
    echo -e "${YELLOW}You'll need to set GITHUB_TOKEN and GOOGLE_API_KEY after deployment${NC}"
fi

echo ""

# Deploy to Cloud Run
echo -e "${YELLOW}Deploying to Cloud Run...${NC}"
echo -e "${YELLOW}This may take several minutes...${NC}\n"

gcloud run deploy $SERVICE_NAME \
  --source . \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --memory $MEMORY \
  --cpu $CPU \
  --timeout $TIMEOUT \
  --max-instances $MAX_INSTANCES \
  --min-instances $MIN_INSTANCES \
  --port 8080

echo -e "\n${GREEN}✓ Deployment successful!${NC}\n"

# Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)')

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}\n"
echo -e "Service URL: ${GREEN}$SERVICE_URL${NC}\n"

# Remind about environment variables
echo -e "${YELLOW}⚠️  IMPORTANT: Set environment variables${NC}"
echo -e "Run the following commands to set your secrets:\n"
echo -e "gcloud run services update $SERVICE_NAME \\"
echo -e "  --update-env-vars GITHUB_TOKEN=your_github_token \\"
echo -e "  --update-env-vars GOOGLE_API_KEY=your_google_api_key \\"
echo -e "  --region $REGION\n"

echo -e "${YELLOW}Or use Secret Manager (recommended):${NC}\n"
echo -e "# Create secrets"
echo -e "echo -n 'your_github_token' | gcloud secrets create github-token --data-file=-"
echo -e "echo -n 'your_google_api_key' | gcloud secrets create google-api-key --data-file=-\n"
echo -e "# Update service to use secrets"
echo -e "gcloud run services update $SERVICE_NAME \\"
echo -e "  --set-secrets GITHUB_TOKEN=github-token:latest \\"
echo -e "  --set-secrets GOOGLE_API_KEY=google-api-key:latest \\"
echo -e "  --region $REGION\n"

# Test endpoint
echo -e "${YELLOW}Test your deployment:${NC}\n"
echo -e "curl -X POST \"$SERVICE_URL/analyze\" \\"
echo -e "  -H \"Content-Type: application/json\" \\"
echo -e "  -d '{"
echo -e "    \"repo_url\": \"https://github.com/owner/repo.git\","
echo -e "    \"severity\": \"CRITICAL,HIGH\","
echo -e "    \"scanners\": \"vuln,secret,misconfig\""
echo -e "  }'\n"

echo -e "${GREEN}View logs:${NC}"
echo -e "gcloud run services logs read $SERVICE_NAME --region $REGION --follow\n"

echo -e "${GREEN}View in Console:${NC}"
echo -e "https://console.cloud.google.com/run/detail/$REGION/$SERVICE_NAME\n"

# Made with Bob
