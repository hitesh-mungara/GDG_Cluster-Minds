import requests

GITHUB_TOKEN = "YOUR_GITHUB_TOKEN"


def create_issue(repo, title, body):

    url = f"https://api.github.com/repos/{repo}/issues"

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}"
    }

    payload = {
        "title": title,
        "body": body
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload
    )

    return response.json()