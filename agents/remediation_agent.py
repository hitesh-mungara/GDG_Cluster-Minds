import os

from langchain_google_genai import (
    ChatGoogleGenerativeAI
)

llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash",
    google_api_key=os.getenv(
        "GOOGLE_API_KEY",
        ""
    )
)


def remediation_agent(state):

    print("\n" + "="*60)
    print("🤖 AGENT 4/8: REMEDIATION AGENT")
    print("="*60)
    print("⏳ Generating AI-powered remediation strategies...")

    findings = state[
        "prioritized_findings"
    ]

    findings = findings[:5]

    print(f"📋 Analyzing top {len(findings)} vulnerabilities with AI...")

    remediation_output = []

    for idx, finding in enumerate(findings, 1):

        print(f"   {idx}/{len(findings)} - Analyzing {finding.get('cve', 'N/A')}...")

        prompt = f"""
        Analyze this vulnerability.

        CVE:
        {finding.get("cve")}

        Package:
        {finding.get("package")}

        Severity:
        {finding.get("severity")}

        Risk Score:
        {finding.get("risk_score")}

        Generate:
        1. Business impact
        2. Exploitability
        3. Remediation steps
        4. Patch strategy
        """

        try:

            response = llm.invoke(
                prompt
            )

            remediation_output.append({
                "finding": finding,
                "analysis": response.content
            })

            print(f"      ✅ AI analysis complete")

        except Exception as e:

            print(f"      ⚠️  AI unavailable: {str(e)}")

            remediation_output.append({
                "finding": finding,
                "analysis": "AI unavailable"
            })

    state[
        "remediation_plan"
    ] = remediation_output

    print(f"✅ Generated {len(remediation_output)} remediation strategies")

    return state