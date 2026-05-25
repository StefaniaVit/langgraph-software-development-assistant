from typing import List, Dict, Optional, Literal
from typing_extensions import TypedDict


AgentStatus = Literal["pending", "completed", "failed", "skipped"]
FinalAction = Literal["respond", "needs_human_review", "fallback"]


class WorkflowState(TypedDict, total=False):
    task_id: str
    user_request: str
    code_snippet: str
    language: str

    task_type: str
    requires_testing: bool
    requires_documentation: bool
    requires_optimization: bool
    priority: str

    code_analysis: str
    test_recommendations: str
    documentation_draft: str
    optimization_recommendations: str
    quality_review: str

    active_agents: List[str]
    completed_agents: List[str]
    skipped_agents: List[str]
    agent_status: Dict[str, AgentStatus]

    confidence_score: float
    final_action: FinalAction
    escalation_reason: Optional[str]

    retry_counts: Dict[str, int]
    error_log: List[str]
    fallback_used: bool
    telemetry_events: List[str]