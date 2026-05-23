import os
import subprocess
import uuid
from git import Repo

BASE_DIR = "repos"
REPORT_DIR = "reports"

os.makedirs(BASE_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)


def clone_repo(repo_url):

    repo_name = str(uuid.uuid4())

    local_path = os.path.join(
        BASE_DIR,
        repo_name
    )

    print(f"\nCloning Repo: {repo_url}\n")

    Repo.clone_from(
        repo_url,
        local_path
    )

    print(f"\nRepo Cloned To: {local_path}\n")

    return local_path


def run_scanners(repo_path):

    trivy_output = os.path.join(
        REPORT_DIR,
        "trivy.json"
    )

    gitleaks_output = os.path.join(
        REPORT_DIR,
        "gitleaks.json"
    )

    semgrep_output = os.path.join(
        REPORT_DIR,
        "semgrep.json"
    )

    # -----------------------------------
    # CLEAN OLD REPORTS
    # -----------------------------------

    for report in [
        trivy_output,
        gitleaks_output,
        semgrep_output
    ]:
        if os.path.exists(report):
            os.remove(report)

    # -----------------------------------
    # TRIVY SCAN
    # -----------------------------------

    print("\n==============================")
    print("RUNNING TRIVY SCAN")
    print("==============================\n")

    trivy_result = subprocess.run([
        "trivy",
        "repo",
        "--scanners",
        "vuln",
        "--format",
        "json",
        "-o",
        trivy_output,
        repo_path
    ],
    capture_output=True,
    text=True,
    timeout=300
    )

    print("\nTRIVY STDOUT:\n")
    print(trivy_result.stdout)

    print("\nTRIVY STDERR:\n")
    print(trivy_result.stderr)

    # -----------------------------------
    # GITLEAKS SCAN
    # -----------------------------------

    print("\n==============================")
    print("RUNNING GITLEAKS SCAN")
    print("==============================\n")

    gitleaks_result = subprocess.run([
        "gitleaks",
        "detect",
        "--source",
        repo_path,
        "-f",
        "json",
        "-r",
        gitleaks_output
    ],
    capture_output=True,
    text=True,
    timeout=300
    )

    print("\nGITLEAKS STDOUT:\n")
    print(gitleaks_result.stdout)

    print("\nGITLEAKS STDERR:\n")
    print(gitleaks_result.stderr)

    # -----------------------------------
    # SEMGREP SCAN
    # -----------------------------------

    print("\n==============================")
    print("RUNNING SEMGREP SCAN")
    print("==============================\n")

    semgrep_result = subprocess.run([
        "semgrep",
        "--config=auto",
        repo_path,
        "--json",
        "-o",
        semgrep_output
    ],
    capture_output=True,
    text=True,
    timeout=300
    )

    print("\nSEMGREP STDOUT:\n")
    print(semgrep_result.stdout)

    print("\nSEMGREP STDERR:\n")
    print(semgrep_result.stderr)

    # -----------------------------------
    # REPORT VALIDATION
    # -----------------------------------

    print("\n==============================")
    print("REPORT VALIDATION")
    print("==============================\n")

    print(
        "Trivy Exists:",
        os.path.exists(trivy_output)
    )

    print(
        "Gitleaks Exists:",
        os.path.exists(gitleaks_output)
    )

    print(
        "Semgrep Exists:",
        os.path.exists(semgrep_output)
    )

    if os.path.exists(trivy_output):

        print("\nTRIVY REPORT SIZE:\n")

        print(
            os.path.getsize(trivy_output),
            "bytes"
        )

    return {
        "trivy": trivy_output,
        "gitleaks": gitleaks_output,
        "semgrep": semgrep_output
    }