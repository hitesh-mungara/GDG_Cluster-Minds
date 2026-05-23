import requests


def get_cve_details(cve_id):

    url = (
        "https://services.nvd.nist.gov/rest/json/cves/2.0"
        f"?cveId={cve_id}"
    )

    response = requests.get(url)

    if response.status_code != 200:
        return {}

    return response.json()