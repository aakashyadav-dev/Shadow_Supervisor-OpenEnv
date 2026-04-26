import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

"""
Naive Supervisor Policy.

This policy is intentionally unsafe:
- asks only operations and communication,
- does not inspect research,
- does not audit risky operations,
- does not revise stakeholder messaging,
- approves too early.

Expected result:
- low reward,
- high unsafe approval rate,
- useful baseline for demo storytelling.
"""

from typing import Dict, Any


class NaiveSupervisorPolicy:
    name = "naive_supervisor"

    def __init__(self):
        self.plan = [
            "assign_ops",
            "assign_communication",
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
    policy = NaiveSupervisorPolicy()
    result = policy.run_episode(env, scenario_index=0)

    print("Policy:", result["policy"])
    print("Case:", result["case_id"])
    print("Success:", result["success"])
    print("Unsafe approval:", result["unsafe_approval"])
    print("Total reward:", result["total_reward"])

    for step in result["trace"]:
        print(step["action"], step["reward"], step["info"].get("message"))
