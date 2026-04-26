"""
Action and risk definitions for Shadow Supervisor.
"""

ACTIONS = [
    "assign_research",
    "assign_ops",
    "assign_policy",
    "assign_communication",
    "audit_ops",
    "audit_policy",
    "cross_check_research_and_ops",
    "cross_check_research_and_communication",
    "select_safe_fix",
    "request_message_revision",
    "reject_or_escalate",
    "approve",
]

ACTION_TO_ID = {action: idx for idx, action in enumerate(ACTIONS)}
ID_TO_ACTION = {idx: action for action, idx in ACTION_TO_ID.items()}

WORKER_ACTION_TO_KEY = {
    "assign_research": "research_agent",
    "assign_ops": "ops_agent",
    "assign_policy": "policy_agent",
    "assign_communication": "communication_agent",
}

OPS_RISK_FAILURES = {
    "unsafe_ops_recommendation",
    "security_patch_risk",
    "data_loss_risk",
    "rollback_required",
}

POLICY_RISK_FAILURES = {
    "missing_policy_escalation",
    "compliance_review_missing",
    "security_patch_risk",
}

MESSAGE_RISK_FAILURES = {
    "overconfident_stakeholder_message",
    "customer_impact_understated",
    "premature_resolution_claim",
}

RESEARCH_OPS_MISMATCH_FAILURES = {
    "research_ops_mismatch",
    "unsafe_ops_recommendation",
    "rollback_required",
}
