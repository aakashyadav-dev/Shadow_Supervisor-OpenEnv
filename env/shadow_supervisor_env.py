import random
from typing import Dict, Any, List, Optional, Tuple

from env.actions import ACTIONS, WORKER_ACTION_TO_KEY
from env.rewards import (
    DEFAULT_REWARD_RULES,
    has_ops_risk,
    has_policy_risk,
    has_message_risk,
    has_research_ops_mismatch,
    is_safe_to_approve,
    missing_required_actions,
    unresolved_risk_summary,
)
from env.scenarios import load_scenarios


class ShadowSupervisorEnv:
    def __init__(
        self,
        scenarios: Optional[List[Dict[str, Any]]] = None,
        scenario_path: Optional[str] = None,
        max_steps: int = 12,
        seed: int = 42,
    ):
        if scenarios is not None:
            self.scenarios = scenarios
        elif scenario_path is not None:
            self.scenarios = load_scenarios(scenario_path)
        else:
            self.scenarios = load_scenarios("data/scenarios_train.json")

        if not self.scenarios:
            raise ValueError("ShadowSupervisorEnv requires at least one scenario.")

        self.max_steps = max_steps
        self.random = random.Random(seed)

        self.current_scenario = {}
        self.visible_worker_outputs = {}
        self.completed_actions = []
        self.risk_flags = []
        self.resolved_risks = []
        self.step_count = 0
        self.total_reward = 0.0
        self.done = False
        self.success = False
        self.unsafe_approval = False
        self.episode_trace = []

    def reset(self, seed: Optional[int] = None, scenario_index: Optional[int] = None):
        if seed is not None:
            self.random.seed(seed)

        if scenario_index is None:
            scenario_index = self.random.randrange(len(self.scenarios))

        self.current_scenario = self.scenarios[scenario_index]

        self.visible_worker_outputs = {
            "research_agent": None,
            "ops_agent": None,
            "policy_agent": None,
            "communication_agent": None,
        }

        self.completed_actions = []
        self.risk_flags = []
        self.resolved_risks = []
        self.step_count = 0
        self.total_reward = 0.0
        self.done = False
        self.success = False
        self.unsafe_approval = False
        self.episode_trace = []

        return self.state()

    def step(self, action: str) -> Tuple[Dict[str, Any], float, bool, Dict[str, Any]]:
        if self.done:
            return self.state(), 0.0, True, {
                "warning": "Episode is already done. Call reset() before stepping again.",
                "action": action,
            }

        self.step_count += 1

        if action not in ACTIONS:
            reward = float(DEFAULT_REWARD_RULES["invalid_action"])
            info = {
                "action": action,
                "valid": False,
                "reason": "invalid_action",
                "message": f"Invalid action: {action}",
            }
            self.total_reward += reward
            self._record_trace(action, reward, info)
            return self.state(), reward, self.done, info

        reward, info = self._apply_action(action)

        # Small efficiency cost: safe supervisors should resolve risks without
        # blindly spamming unnecessary actions.
        if action != "approve":
            step_cost = float(DEFAULT_REWARD_RULES.get("step_cost", 0.0))
            reward += step_cost
            info["step_cost"] = step_cost

        if self.step_count >= self.max_steps and not self.done:
            reward += DEFAULT_REWARD_RULES["too_many_steps"]
            self.done = True
            info["episode_end_reason"] = "max_steps_reached"

        self.total_reward += reward
        self._record_trace(action, reward, info)

        return self.state(), float(reward), self.done, info

    def state(self) -> Dict[str, Any]:
        return {
            "case_id": self.current_scenario.get("case_id"),
            "domain": self.current_scenario.get("domain"),
            "incident": self.current_scenario.get("incident"),
            "source_notes": self.current_scenario.get("source_notes", {}),
            "visible_worker_outputs": dict(self.visible_worker_outputs),
            "completed_actions": list(self.completed_actions),
            "risk_flags": list(self.risk_flags),
            "resolved_risks": list(self.resolved_risks),
            "available_actions": list(ACTIONS),
            "step_count": self.step_count,
            "max_steps": self.max_steps,
            "total_reward": round(self.total_reward, 3),
            "done": self.done,
            "success": self.success,
            "unsafe_approval": self.unsafe_approval,
        }

    def render_trace(self):
        return list(self.episode_trace)

    def _apply_action(self, action: str):
        info = {
            "action": action,
            "valid": True,
            "new_risk_flags": [],
            "new_resolved_risks": [],
            "message": "",
        }

        if action in self.completed_actions:
            reward = float(DEFAULT_REWARD_RULES["repeated_action"])
            info["reason"] = "repeated_action"
            info["message"] = f"Action '{action}' was already completed."
            return reward, info

        self.completed_actions.append(action)

        if action in WORKER_ACTION_TO_KEY:
            return self._assign_worker(action, info)

        if action == "audit_ops":
            return self._audit_ops(info)

        if action == "audit_policy":
            return self._audit_policy(info)

        if action == "cross_check_research_and_ops":
            return self._cross_check_research_and_ops(info)

        if action == "cross_check_research_and_communication":
            return self._cross_check_research_and_communication(info)

        if action == "select_safe_fix":
            return self._select_safe_fix(info)

        if action == "request_message_revision":
            return self._request_message_revision(info)

        if action == "reject_or_escalate":
            return self._reject_or_escalate(info)

        if action == "approve":
            return self._approve(info)

        return 0.0, info

    def _assign_worker(self, action, info):
        worker_key = WORKER_ACTION_TO_KEY[action]
        worker_outputs = self.current_scenario.get("worker_outputs", {})
        self.visible_worker_outputs[worker_key] = worker_outputs.get(worker_key)

        reward = float(DEFAULT_REWARD_RULES.get(action, 1))
        info["worker"] = worker_key
        info["message"] = f"{worker_key} output is now visible."

        return reward, info

    def _audit_ops(self, info):
        if self.visible_worker_outputs.get("ops_agent") is None:
            info["reason"] = "missing_ops_output"
            info["message"] = "Cannot audit ops before assigning ops agent."
            return float(DEFAULT_REWARD_RULES["missing_prerequisite"]), info

        if has_ops_risk(self.current_scenario):
            self._add_risk_flag("ops_risk_detected", info)
            reward = float(DEFAULT_REWARD_RULES["audit_ops"])
            info["message"] = "Operations risk detected."
        else:
            reward = float(DEFAULT_REWARD_RULES["irrelevant_action"])
            info["message"] = "No operations risk was present."

        return reward, info

    def _audit_policy(self, info):
        if self.visible_worker_outputs.get("policy_agent") is None:
            info["reason"] = "missing_policy_output"
            info["message"] = "Cannot audit policy before assigning policy agent."
            return float(DEFAULT_REWARD_RULES["missing_prerequisite"]), info

        if has_policy_risk(self.current_scenario):
            self._add_risk_flag("policy_risk_detected", info)
            self._add_resolved_risk("policy_audited", info)
            reward = float(DEFAULT_REWARD_RULES["audit_policy"])
            info["message"] = "Policy risk detected and audited."
        else:
            reward = float(DEFAULT_REWARD_RULES["irrelevant_action"])
            info["message"] = "No policy risk was present."

        return reward, info

    def _cross_check_research_and_ops(self, info):
        if (
            self.visible_worker_outputs.get("research_agent") is None
            or self.visible_worker_outputs.get("ops_agent") is None
        ):
            info["reason"] = "missing_research_or_ops_output"
            info["message"] = "Need research and ops outputs before cross-checking."
            return float(DEFAULT_REWARD_RULES["missing_prerequisite"]), info

        if has_research_ops_mismatch(self.current_scenario) or has_ops_risk(self.current_scenario):
            self._add_risk_flag("research_ops_mismatch_detected", info)
            self._add_resolved_risk("research_ops_cross_checked", info)
            reward = float(DEFAULT_REWARD_RULES["cross_check_research_and_ops"])
            info["message"] = "Research and operations outputs were cross-checked."
        else:
            reward = float(DEFAULT_REWARD_RULES["irrelevant_action"])
            info["message"] = "No meaningful research/ops mismatch was present."

        return reward, info

    def _cross_check_research_and_communication(self, info):
        if (
            self.visible_worker_outputs.get("research_agent") is None
            or self.visible_worker_outputs.get("communication_agent") is None
        ):
            info["reason"] = "missing_research_or_communication_output"
            info["message"] = "Need research and communication outputs before cross-checking."
            return float(DEFAULT_REWARD_RULES["missing_prerequisite"]), info

        if has_message_risk(self.current_scenario):
            self._add_risk_flag("message_risk_detected", info)
            reward = float(DEFAULT_REWARD_RULES["cross_check_research_and_communication"])
            info["message"] = "Stakeholder-message risk detected."
        else:
            reward = float(DEFAULT_REWARD_RULES["irrelevant_action"])
            info["message"] = "No stakeholder-message risk was present."

        return reward, info

    def _select_safe_fix(self, info):
        if not has_ops_risk(self.current_scenario):
            info["message"] = "No unsafe operations recommendation needed fixing."
            return float(DEFAULT_REWARD_RULES["irrelevant_action"]), info

        safe_outputs = self.current_scenario.get("safe_outputs", {})
        safe_ops = safe_outputs.get("ops_agent")

        if safe_ops:
            self.visible_worker_outputs["ops_agent"] = safe_ops

        self._add_resolved_risk("safe_fix_selected", info)

        reward = float(DEFAULT_REWARD_RULES["select_safe_fix"])
        info["message"] = "Safe operations fix selected."

        return reward, info

    def _request_message_revision(self, info):
        if not has_message_risk(self.current_scenario):
            info["message"] = "No unsafe stakeholder message needed revision."
            return float(DEFAULT_REWARD_RULES["irrelevant_action"]), info

        safe_outputs = self.current_scenario.get("safe_outputs", {})
        safe_message = safe_outputs.get("communication_agent")

        if safe_message:
            self.visible_worker_outputs["communication_agent"] = safe_message

        self._add_resolved_risk("message_revised", info)

        reward = float(DEFAULT_REWARD_RULES["request_message_revision"])
        info["message"] = "Stakeholder message revised."

        return reward, info

    def _reject_or_escalate(self, info):
        if has_policy_risk(self.current_scenario):
            self._add_risk_flag("policy_escalation_required", info)
            self._add_resolved_risk("policy_escalated", info)
            reward = float(DEFAULT_REWARD_RULES["reject_or_escalate"])
            info["message"] = "Workflow escalated or rejected for required review."
        else:
            reward = float(DEFAULT_REWARD_RULES["unnecessary_escalation"])
            info["message"] = "Escalation was unnecessary."

        return reward, info

    def _approve(self, info):
        self.done = True

        missing = missing_required_actions(self.current_scenario, self.completed_actions)
        unresolved = unresolved_risk_summary(self.current_scenario, self.resolved_risks)

        safe = is_safe_to_approve(
            self.current_scenario,
            self.completed_actions,
            self.resolved_risks,
        )

        info["missing_required_actions"] = missing
        info["unresolved_risks"] = unresolved

        if safe:
            reward = float(DEFAULT_REWARD_RULES["approve_after_resolution"])
            self.success = True
            self.unsafe_approval = False
            info["message"] = "Approved safely after all required checks."
            info["episode_end_reason"] = "safe_approval"
        else:
            reward = float(DEFAULT_REWARD_RULES["unsafe_approval"])
            self.success = False
            self.unsafe_approval = True
            info["message"] = "Unsafe approval: hidden failures were not fully resolved."
            info["episode_end_reason"] = "unsafe_approval"

            if unresolved.get("message_unresolved"):
                reward += float(DEFAULT_REWARD_RULES["unsafe_message"])
                info["message_penalty"] = "Unsafe stakeholder message remained unresolved."

        return reward, info

    def _add_risk_flag(self, flag, info):
        if flag not in self.risk_flags:
            self.risk_flags.append(flag)
            info["new_risk_flags"].append(flag)

    def _add_resolved_risk(self, risk, info):
        if risk not in self.resolved_risks:
            self.resolved_risks.append(risk)
            info["new_resolved_risks"].append(risk)

    def _record_trace(self, action, reward, info):
        self.episode_trace.append(
            {
                "step": self.step_count,
                "action": action,
                "reward": reward,
                "total_reward_after_step": round(self.total_reward + reward, 3),
                "risk_flags": list(self.risk_flags),
                "resolved_risks": list(self.resolved_risks),
                "done": self.done,
                "success": self.success,
                "unsafe_approval": self.unsafe_approval,
                "info": dict(info),
            }
        )