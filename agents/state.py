from typing import TypedDict


class AgentState(TypedDict):

    scan_data: dict

    findings: list

    enriched_findings: list

    prioritized_findings: list

    remediation_plan: list

    workflow_actions: list

    generated_fixes: list

    pr_response: dict

    repo_url: str

    repo_path: str

    approve_pr: bool