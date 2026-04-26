from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from env.shadow_supervisor_env import ShadowSupervisorEnv
from env.scenarios import load_eval_scenarios
from agents.random_policy import RandomSupervisorPolicy
from agents.naive_policy import NaiveSupervisorPolicy
from agents.training_candidate_policy import TrainingCandidatePolicy
from agents.spam_all_actions_policy import SpamAllActionsPolicy
from agents.rl_policy import RLEnvTrainedPolicy
from agents.cautious_policy import CautiousSupervisorPolicy
from evaluation.metrics import summarize_episode_results

DATA_DIR = ROOT_DIR / "data"
OUTPUTS_DIR = ROOT_DIR / "outputs"


def run_policy(policy, scenario_path: str, scenarios: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    results = []

    for i in range(len(scenarios)):
        env = ShadowSupervisorEnv(scenario_path=scenario_path, seed=700 + i)
        result = policy.run_episode(env, scenario_index=i, seed=700 + i)
        result["scenario_index"] = i
        result["domain"] = scenarios[i].get("domain")
        result["hidden_failures"] = scenarios[i].get("hidden_failures", [])
        results.append(result)

    return results


def main() -> None:
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    scenario_path = str(DATA_DIR / "scenarios_eval.json")
    scenarios = load_eval_scenarios()

    policies = [
        RandomSupervisorPolicy(),
        NaiveSupervisorPolicy(),
        TrainingCandidatePolicy(),
        SpamAllActionsPolicy(),
        RLEnvTrainedPolicy(),
        CautiousSupervisorPolicy(),
    ]

    comparison = {}
    all_results = {}

    for policy in policies:
        results = run_policy(policy, scenario_path, scenarios)
        comparison[policy.name] = summarize_episode_results(results)
        all_results[policy.name] = results

    out_json = {
        "description": "Hardened evaluation with random, naive, candidate, spam-all-actions, RL-trained, and cautious policies.",
        "eval_scenarios": len(scenarios),
        "policies": comparison,
    }

    json_path = DATA_DIR / "policy_comparison_hardened.json"
    csv_path = OUTPUTS_DIR / "policy_comparison_hardened.csv"
    trace_path = OUTPUTS_DIR / "rl_sample_episode_trace.json"

    json_path.write_text(json.dumps(out_json, indent=2), encoding="utf-8")

    rows = []
    for policy_name, metrics in comparison.items():
        row = {"policy": policy_name}
        row.update(metrics)
        rows.append(row)

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    rl_results = all_results.get("rl_trained_supervisor", [])

    if rl_results:
        trace_path.write_text(json.dumps(rl_results[0], indent=2), encoding="utf-8")

    print("✅ Hardened evaluation complete.")
    print(f"Saved: {json_path}")
    print(f"Saved: {csv_path}")
    print(f"Saved: {trace_path}")
    print(json.dumps(out_json, indent=2))


if __name__ == "__main__":
    main()