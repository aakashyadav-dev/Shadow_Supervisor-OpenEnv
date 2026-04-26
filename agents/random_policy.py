from __future__ import annotations

import random
import sys
from pathlib import Path
from typing import Any, Dict

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from env.actions import ACTIONS


class RandomSupervisorPolicy:
    name = "random_supervisor"

    def __init__(self, seed: int = 42):
        self.random = random.Random(seed)
        self.steps = 0

    def reset(self):
        self.steps = 0

    def act(self, state: Dict[str, Any]) -> str:
        self.steps += 1
        completed = set(state.get("completed_actions", []))
        candidates = [a for a in ACTIONS if a not in completed]

        if self.steps >= 5 and self.random.random() < 0.4:
            return "approve"

        if not candidates:
            return "approve"

        return self.random.choice(candidates)

    def run_episode(self, env, scenario_index=None, seed=None):
        self.reset()

        if seed is not None:
            self.random.seed(seed)

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
    policy = RandomSupervisorPolicy()
    result = policy.run_episode(env, scenario_index=0, seed=42)

    print("Policy:", result["policy"])
    print("Success:", result["success"])
    print("Unsafe approval:", result["unsafe_approval"])
    print("Reward:", result["total_reward"])