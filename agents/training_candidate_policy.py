import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

"""
Training Candidate Supervisor Policy.

This policy is better than the naive policy:
- gathers research, operations, and policy,
- audits operations,
- cross-checks research and operations,
- selects a safe technical fix.

But it is still imperfect:
- often forgets to inspect or revise stakeholder communication,
- may approve while message risk remains unresolved.

Expected result:
- better reward than naive,
- partial success,
- still clear failure cases for training improvement.
"""

from typing import Dict, Any


class TrainingCandidatePolicy:
    name = "training_candidate_supervisor"

    def __init__(self):
        self.plan = [
            "assign_research",
            "assign_ops",
            "assign_policy",
            "audit_ops",
            "audit_policy",
            "cross_check_research_and_ops",
            "select_safe_fix",
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
    policy = TrainingCandidatePolicy()
    result = policy.run_episode(env, scenario_index=0)

    print("Policy:", result["policy"])
    print("Case:", result["case_id"])
    print("Success:", result["success"])
    print("Unsafe approval:", result["unsafe_approval"])
    print("Total reward:", result["total_reward"])

    for step in result["trace"]:
        print(step["action"], step["reward"], step["info"].get("message"))
