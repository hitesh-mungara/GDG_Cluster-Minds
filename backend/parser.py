import json
import os


def parse_reports(report_paths):

    findings = []

    # -----------------------------------
    # TRIVY PARSING
    # -----------------------------------

    trivy_file = report_paths["trivy"]

    if os.path.exists(trivy_file):

        with open(trivy_file) as f:

            content = f.read().strip()

            if content:

                trivy_data = json.loads(content)

                for result in trivy_data.get(
                    "Results",
                    []
                ):

                    # -------------------------
                    # Vulnerabilities
                    # -------------------------

                    vulns = result.get(
                        "Vulnerabilities",
                        []
                    )

                    for vuln in vulns:

                        findings.append({
                            "scanner": "trivy",
                            "type": "cve",
                            "title": vuln.get("Title"),
                            "cve": vuln.get(
                                "VulnerabilityID"
                            ),
                            "severity": vuln.get(
                                "Severity"
                            ),
                            "package": vuln.get(
                                "PkgName"
                            ),
                            "fixed_version": vuln.get(
                                "FixedVersion"
                            )
                        })

                    # -------------------------
                    # Misconfigurations
                    # -------------------------

                    misconfigs = result.get(
                        "Misconfigurations",
                        []
                    )

                    for misconfig in misconfigs:

                        findings.append({
                            "scanner": "trivy",
                            "type": "misconfiguration",
                            "title": misconfig.get(
                                "Title"
                            ),
                            "severity": misconfig.get(
                                "Severity"
                            ),
                            "message": misconfig.get(
                                "Description"
                            )
                        })

    # -----------------------------------
    # GITLEAKS PARSING
    # -----------------------------------

    gitleaks_file = report_paths["gitleaks"]

    if os.path.exists(gitleaks_file):

        with open(gitleaks_file) as f:

            content = f.read().strip()

            if content:

                gitleaks_data = json.loads(content)

                for leak in gitleaks_data:

                    findings.append({
                        "scanner": "gitleaks",
                        "type": "secret",
                        "title": leak.get(
                            "Description"
                        ),
                        "severity": "HIGH",
                        "file": leak.get("File"),
                        "secret_type": leak.get(
                            "RuleID"
                        )
                    })

    # -----------------------------------
    # SEMGREP PARSING
    # -----------------------------------

    semgrep_file = report_paths["semgrep"]

    if os.path.exists(semgrep_file):

        with open(semgrep_file) as f:

            content = f.read().strip()

            if content:

                semgrep_data = json.loads(content)

                for result in semgrep_data.get(
                    "results",
                    []
                ):

                    findings.append({
                        "scanner": "semgrep",
                        "type": "sast",
                        "title": result.get(
                            "check_id"
                        ),
                        "severity": result.get(
                            "extra",
                            {}
                        ).get(
                            "severity",
                            "MEDIUM"
                        ),
                        "message": result.get(
                            "extra",
                            {}
                        ).get(
                            "message"
                        ),
                        "file": result.get("path")
                    })

    return findings