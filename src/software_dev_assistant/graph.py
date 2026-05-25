from langgraph.graph import StateGraph, END
from software_dev_assistant.state import WorkflowState


def coordinator_node(state: WorkflowState) -> WorkflowState:
    request = state.get("user_request", "").lower()

    requires_testing = any(word in request for word in ["test", "bug", "failure", "error"])
    requires_documentation = any(word in request for word in ["document", "doc", "explain", "readme"])
    requires_optimization = any(word in request for word in ["optimize", "performance", "refactor", "speed"])

    if not any([requires_testing, requires_documentation, requires_optimization]):
        requires_testing = True
        requires_documentation = True

    active_agents = ["code_analysis"]
    if requires_testing:
        active_agents.append("test_generation")
    if requires_documentation:
        active_agents.append("documentation")
    if requires_optimization:
        active_agents.append("optimization")

    agent_status = state.get("agent_status", {})
    for agent in active_agents:
        agent_status[agent] = "pending"

    telemetry = state.get("telemetry_events", [])
    telemetry.append("Coordinator planned workflow")

    return {
        **state,
        "task_type": "software_development_assistant",
        "requires_testing": requires_testing,
        "requires_documentation": requires_documentation,
        "requires_optimization": requires_optimization,
        "priority": "normal",
        "active_agents": active_agents,
        "agent_status": agent_status,
        "telemetry_events": telemetry,
    }


def code_analysis_node(state: WorkflowState) -> WorkflowState:
    code = state.get("code_snippet", "")
    analysis = (
        "The code appears to need structured review for readability, possible edge cases, "
        "and maintainability improvements."
        if code
        else "No code snippet provided. Analysis is based only on the user request."
    )

    agent_status = state.get("agent_status", {})
    agent_status["code_analysis"] = "completed"

    completed = state.get("completed_agents", [])
    completed.append("code_analysis")

    telemetry = state.get("telemetry_events", [])
    telemetry.append("Code analysis completed")

    return {
        **state,
        "code_analysis": analysis,
        "agent_status": agent_status,
        "completed_agents": completed,
        "telemetry_events": telemetry,
    }


def test_generation_node(state: WorkflowState) -> WorkflowState:
    recommendations = (
        "Suggested tests: nominal case, invalid input handling, boundary cases, "
        "and regression tests for known failure modes."
    )

    agent_status = state.get("agent_status", {})
    agent_status["test_generation"] = "completed"

    completed = state.get("completed_agents", [])
    completed.append("test_generation")

    telemetry = state.get("telemetry_events", [])
    telemetry.append("Test generation completed")

    return {
        **state,
        "test_recommendations": recommendations,
        "agent_status": agent_status,
        "completed_agents": completed,
        "telemetry_events": telemetry,
    }


def documentation_node(state: WorkflowState) -> WorkflowState:
    draft = (
        "Documentation draft: describe purpose, inputs, outputs, assumptions, "
        "usage example, and known limitations."
    )

    agent_status = state.get("agent_status", {})
    agent_status["documentation"] = "completed"

    completed = state.get("completed_agents", [])
    completed.append("documentation")

    telemetry = state.get("telemetry_events", [])
    telemetry.append("Documentation generation completed")

    return {
        **state,
        "documentation_draft": draft,
        "agent_status": agent_status,
        "completed_agents": completed,
        "telemetry_events": telemetry,
    }


def optimization_node(state: WorkflowState) -> WorkflowState:
    recommendations = (
        "Optimization recommendations: simplify control flow, isolate reusable functions, "
        "and profile bottlenecks before changing algorithmic structure."
    )

    agent_status = state.get("agent_status", {})
    agent_status["optimization"] = "completed"

    completed = state.get("completed_agents", [])
    completed.append("optimization")

    telemetry = state.get("telemetry_events", [])
    telemetry.append("Optimization review completed")

    return {
        **state,
        "optimization_recommendations": recommendations,
        "agent_status": agent_status,
        "completed_agents": completed,
        "telemetry_events": telemetry,
    }


def quality_review_node(state: WorkflowState) -> WorkflowState:
    errors = state.get("error_log", [])
    completed = state.get("completed_agents", [])
    active = state.get("active_agents", [])

    confidence = 0.9 if len(completed) >= max(2, len(active)) else 0.6

    if errors:
        final_action = "fallback"
        review = "Errors detected during workflow execution. Fallback response recommended."
        escalation_reason = "Errors present in error_log."
    elif confidence < 0.75:
        final_action = "needs_human_review"
        review = "Low confidence in workflow completeness. Human review recommended."
        escalation_reason = "Low confidence score."
    else:
        final_action = "respond"
        review = "Outputs are sufficiently complete and coherent for response delivery."
        escalation_reason = None

    telemetry = state.get("telemetry_events", [])
    telemetry.append("Quality review completed")

    return {
        **state,
        "quality_review": review,
        "confidence_score": confidence,
        "final_action": final_action,
        "escalation_reason": escalation_reason,
        "telemetry_events": telemetry,
    }


def route_after_coordinator(state: WorkflowState) -> str:
    return "code_analysis"


def route_after_code_analysis(state: WorkflowState) -> str:
    if state.get("requires_testing"):
        return "test_generation"
    if state.get("requires_documentation"):
        return "documentation"
    if state.get("requires_optimization"):
        return "optimization"
    return "quality_review"


def route_after_test_generation(state: WorkflowState) -> str:
    if state.get("requires_documentation"):
        return "documentation"
    if state.get("requires_optimization"):
        return "optimization"
    return "quality_review"


def route_after_documentation(state: WorkflowState) -> str:
    if state.get("requires_optimization"):
        return "optimization"
    return "quality_review"


def build_graph():
    graph = StateGraph(WorkflowState)

    graph.add_node("coordinator", coordinator_node)
    graph.add_node("code_analysis", code_analysis_node)
    graph.add_node("test_generation", test_generation_node)
    graph.add_node("documentation", documentation_node)
    graph.add_node("optimization", optimization_node)
    graph.add_node("quality_review", quality_review_node)

    graph.set_entry_point("coordinator")

    graph.add_conditional_edges("coordinator", route_after_coordinator)
    graph.add_conditional_edges("code_analysis", route_after_code_analysis)
    graph.add_conditional_edges("test_generation", route_after_test_generation)
    graph.add_conditional_edges("documentation", route_after_documentation)

    graph.add_edge("optimization", "quality_review")
    graph.add_edge("quality_review", END)

    return graph.compile()