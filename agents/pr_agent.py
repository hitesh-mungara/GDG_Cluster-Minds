import os
import subprocess
import requests


GITHUB_TOKEN = os.getenv(
    "GITHUB_TOKEN",
    ""
)


def pr_agent(state):

    print("\n====================")
    print("PR AGENT STARTED")
    print("====================")

    # =========================================
    # AI APPROVAL CHECK
    # =========================================

    if not state.get("approve_pr"):

        print("\nAI REJECTED PR CREATION\n")

        state["pr_response"] = {

            "message":
            "AI rejected automatic PR creation"
        }

        return state

    repo_path = state["repo_path"]

    repo_url = state["repo_url"]

    fixes = state["generated_fixes"]

    print("\nRECEIVED FIXES\n")

    print(fixes)

    # =========================================
    # NO FIXES
    # =========================================

    if not fixes:

        state["pr_response"] = {

            "message":
            "No fixes generated"
        }

        return state

    branch_name = (
        "ai-security-fixes"
    )

    # =========================================
    # AUTHENTICATED REMOTE
    # =========================================

    authenticated_url = (
        repo_url.replace(
            "https://",
            f"https://{GITHUB_TOKEN}@"
        )
    )

    # =========================================
    # SET REMOTE URL
    # =========================================

    remote_result = subprocess.run([
        "git",
        "remote",
        "set-url",
        "origin",
        authenticated_url
    ],
    cwd=repo_path,
    capture_output=True,
    text=True
    )

    print("\nREMOTE RESULT\n")

    print(remote_result.stdout)
    print(remote_result.stderr)

    # =========================================
    # CREATE BRANCH
    # =========================================

    branch_result = subprocess.run([
        "git",
        "checkout",
        "-B",
        branch_name
    ],
    cwd=repo_path,
    capture_output=True,
    text=True
    )

    print("\nBRANCH RESULT\n")

    print(branch_result.stdout)
    print(branch_result.stderr)

    # =========================================
    # GIT CONFIG
    # =========================================

    subprocess.run([
        "git",
        "config",
        "user.email",
        "ai-agent@secureops.ai"
    ],
    cwd=repo_path
    )

    subprocess.run([
        "git",
        "config",
        "user.name",
        "SecureOps AI"
    ],
    cwd=repo_path
    )

    # =========================================
    # GIT STATUS BEFORE COMMIT
    # =========================================

    status_before = subprocess.run([
        "git",
        "status"
    ],
    cwd=repo_path,
    capture_output=True,
    text=True
    )

    print("\nGIT STATUS BEFORE\n")

    print(status_before.stdout)

    # =========================================
    # GIT ADD
    # =========================================

    add_result = subprocess.run([
        "git",
        "add",
        "."
    ],
    cwd=repo_path,
    capture_output=True,
    text=True
    )

    print("\nADD RESULT\n")

    print(add_result.stdout)
    print(add_result.stderr)

    # =========================================
    # GIT COMMIT
    # =========================================

    commit_result = subprocess.run([
        "git",
        "commit",
        "-m",
        "AI-generated security remediation fixes"
    ],
    cwd=repo_path,
    capture_output=True,
    text=True
    )

    print("\nCOMMIT RESULT\n")

    print(commit_result.stdout)
    print(commit_result.stderr)

    # =========================================
    # GIT STATUS AFTER COMMIT
    # =========================================

    status_after = subprocess.run([
        "git",
        "status"
    ],
    cwd=repo_path,
    capture_output=True,
    text=True
    )

    print("\nGIT STATUS AFTER\n")

    print(status_after.stdout)

    # =========================================
    # PUSH BRANCH
    # =========================================

    push_result = subprocess.run([
        "git",
        "push",
        "--set-upstream",
        "origin",
        branch_name
    ],
    cwd=repo_path,
    capture_output=True,
    text=True
    )

    print("\nPUSH RESULT\n")

    print(push_result.stdout)
    print(push_result.stderr)

    # =========================================
    # CHECK PUSH FAILURE
    # =========================================

    if push_result.returncode != 0:

        state["pr_response"] = {

            "message":
            "Git push failed",

            "details":
            push_result.stderr
        }

        return state

    # =========================================
    # EXTRACT OWNER/REPO
    # =========================================

    cleaned = (
        repo_url
        .replace(
            "https://github.com/",
            ""
        )
        .replace(".git", "")
    )

    # =========================================
    # GET DEFAULT BRANCH
    # =========================================

    repo_api_url = (
        f"https://api.github.com/repos/"
        f"{cleaned}"
    )

    headers = {
        "Authorization":
        f"Bearer {GITHUB_TOKEN}",

        "Accept":
        "application/vnd.github+json"
    }

    try:
        repo_info = requests.get(
            repo_api_url,
            headers=headers
        )

        default_branch = "main"

        if repo_info.status_code == 200:
            default_branch = (
                repo_info
                .json()
                .get(
                    "default_branch",
                    "main"
                )
            )

        print(
            f"\nDETECTED DEFAULT BRANCH: "
            f"{default_branch}\n"
        )

    except Exception as e:

        print(
            f"\nFAILED TO DETECT BRANCH: "
            f"{str(e)}\n"
        )

        default_branch = "main"

    # =========================================
    # CREATE PULL REQUEST
    # =========================================

    url = (
        f"https://api.github.com/repos/"
        f"{cleaned}/pulls"
    )

    payload = {

        "title":
        "AI Security Remediation PR",

        "body":
        """
        Automatically generated by SecureOps AI.

        This PR contains:
        - dependency upgrades
        - remediation fixes
        - AI-generated security improvements
        """,

        "head":
        branch_name,

        "base":
        default_branch
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload
    )

    print("\nPR RESPONSE\n")

    print(response.json())

    state["pr_response"] = (
        response.json()
    )

    return state