import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

"""
Cautious Supervisor Policy.

This policy models the ideal supervisor:
- gathers all worker outputs,
- audits operations and policy,
- cross-checks research vs operations,
- cross-checks research vs communication,
- selects safe technical fix,
- requests stakeholder message revision,
- escalates when policy risk is detected,
- approves only after risks are resolved.

Expected result:
- highest reward,
- high success rate,
- low unsafe approval rate.
"""

from typing import Dict, Any


class CautiousSupervisorPolicy:
    name = "cautious_supervisor"

    def __init__(self):
        self.phase = 0

    def reset(self):
        self.phase = 0

    def act(self, state: Dict[str, Any]) -> str:
        fixed_plan = [
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
        ]

        if self.phase < len(fixed_plan):
            action = fixed_plan[self.phase]
            self.phase += 1
            return action

        self.phase += 1

        risk_flags = set(state.get("risk_flags", []))
        completed_actions = set(state.get("completed_actions", []))

        if (
            "policy_risk_detected" in risk_flags
            and "reject_or_escalate" not in completed_actions
        ):
            return "reject_or_escalate"

        return "approve"

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
    policy = CautiousSupervisorPolicy()
    result = policy.run_episode(env, scenario_index=0)

    print("Policy:", result["policy"])
    print("Case:", result["case_id"])
    print("Success:", result["success"])
    print("Unsafe approval:", result["unsafe_approval"])
    print("Total reward:", result["total_reward"])

    for step in result["trace"]:
        print(step["action"], step["reward"], step["info"].get("message"))
