def calculate_score(finding):

    score = 0

    severity = finding.get(
        "severity",
        ""
    )

    if severity == "CRITICAL":
        score += 50

    elif severity == "HIGH":
        score += 35

    elif severity == "MEDIUM":
        score += 20

    if finding.get("public_exploit"):
        score += 25

    if finding.get("kev"):
        score += 25

    return min(score, 100)


def risk_agent(state):

    print("\n" + "="*60)
    print("⚠️  AGENT 3/8: RISK AGENT")
    print("="*60)
    print("⏳ Calculating risk scores and prioritizing...")

    findings = state[
        "enriched_findings"
    ]

    print(f"📊 Analyzing {len(findings)} vulnerabilities...")

    for finding in findings:

        finding["risk_score"] = (
            calculate_score(
                finding
            )
        )

    findings = sorted(
        findings,
        key=lambda x: x["risk_score"],
        reverse=True
    )

    state[
        "prioritized_findings"
    ] = findings

    # Show top 5 highest risk
    print(f"✅ Risk scoring complete")
    print(f"\n🔥 Top 5 Highest Risk Vulnerabilities:")
    for idx, finding in enumerate(findings[:5], 1):
        print(f"   {idx}. {finding.get('cve', 'N/A')} - Risk Score: {finding.get('risk_score', 0)}/100")
        print(f"      Package: {finding.get('package', 'N/A')} | Severity: {finding.get('severity', 'N/A')}")

    return state