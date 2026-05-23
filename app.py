import json
import os
import time
import uuid
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl

from google.cloud.devtools import cloudbuild_v1
from google.cloud import storage
from google.protobuf.duration_pb2 import Duration


def log_event(event_name: str, **kwargs):
    """
    Human-readable Cloud Run log line.
    This will clearly show in:
    - gcloud run services logs read
    - Logs Explorer textPayload
    - log-based metrics
    """
    fields = [f"event={event_name}"]

    for key, value in kwargs.items():
        if value is None:
            continue

        safe_value = str(value).replace(" ", "_").replace("\n", "_")
        fields.append(f"{key}={safe_value}")

    print("OBS_APP_EVENT " + " ".join(fields), flush=True)


app = FastAPI(title="Observable Trivy Cloud Build Scanner API")


PROJECT_ID = os.environ["PROJECT_ID"]
BUCKET_NAME = os.environ["BUCKET_NAME"]


class ScanRequest(BaseModel):
    repo_url: HttpUrl
    branch: Optional[str] = None
    severity: str = "CRITICAL,HIGH"
    scanners: str = "vuln,secret,misconfig"


@app.get("/health")
def health():
    log_event("health_check")
    return {"status": "ok"}

APP_VERSION = "obs-v3-visible-logs"


@app.get("/version")
def version():
    log_event("version_check", app_version=APP_VERSION)
    return {
        "app_version": APP_VERSION,
        "logging_mode": "OBS_APP_EVENT_TEXT",
    }

@app.post("/scan")
def scan_repo(request: ScanRequest):
    scan_start_time = time.time()

    scan_id = str(uuid.uuid4())
    result_object = f"trivy-results/{scan_id}/trivy-result.json"
    result_gcs_uri = f"gs://{BUCKET_NAME}/{result_object}"

    repo_url = str(request.repo_url)

    if not repo_url.startswith("https://github.com/"):
        log_event(
            "scan_rejected",
            scan_id=scan_id,
            reason="non_github_repo",
            repo_url=repo_url,
        )
        raise HTTPException(
            status_code=400,
            detail="Only public GitHub repositories are allowed",
        )

    log_event(
        "scan_requested",
        scan_id=scan_id,
        repo_url=repo_url,
        branch=request.branch,
        severity=request.severity,
        scanners=request.scanners,
        result_gcs_uri=result_gcs_uri,
    )

    try:
        build_id = run_cloud_build(
            scan_id=scan_id,
            repo_url=repo_url,
            branch=request.branch,
            severity=request.severity,
            scanners=request.scanners,
            result_gcs_uri=result_gcs_uri,
        )

        log_event(
            "gcs_result_read_started",
            scan_id=scan_id,
            build_id=build_id,
            result_gcs_uri=result_gcs_uri,
        )

        scan_json = read_result_from_gcs(result_object)

        log_event(
            "gcs_result_read_completed",
            scan_id=scan_id,
            build_id=build_id,
            result_gcs_uri=result_gcs_uri,
        )

        summary = summarize_trivy_result(scan_json)

        duration_seconds = round(time.time() - scan_start_time, 2)

        log_event(
            "scan_completed",
            scan_id=scan_id,
            build_id=build_id,
            repo_url=repo_url,
            branch=request.branch,
            severity=request.severity,
            scanners=request.scanners,
            result_gcs_uri=result_gcs_uri,
            duration_seconds=duration_seconds,
            total_vulnerabilities=summary.get("total_vulnerabilities", 0),
            total_misconfigurations=summary.get("total_misconfigurations", 0),
            total_secrets=summary.get("total_secrets", 0),
            critical_count=summary.get("vulnerabilities_by_severity", {}).get("CRITICAL", 0),
            high_count=summary.get("vulnerabilities_by_severity", {}).get("HIGH", 0),
            medium_count=summary.get("vulnerabilities_by_severity", {}).get("MEDIUM", 0),
            low_count=summary.get("vulnerabilities_by_severity", {}).get("LOW", 0),
        )

        return {
            "scan_id": scan_id,
            "build_id": build_id,
            "repo_url": repo_url,
            "branch": request.branch,
            "result_gcs_uri": result_gcs_uri,
            "duration_seconds": duration_seconds,
            "summary": summary,
            "trivy_result": scan_json,
        }

    except Exception as e:
        duration_seconds = round(time.time() - scan_start_time, 2)

        log_event(
            "scan_failed",
            scan_id=scan_id,
            repo_url=repo_url,
            branch=request.branch,
            severity=request.severity,
            scanners=request.scanners,
            duration_seconds=duration_seconds,
            error=str(e),
        )

        raise HTTPException(status_code=500, detail=str(e))


