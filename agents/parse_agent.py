def parse_agent(state):

    print("\n" + "="*60)
    print("📋 AGENT 1/8: PARSE AGENT")
    print("="*60)
    print("⏳ Parsing Trivy scan results...")

    scan_data = state["scan_data"]

    findings = []

    # Handle both direct Results and nested trivy_result structure
    results = []
    
    if "trivy_result" in scan_data:
        # Nested structure
        print("📦 Detected nested trivy_result structure")
        results = (
            scan_data
            .get("trivy_result", {})
            .get("Results", [])
        )
    elif "Results" in scan_data:
        # Direct structure from Trivy API
        print("📦 Detected direct Results structure")
        results = scan_data.get("Results", [])
    else:
        # Fallback: scan_data might be the results array itself
        if isinstance(scan_data, list):
            print("📦 Detected array structure")
            results = scan_data

    print(f"🔍 Processing {len(results)} result groups...")

    vuln_count = 0
    for result in results:

        vulnerabilities = result.get(
            "Vulnerabilities",
            []
        )

        if vulnerabilities is None:
            continue

        vuln_count += len(vulnerabilities) if vulnerabilities else 0

        for vuln in vulnerabilities:

            findings.append({
                "cve": vuln.get(
                    "VulnerabilityID"
                ),
                "package": vuln.get(
                    "PkgName"
                ),
                "severity": vuln.get(
                    "Severity"
                ),
                "installed_version": vuln.get(
                    "InstalledVersion"
                ),
                "fixed_version": vuln.get(
                    "FixedVersion"
                ),
                "title": vuln.get(
                    "Title"
                )
            })

    state["findings"] = findings

    print(f"✅ Parsed {len(findings)} vulnerabilities")
    print(f"   - CRITICAL: {sum(1 for f in findings if f.get('severity') == 'CRITICAL')}")
    print(f"   - HIGH: {sum(1 for f in findings if f.get('severity') == 'HIGH')}")
    print(f"   - MEDIUM: {sum(1 for f in findings if f.get('severity') == 'MEDIUM')}")
    print(f"   - LOW: {sum(1 for f in findings if f.get('severity') == 'LOW')}")

    return state