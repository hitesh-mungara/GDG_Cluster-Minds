import os
import sys
import uuid
import requests
from git import Repo
from fastapi import FastAPI
from dotenv import load_dotenv

# Load environment variables from .env file (if it exists)
# In production (Cloud Run), environment variables are set via Cloud Run configuration
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    # Running in production - environment variables should be set by Cloud Run
    print("ℹ️  No .env file found - using environment variables from Cloud Run")

# Add parent directory to path to import agents module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.graph import (
    run_pipeline
)

app = FastAPI()

BASE_DIR = "repos"

os.makedirs(
    BASE_DIR,
    exist_ok=True
)


def clone_repo(repo_url):

    repo_name = str(uuid.uuid4())

    local_path = os.path.join(
        BASE_DIR,
        repo_name
    )

    Repo.clone_from(
        repo_url,
        local_path
    )

    return local_path


@app.post("/analyze")

def analyze_repo(payload: dict):

    print("\n" + "="*60)
    print("🚀 STARTING SECURITY ANALYSIS")
    print("="*60)

    repo_url = payload.get(
        "repo_url"
    )

    if not repo_url:
        print("❌ ERROR: repo_url is required")
        return {
            "error": "repo_url is required"
        }

    print(f"📦 Repository URL: {repo_url}")

    # Get optional parameters with defaults
    severity = payload.get(
        "severity",
        "CRITICAL,HIGH"
    )

    scanners = payload.get(
        "scanners",
        "vuln,secret,misconfig"
    )

    print(f"🔍 Severity Filter: {severity}")
    print(f"🔍 Scanners: {scanners}")

    print("\n" + "-"*60)
    print("📥 CLONING REPOSITORY")
    print("-"*60)

    repo_path = clone_repo(
        repo_url
    )

    print(f"✅ Repository cloned to: {repo_path}")

    # Prepare payload for Trivy API
    trivy_payload = {
        "repo_url": repo_url,
        "severity": severity,
        "scanners": scanners
    }

    print("\n" + "-"*60)
    print("🔒 RUNNING TRIVY SECURITY SCAN")
    print("-"*60)
    print("⏳ This may take several minutes...")
    print(f"📡 Sending request to Trivy API...")

    try:
        trivy_response = requests.post(
            "https://trivy-api-109127597395.asia-south1.run.app/scan",
            json=trivy_payload,
            timeout=600
        )

        print(f"📊 Trivy API Response Status: {trivy_response.status_code}")

        trivy_response.raise_for_status()

        scan_data = (
            trivy_response.json()
        )

        print("✅ Trivy scan completed successfully")

    except requests.exceptions.RequestException as e:
        print(f"❌ Trivy scan failed: {str(e)}")
        return {
            "error": f"Trivy scan failed: {str(e)}"
        }

    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return {
            "error": f"Unexpected error: {str(e)}"
        }

    print("\n" + "-"*60)
    print("🤖 STARTING AI AGENT PIPELINE")
    print("-"*60)
    print("📋 Pipeline: Parse → Intel → Risk → Remediation (Summary)")
    print("⚠️  Note: Pipeline stops at Remediation Agent (no PR creation)")

    result = run_pipeline(
        scan_data=scan_data,
        repo_url=repo_url,
        repo_path=repo_path
    )

    print("\n" + "="*60)
    print("✅ ANALYSIS COMPLETE - SUMMARY GENERATED")
    print("="*60 + "\n")

    return result