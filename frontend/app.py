import streamlit as st
import requests
import pandas as pd

st.set_page_config(
    page_title="SecureOps AI",
    layout="wide"
)

st.title("Agentic AI Security Platform")

repo_url = st.text_input(
    "Enter GitHub Repository URL",
    value="https://github.com/WebGoat/WebGoat.git"
)

severity = st.multiselect(
    "Select Severity",
    ["CRITICAL", "HIGH", "MEDIUM", "LOW"],
    default=["CRITICAL", "HIGH"]
)

scanners = st.multiselect(
    "Select Scanners",
    ["vuln", "secret", "misconfig"],
    default=["vuln", "secret", "misconfig"]
)

if st.button("Analyze Repository"):

    payload = {
        "repo_url": repo_url,
        "severity": ",".join(severity),
        "scanners": ",".join(scanners)
    }

    with st.spinner("Running Agentic Security Analysis..."):

        try:

            response = requests.post(
                "http://127.0.0.1:8000/analyze",
                json=payload,
                timeout=600
            )

            st.write("Status Code:", response.status_code)

            data = response.json()

            # -----------------------------------
            # ERROR HANDLING
            # -----------------------------------

            if "detail" in data:

                st.error(data["detail"])

            # -----------------------------------
            # PRIORITIZED FINDINGS
            # -----------------------------------

            findings = data.get(
                "prioritized_findings",
                []
            )

            if findings:

                st.subheader(
                    "Prioritized Vulnerabilities"
                )

                df = pd.DataFrame(findings)

                st.dataframe(
                    df,
                    use_container_width=True
                )

                # Metrics

                col1, col2, col3 = st.columns(3)

                col1.metric(
                    "Total Findings",
                    len(findings)
                )

                critical_count = len([
                    f for f in findings
                    if f.get("severity")
                    == "CRITICAL"
                ])

                high_count = len([
                    f for f in findings
                    if f.get("severity")
                    == "HIGH"
                ])

                col2.metric(
                    "Critical",
                    critical_count
                )

                col3.metric(
                    "High",
                    high_count
                )

            # -----------------------------------
            # AI REMEDIATION
            # -----------------------------------

            remediation = data.get(
                "remediation_plan",
                []
            )

            if remediation:

                st.subheader(
                    "AI Remediation Analysis"
                )

                for item in remediation:

                    finding = item["finding"]

                    with st.expander(
                        f"{finding.get('cve')} - "
                        f"{finding.get('severity')}"
                    ):

                        st.write(
                            "Package:",
                            finding.get("package")
                        )

                        st.write(
                            "Risk Score:",
                            finding.get(
                                "risk_score"
                            )
                        )

                        st.markdown(
                            item["analysis"]
                        )

            # -----------------------------------
            # WORKFLOW ACTIONS
            # -----------------------------------

            actions = data.get(
                "workflow_actions",
                []
            )

            if actions:

                st.subheader(
                    "Autonomous Workflow Actions"
                )

                st.json(actions)

        except Exception as e:

            st.error(str(e))