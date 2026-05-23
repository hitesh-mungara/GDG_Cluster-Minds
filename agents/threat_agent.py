from backend.nvd_service import get_cve_details


def threat_agent(findings):

    for finding in findings:

        if finding.get("type") == "cve":
            cve_data = get_cve_details(finding["cve"])

            finding["nvd_data"] = cve_data

    return findings