def run_cloud_build(
    scan_id: str,
    repo_url: str,
    branch: Optional[str],
    severity: str,
    scanners: str,
    result_gcs_uri: str,
) -> str:
    client = cloudbuild_v1.CloudBuildClient()

    if branch:
        clone_command = f'git clone --depth 1 --branch "{branch}" "{repo_url}" source'
    else:
        clone_command = f'git clone --depth 1 "{repo_url}" source'

    log_event(
        "cloud_build_create_started",
        scan_id=scan_id,
        repo_url=repo_url,
        branch=branch,
        severity=severity,
        scanners=scanners,
    )

    scan_script = f"""
set -e

echo "OBS_EVENT scan_id={scan_id} event=build_container_started"

apt-get update
apt-get install -y wget gnupg lsb-release git ca-certificates

echo "OBS_EVENT scan_id={scan_id} event=trivy_install_started"
wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | gpg --dearmor -o /usr/share/keyrings/trivy.gpg
echo "deb [signed-by=/usr/share/keyrings/trivy.gpg] https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" > /etc/apt/sources.list.d/trivy.list
apt-get update
apt-get install -y trivy
trivy --version

echo "OBS_EVENT scan_id={scan_id} event=repo_clone_started repo_url={repo_url}"
{clone_command}

echo "OBS_EVENT scan_id={scan_id} event=repo_clone_completed"
ls -la source

echo "OBS_EVENT scan_id={scan_id} event=trivy_scan_started severity={severity} scanners={scanners}"
trivy fs source \
  --format json \
  --severity "{severity}" \
  --scanners "{scanners}" \
  --output /workspace/trivy-result.json \
  --quiet

echo "OBS_EVENT scan_id={scan_id} event=trivy_scan_completed"

echo "OBS_EVENT scan_id={scan_id} event=gcs_upload_started uri={result_gcs_uri}"
gcloud storage cp /workspace/trivy-result.json "{result_gcs_uri}"

echo "OBS_EVENT scan_id={scan_id} event=gcs_upload_completed uri={result_gcs_uri}"
"""

    build = cloudbuild_v1.Build(
        steps=[
            cloudbuild_v1.BuildStep(
                name="gcr.io/google.com/cloudsdktool/cloud-sdk:slim",
                entrypoint="bash",
                args=["-c", scan_script],
            )
        ],
        timeout=Duration(seconds=1800),
        service_account=(
            f"projects/{PROJECT_ID}/serviceAccounts/"
            f"trivy-cloudbuild-sa@{PROJECT_ID}.iam.gserviceaccount.com"
        ),
        options=cloudbuild_v1.BuildOptions(
            logging=cloudbuild_v1.BuildOptions.LoggingMode.CLOUD_LOGGING_ONLY
        ),
    )

    operation = client.create_build(project_id=PROJECT_ID, build=build)
    result = operation.result()

    log_event(
        "cloud_build_finished",
        scan_id=scan_id,
        build_id=result.id,
        build_status=result.status.name,
    )

    if result.status != cloudbuild_v1.Build.Status.SUCCESS:
        log_event(
            "cloud_build_failed",
            scan_id=scan_id,
            build_id=result.id,
            build_status=result.status.name,
        )
        raise RuntimeError(
            f"Cloud Build failed. Build ID: {result.id}, status: {result.status.name}"
        )

    log_event(
        "cloud_build_completed",
        scan_id=scan_id,
        build_id=result.id,
        build_status=result.status.name,
    )

    return result.id


def read_result_from_gcs(result_object: str) -> dict:
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(result_object)

    if not blob.exists():
        raise RuntimeError(f"Trivy result file not found in GCS: {result_object}")

    content = blob.download_as_text()
    return json.loads(content)


def summarize_trivy_result(scan_json: dict) -> dict:
    counts = {
        "CRITICAL": 0,
        "HIGH": 0,
        "MEDIUM": 0,
        "LOW": 0,
        "UNKNOWN": 0,
    }

    total_vulnerabilities = 0
    total_misconfigurations = 0
    total_secrets = 0

    for result in scan_json.get("Results", []):
        for vuln in result.get("Vulnerabilities") or []:
            severity = vuln.get("Severity", "UNKNOWN")
            counts[severity] = counts.get(severity, 0) + 1
            total_vulnerabilities += 1

        for _ in result.get("Misconfigurations") or []:
            total_misconfigurations += 1

        for _ in result.get("Secrets") or []:
            total_secrets += 1

    return {
        "total_vulnerabilities": total_vulnerabilities,
        "total_misconfigurations": total_misconfigurations,
        "total_secrets": total_secrets,
        "vulnerabilities_by_severity": counts,
    }