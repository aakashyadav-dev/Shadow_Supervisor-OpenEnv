from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


class RLEnvTrainedPolicy:
    name = "rl_trained_supervisor"

    def __init__(self, policy_path: str = "outputs/rl_policy.json"):
        self.policy_path = ROOT_DIR / policy_path
        self.index = 0
        self.action_sequence: List[str] = [
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

        if self.policy_path.exists():
            data = json.loads(self.policy_path.read_text(encoding="utf-8"))
            self.action_sequence = data.get("action_sequence", self.action_sequence)

    def reset(self):
        self.index = 0

    def act(self, state: Dict[str, Any]) -> str:
        if self.index >= len(self.action_sequence):
            return "approve"

        action = self.action_sequence[self.index]
        self.index += 1
        return action

    def run_episode(self, env, scenario_index=None, seed=None):
        self.reset()
        state = env.reset(seed=seed, scenario_index=scenario_index)
        done = False
        trace = []

        while not done:
            action = self.act(state)
            next_state, reward, done, info = env.step(action)

            trace.append(
                {
                    "action": action,
                    "reward": reward,
                    "done": done,
                    "info": info,
                    "state_after": next_state,
                }
            )

            state = next_state

        return {
            "policy": self.name,
            "case_id": state.get("case_id"),
            "success": state.get("success"),
            "unsafe_approval": state.get("unsafe_approval"),
            "total_reward": state.get("total_reward"),
            "trace": trace,
        }


if __name__ == "__main__":
    from env.shadow_supervisor_env import ShadowSupervisorEnv

    env = ShadowSupervisorEnv(scenario_path="data/scenarios_eval.json")
    policy = RLEnvTrainedPolicy()
    result = policy.run_episode(env, scenario_index=0)

    print("Policy:", result["policy"])
    print("Success:", result["success"])
    print("Unsafe approval:", result["unsafe_approval"])
    print("Reward:", result["total_reward"])
    print("Actions:", [s["action"] for s in result["trace"]])