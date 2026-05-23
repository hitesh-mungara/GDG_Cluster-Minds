import json
import time
from typing import Any, Dict, List

import pandas as pd
import plotly.express as px
import requests
import streamlit as st


DEFAULT_API_BASE_URL = "https://trivy-api-109127597395.asia-south1.run.app"


st.set_page_config(
    page_title="Trivy Repo Scanner",
    page_icon="🛡️",
    layout="wide",
)


def call_scan_api(
    api_base_url: str,
    repo_url: str,
    branch: str | None,
    severity: str,
    scanners: str,
    timeout_seconds: int = 3600,
) -> Dict[str, Any]:
    url = f"{api_base_url.rstrip('/')}/scan"

    payload = {
        "repo_url": repo_url,
        "severity": severity,
        "scanners": scanners,
    }

    if branch:
        payload["branch"] = branch

    response = requests.post(
        url,
        json=payload,
        timeout=timeout_seconds,
    )

    if not response.ok:
        try:
            error_body = response.json()
        except Exception:
            error_body = response.text

        raise RuntimeError(
            f"API call failed with status {response.status_code}: {error_body}"
        )

    return response.json()


def extract_vulnerabilities(scan_response: Dict[str, Any]) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []

    trivy_result = scan_response.get("trivy_result", {})
    results = trivy_result.get("Results", []) or []

    for result in results:
        target = result.get("Target")
        result_type = result.get("Type")

        for vuln in result.get("Vulnerabilities") or []:
            rows.append(
                {
                    "Target": target,
                    "Type": result_type,
                    "Vulnerability ID": vuln.get("VulnerabilityID"),
                    "Package": vuln.get("PkgName"),
                    "Installed Version": vuln.get("InstalledVersion"),
                    "Fixed Version": vuln.get("FixedVersion"),
                    "Severity": vuln.get("Severity"),
                    "Title": vuln.get("Title"),
                    "Primary URL": vuln.get("PrimaryURL"),
                }
            )

    return pd.DataFrame(rows)


def extract_misconfigurations(scan_response: Dict[str, Any]) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []

    trivy_result = scan_response.get("trivy_result", {})
    results = trivy_result.get("Results", []) or []

    for result in results:
        target = result.get("Target")

        for misconfig in result.get("Misconfigurations") or []:
            rows.append(
                {
                    "Target": target,
                    "ID": misconfig.get("ID"),
                    "Title": misconfig.get("Title"),
                    "Severity": misconfig.get("Severity"),
                    "Status": misconfig.get("Status"),
                    "Message": misconfig.get("Message"),
                }
            )

    return pd.DataFrame(rows)


def extract_secrets(scan_response: Dict[str, Any]) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []

    trivy_result = scan_response.get("trivy_result", {})
    results = trivy_result.get("Results", []) or []

    for result in results:
        target = result.get("Target")

        for secret in result.get("Secrets") or []:
            rows.append(
                {
                    "Target": target,
                    "Rule ID": secret.get("RuleID"),
                    "Category": secret.get("Category"),
                    "Severity": secret.get("Severity"),
                    "Title": secret.get("Title"),
                    "Start Line": secret.get("StartLine"),
                    "End Line": secret.get("EndLine"),
                }
            )

    return pd.DataFrame(rows)


def show_summary_cards(summary: Dict[str, Any]) -> None:
    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Total Vulnerabilities",
        summary.get("total_vulnerabilities", 0),
    )
    c2.metric(
        "Total Misconfigurations",
        summary.get("total_misconfigurations", 0),
    )
    c3.metric(
        "Total Secrets",
        summary.get("total_secrets", 0),
    )


def show_severity_chart(summary: Dict[str, Any]) -> None:
    severity_counts = summary.get("vulnerabilities_by_severity", {}) or {}

    if not severity_counts:
        st.info("No severity data found.")
        return

    df = pd.DataFrame(
        [
            {"Severity": severity, "Count": count}
            for severity, count in severity_counts.items()
            if count is not None
        ]
    )

    if df.empty:
        st.info("No vulnerability severity counts to show.")
        return

    fig = px.bar(
        df,
        x="Severity",
        y="Count",
        title="Vulnerabilities by Severity",
        text="Count",
    )
    fig.update_layout(xaxis_title="Severity", yaxis_title="Count")
    st.plotly_chart(fig, use_container_width=True)


def show_package_chart(vuln_df: pd.DataFrame) -> None:
    if vuln_df.empty or "Package" not in vuln_df.columns:
        st.info("No package vulnerability data found.")
        return

    package_df = (
        vuln_df.groupby("Package", dropna=False)
        .size()
        .reset_index(name="Count")
        .sort_values("Count", ascending=False)
        .head(15)
    )

    fig = px.bar(
        package_df,
        x="Count",
        y="Package",
        orientation="h",
        title="Top Vulnerable Packages",
        text="Count",
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig, use_container_width=True)


