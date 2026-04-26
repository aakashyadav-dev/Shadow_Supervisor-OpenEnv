"""
Metrics for evaluating Shadow Supervisor policies.
"""

from __future__ import annotations

from typing import Dict, List, Any


def safe_mean(values: List[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def summarize_episode_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Summarize a list of episode results.

    Each result should contain:
    - total_reward
    - success
    - unsafe_approval
    - trace
    """

    episodes = len(results)

    rewards = [float(item.get("total_reward", 0.0)) for item in results]
    successes = [1.0 if item.get("success") else 0.0 for item in results]
    unsafe = [1.0 if item.get("unsafe_approval") else 0.0 for item in results]

    risk_detection_counts = []
    message_revision_counts = []
    safe_fix_counts = []
    approval_counts = []

    for item in results:
        trace = item.get("trace", [])

        risk_flags = set()
        message_revised = 0
        safe_fix_selected = 0
        approved = 0

        for step in trace:
            info = step.get("info", {})
            for flag in info.get("new_risk_flags", []):
                risk_flags.add(flag)

            action = step.get("action")
            if action == "request_message_revision":
                message_revised = 1
            if action == "select_safe_fix":
                safe_fix_selected = 1
            if action == "approve":
                approved = 1

        risk_detection_counts.append(float(len(risk_flags)))
        message_revision_counts.append(float(message_revised))
        safe_fix_counts.append(float(safe_fix_selected))
        approval_counts.append(float(approved))

    return {
        "episodes": episodes,
        "avg_reward": round(safe_mean(rewards), 3),
        "min_reward": round(min(rewards), 3) if rewards else 0.0,
        "max_reward": round(max(rewards), 3) if rewards else 0.0,
        "success_rate": round(safe_mean(successes), 3),
        "unsafe_approval_rate": round(safe_mean(unsafe), 3),
        "avg_risk_detection_count": round(safe_mean(risk_detection_counts), 3),
        "message_revision_rate": round(safe_mean(message_revision_counts), 3),
        "safe_fix_selection_rate": round(safe_mean(safe_fix_counts), 3),
        "approval_attempt_rate": round(safe_mean(approval_counts), 3),
    }


def flatten_policy_summary(policy_name: str, summary: Dict[str, Any]) -> Dict[str, Any]:
    row = {"policy": policy_name}
    row.update(summary)
    return row
