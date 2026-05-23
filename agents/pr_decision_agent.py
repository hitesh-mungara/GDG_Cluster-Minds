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


def pr_decision_agent(state):

    print("\n" + "="*60)
    print("🤔 AGENT 6/8: PR DECISION AGENT")
    print("="*60)
    print("⏳ AI evaluating if automatic PR creation is safe...")

    findings = state[
        "prioritized_findings"
    ]

    fixes = state[
        "generated_fixes"
    ]

    # -----------------------------------
    # NO FIXES → REJECT
    # -----------------------------------

    if not fixes:

        print("❌ No fixes generated - PR creation rejected")
        state["approve_pr"] = False

        return state

    print(f"📊 Analyzing {len(fixes)} fixes for safety...")

    prompt = f"""
    You are an autonomous
    security remediation agent.

    Analyze the following.

    Vulnerabilities:
    {findings}

    Generated Fixes:
    {fixes}

    Decide:
    1. Is automatic PR creation safe?
    2. Could these upgrades break the app?
    3. Is human approval required?

    Return ONLY:
    APPROVE
    or
    REJECT
    """

    try:

        print("🤖 Consulting AI for decision...")

        response = llm.invoke(
            prompt
        )

        decision = (
            response.content
            .strip()
            .upper()
        )

        print(f"\n🎯 AI Decision: {decision}")

        if "APPROVE" in decision:

            print("✅ AI approved automatic PR creation")
            state["approve_pr"] = True

        else:

            print("⚠️  AI rejected automatic PR creation - human review required")
            state["approve_pr"] = False

    except Exception as e:

        print(f"❌ AI decision failed: {str(e)}")
        print("⚠️  Defaulting to REJECT for safety")

        state["approve_pr"] = False

    return state