def show_target_chart(vuln_df: pd.DataFrame) -> None:
    if vuln_df.empty or "Target" not in vuln_df.columns:
        st.info("No target vulnerability data found.")
        return

    target_df = (
        vuln_df.groupby("Target", dropna=False)
        .size()
        .reset_index(name="Count")
        .sort_values("Count", ascending=False)
        .head(15)
    )

    fig = px.bar(
        target_df,
        x="Count",
        y="Target",
        orientation="h",
        title="Top Vulnerable Targets / Files",
        text="Count",
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig, use_container_width=True)


st.title("🛡️ Trivy GitHub Repository Scanner")
st.caption("Frontend for your Cloud Run FastAPI API. The backend triggers Cloud Build and runs Trivy.")

with st.sidebar:
    st.header("Backend")
    api_base_url = st.text_input(
        "API Base URL",
        value=DEFAULT_API_BASE_URL,
    )

    st.divider()

    st.header("Scan Settings")

    repo_url = st.text_input(
        "GitHub Repo URL",
        value="https://github.com/WebGoat/WebGoat.git",
    )

    branch = st.text_input(
        "Branch Optional",
        value="",
        placeholder="main",
    )

    st.subheader("Severity")
    sev_critical = st.checkbox("CRITICAL", value=True)
    sev_high = st.checkbox("HIGH", value=True)
    sev_medium = st.checkbox("MEDIUM", value=False)
    sev_low = st.checkbox("LOW", value=False)

    selected_severities = []
    if sev_critical:
        selected_severities.append("CRITICAL")
    if sev_high:
        selected_severities.append("HIGH")
    if sev_medium:
        selected_severities.append("MEDIUM")
    if sev_low:
        selected_severities.append("LOW")

    st.subheader("Scanners")
    scan_vuln = st.checkbox("vuln", value=True)
    scan_secret = st.checkbox("secret", value=True)
    scan_misconfig = st.checkbox("misconfig", value=True)

    selected_scanners = []
    if scan_vuln:
        selected_scanners.append("vuln")
    if scan_secret:
        selected_scanners.append("secret")
    if scan_misconfig:
        selected_scanners.append("misconfig")

    run_scan = st.button("Run Trivy Scan", type="primary")


if "scan_response" not in st.session_state:
    st.session_state.scan_response = None

if run_scan:
    if not repo_url:
        st.error("Please enter a GitHub repository URL.")
        st.stop()

    if not selected_severities:
        st.error("Please select at least one severity.")
        st.stop()

    if not selected_scanners:
        st.error("Please select at least one scanner.")
        st.stop()

    severity = ",".join(selected_severities)
    scanners = ",".join(selected_scanners)

    with st.spinner("Cloud Build scan is running. This may take a few minutes..."):
        start_time = time.time()

        try:
            scan_response = call_scan_api(
                api_base_url=api_base_url,
                repo_url=repo_url,
                branch=branch.strip() or None,
                severity=severity,
                scanners=scanners,
            )

            elapsed = round(time.time() - start_time, 2)
            st.session_state.scan_response = scan_response

            st.success(f"Scan completed in {elapsed} seconds.")

        except Exception as e:
            st.error(str(e))
            st.stop()


scan_response = st.session_state.scan_response

if scan_response:
    summary = scan_response.get("summary", {})

    st.subheader("Scan Metadata")

    m1, m2 = st.columns(2)

    with m1:
        st.write("**Scan ID:**", scan_response.get("scan_id"))
        st.write("**Build ID:**", scan_response.get("build_id"))
        st.write("**Repo URL:**", scan_response.get("repo_url"))

    with m2:
        st.write("**Branch:**", scan_response.get("branch"))
        st.write("**Result GCS URI:**", scan_response.get("result_gcs_uri"))

    st.divider()

    st.subheader("Summary")
    show_summary_cards(summary)

    st.divider()

    vuln_df = extract_vulnerabilities(scan_response)
    misconfig_df = extract_misconfigurations(scan_response)
    secret_df = extract_secrets(scan_response)

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        show_severity_chart(summary)

    with chart_col2:
        show_package_chart(vuln_df)

    show_target_chart(vuln_df)

    st.divider()

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "Vulnerabilities",
            "Misconfigurations",
            "Secrets",
            "Raw JSON",
        ]
    )

    with tab1:
        st.subheader("Vulnerabilities")

        if vuln_df.empty:
            st.info("No vulnerabilities found for the selected filters.")
        else:
            st.dataframe(vuln_df, use_container_width=True)

            csv = vuln_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download Vulnerabilities CSV",
                data=csv,
                file_name="trivy-vulnerabilities.csv",
                mime="text/csv",
            )

    with tab2:
        st.subheader("Misconfigurations")

        if misconfig_df.empty:
            st.info("No misconfigurations found for the selected filters.")
        else:
            st.dataframe(misconfig_df, use_container_width=True)

    with tab3:
        st.subheader("Secrets")

        if secret_df.empty:
            st.info("No secrets found for the selected filters.")
        else:
            st.dataframe(secret_df, use_container_width=True)

    with tab4:
        st.subheader("Raw API Response")
        st.json(scan_response)

        st.download_button(
            "Download Raw JSON",
            data=json.dumps(scan_response, indent=2),
            file_name="trivy-scan-response.json",
            mime="application/json",
        )

else:
    st.info("Enter a GitHub repo URL in the sidebar and click Run Trivy Scan.")