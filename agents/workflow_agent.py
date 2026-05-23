def workflow_agent(state):

    print("\n" + "="*60)
    print("📋 AGENT 8/8: WORKFLOW AGENT")
    print("="*60)
    print("⏳ Determining additional workflow actions...")

    findings = state[
        "prioritized_findings"
    ]

    actions = []

    high_risk_count = 0
    medium_risk_count = 0

    for finding in findings:

        score = finding.get(
            "risk_score",
            0
        )

        if score >= 80:

            actions.append({
                "action": "SLACK_ALERT",
                "cve": finding.get("cve")
            })
            high_risk_count += 1

        elif score >= 60:

            actions.append({
                "action": "CREATE_JIRA",
                "cve": finding.get("cve")
            })
            medium_risk_count += 1

    state["workflow_actions"] = (
        actions
    )

    print(f"✅ Workflow actions determined:")
    print(f"   - Slack alerts: {high_risk_count} (risk score >= 80)")
    print(f"   - JIRA tickets: {medium_risk_count} (risk score >= 60)")

    return state