"""
Run evaluation for Shadow Supervisor policies.

Outputs:
- outputs/policy_comparison.csv
- outputs/sample_episode_trace.json
- data/policy_comparison.json
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Dict, Any, List

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from env.shadow_supervisor_env import ShadowSupervisorEnv
from env.scenarios import load_eval_scenarios
from agents.naive_policy import NaiveSupervisorPolicy
from agents.training_candidate_policy import TrainingCandidatePolicy
from agents.cautious_policy import CautiousSupervisorPolicy
from evaluation.metrics import summarize_episode_results, flatten_policy_summary


DATA_DIR = ROOT_DIR / "data"
OUTPUTS_DIR = ROOT_DIR / "outputs"


def run_policy_on_eval(policy, scenario_path: str) -> List[Dict[str, Any]]:
    scenarios = load_eval_scenarios()
    results = []

    for scenario_index in range(len(scenarios)):
        env = ShadowSupervisorEnv(
            scenario_path=scenario_path,
            seed=42 + scenario_index,
        )

        result = policy.run_episode(
            env,
            scenario_index=scenario_index,
            seed=42 + scenario_index,
        )

        result["scenario_index"] = scenario_index
        result["domain"] = scenarios[scenario_index].get("domain")
        result["incident"] = scenarios[scenario_index].get("incident")
        result["hidden_failures"] = scenarios[scenario_index].get("hidden_failures", [])

        results.append(result)

    return results


def write_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    if not rows:
        return

    fieldnames = list(rows[0].keys())

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    scenario_path = str(DATA_DIR / "scenarios_eval.json")

    policies = [
        NaiveSupervisorPolicy(),
        TrainingCandidatePolicy(),
        CautiousSupervisorPolicy(),
    ]

    all_policy_results = {}
    policy_rows = []

    for policy in policies:
        results = run_policy_on_eval(policy, scenario_path)
        summary = summarize_episode_results(results)

        all_policy_results[policy.name] = {
            "summary": summary,
            "episodes": results,
        }

        policy_rows.append(flatten_policy_summary(policy.name, summary))

    policy_comparison = {
        "description": (
            "Evaluation of naive, training-candidate, and cautious supervisor "
            "policies on held-out Shadow Supervisor scenarios."
        ),
        "eval_scenarios": len(load_eval_scenarios()),
        "policies": {
            name: value["summary"] for name, value in all_policy_results.items()
        },
    }

    csv_path = OUTPUTS_DIR / "policy_comparison.csv"
    json_path = DATA_DIR / "policy_comparison.json"
    trace_path = OUTPUTS_DIR / "sample_episode_trace.json"

    write_csv(csv_path, policy_rows)
    json_path.write_text(json.dumps(policy_comparison, indent=2), encoding="utf-8")

    # Save one strong demo trace from the cautious policy on scenario 0.
    sample_trace = all_policy_results["cautious_supervisor"]["episodes"][0]
    trace_path.write_text(json.dumps(sample_trace, indent=2), encoding="utf-8")

    print("✅ Evaluation complete.")
    print(f"Saved CSV: {csv_path}")
    print(f"Saved JSON: {json_path}")
    print(f"Saved sample trace: {trace_path}")
    print()
    print("Policy comparison:")
    print(json.dumps(policy_comparison, indent=2))


if __name__ == "__main__":
    main()
