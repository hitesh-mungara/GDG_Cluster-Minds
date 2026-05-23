from langgraph.graph import (
    StateGraph
)

from agents.state import (
    AgentState
)

from agents.parse_agent import (
    parse_agent
)

from agents.intel_agent import (
    intel_agent
)

from agents.risk_agent import (
    risk_agent
)

from agents.remediation_agent import (
    remediation_agent
)

from agents.fix_agent import (
    fix_agent
)

from agents.pr_decision_agent import (
    pr_decision_agent
)

from agents.pr_agent import (
    pr_agent
)

from agents.workflow_agent import (
    workflow_agent
)

# =====================================================
# CREATE GRAPH
# =====================================================

graph = StateGraph(
    AgentState
)

# =====================================================
# ADD NODES
# =====================================================

graph.add_node(
    "parse_agent",
    parse_agent
)

graph.add_node(
    "intel_agent",
    intel_agent
)

graph.add_node(
    "risk_agent",
    risk_agent
)

graph.add_node(
    "remediation_agent",
    remediation_agent
)

# Commented out agents - stopping at remediation (summarizing) agent
# graph.add_node(
#     "fix_agent",
#     fix_agent
# )
#
# graph.add_node(
#     "pr_decision_agent",
#     pr_decision_agent
# )
#
# graph.add_node(
#     "pr_agent",
#     pr_agent
# )
#
# graph.add_node(
#     "workflow_agent",
#     workflow_agent
# )

# =====================================================
# ENTRY POINT
# =====================================================

graph.set_entry_point(
    "parse_agent"
)

# =====================================================
# EDGES / FLOW - STOPPING AT REMEDIATION AGENT
# =====================================================

graph.add_edge(
    "parse_agent",
    "intel_agent"
)

graph.add_edge(
    "intel_agent",
    "risk_agent"
)

graph.add_edge(
    "risk_agent",
    "remediation_agent"
)

# Commented out remaining edges - stopping at remediation agent
# graph.add_edge(
#     "remediation_agent",
#     "fix_agent"
# )
#
# graph.add_edge(
#     "fix_agent",
#     "pr_decision_agent"
# )
#
# graph.add_edge(
#     "pr_decision_agent",
#     "pr_agent"
# )
#
# graph.add_edge(
#     "pr_agent",
#     "workflow_agent"
# )

# =====================================================
# FINISH POINT - NOW AT REMEDIATION AGENT
# =====================================================

graph.set_finish_point(
    "remediation_agent"
)

# =====================================================
# COMPILE GRAPH
# =====================================================

app = graph.compile()

# =====================================================
# RUN PIPELINE
# =====================================================

def run_pipeline(
    scan_data,
    repo_url,
    repo_path
):

    return app.invoke({

        "scan_data":
        scan_data,

        "repo_url":
        repo_url,

        "repo_path":
        repo_path
    })