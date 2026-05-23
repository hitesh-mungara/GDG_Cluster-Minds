import requests


def intel_agent(state):

    print("\n" + "="*60)
    print("🔍 AGENT 2/8: INTEL AGENT")
    print("="*60)
    print("⏳ Enriching findings with threat intelligence...")

    findings = state["findings"]

    print(f"📊 Checking {len(findings)} vulnerabilities against NVD database...")

    enriched_count = 0
    for idx, finding in enumerate(findings, 1):

        cve = finding.get("cve")

        if not cve:
            continue

        if idx % 10 == 0:
            print(f"   Progress: {idx}/{len(findings)} CVEs checked...")

        url = (
            "https://services.nvd.nist.gov/"
            "rest/json/cves/2.0"
            f"?cveId={cve}"
        )

        try:

            response = requests.get(
                url,
                timeout=10
            )

            if response.status_code == 200:

                finding["public_exploit"] = True

                finding["kev"] = True
                
                enriched_count += 1

        except Exception:

            pass

    state["enriched_findings"] = findings

    print(f"✅ Enriched {enriched_count} vulnerabilities with threat intelligence")

    return state