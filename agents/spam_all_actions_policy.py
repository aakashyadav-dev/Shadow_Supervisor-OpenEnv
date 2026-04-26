from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


class SpamAllActionsPolicy:
    """
    Reward-hacking baseline.

    This policy tries to brute-force the environment by repeating actions,
    doing checks out of order, and approving after noisy supervision.
    A robust reward function should penalize this behavior.
    """

    name = "spam_all_actions_supervisor"

    def __init__(self):
        self.plan = [
            "assign_ops",
            "assign_ops",                         # repeated
            "audit_ops",
            "audit_ops",                          # repeated
            "select_safe_fix",
            "assign_communication",
            "request_message_revision",
            "request_message_revision",           # repeated
            "reject_or_escalate",                 # often premature/unnecessary
            "assign_policy",
            "audit_policy",
            "approve",
        ]
        self.index = 0

    def reset(self):
        self.index = 0

    def act(self, state: Dict[str, Any]) -> str:
        if self.index >= len(self.plan):
            return "approve"

        action = self.plan[self.index]
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
    policy = SpamAllActionsPolicy()
    result = policy.run_episode(env, scenario_index=0)

    print("Policy:", result["policy"])
    print("Success:", result["success"])
    print("Unsafe approval:", result["unsafe_approval"])
    print("Reward:", result["total_reward"])
    print("Actions:", [s["action"] for s in result["trace"]])
