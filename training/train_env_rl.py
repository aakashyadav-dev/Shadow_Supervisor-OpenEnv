from __future__ import annotations

import csv
import json
import random
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from env.actions import ACTIONS
from env.shadow_supervisor_env import ShadowSupervisorEnv
from env.scenarios import load_train_scenarios, load_eval_scenarios
from agents.random_policy import RandomSupervisorPolicy
from agents.naive_policy import NaiveSupervisorPolicy
from agents.training_candidate_policy import TrainingCandidatePolicy
from agents.cautious_policy import CautiousSupervisorPolicy
from agents.rl_policy import RLEnvTrainedPolicy
from evaluation.metrics import summarize_episode_results

DATA_DIR = ROOT_DIR / "data"
OUTPUTS_DIR = ROOT_DIR / "outputs"


def softmax(logits: np.ndarray) -> np.ndarray:
    logits = logits - np.max(logits)
    exp = np.exp(logits)
    return exp / np.sum(exp)


def init_logits(max_steps: int) -> np.ndarray:
    logits = np.zeros((max_steps, len(ACTIONS)), dtype=np.float32)

    prior = [
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

    for i, action in enumerate(prior[:max_steps]):
        logits[i, ACTIONS.index(action)] += 0.8

    return logits


def sample_sequence(logits: np.ndarray, rng: random.Random) -> List[str]:
    sequence = []

    for step_logits in logits:
        probs = softmax(step_logits)
        action_idx = rng.choices(range(len(ACTIONS)), weights=probs.tolist(), k=1)[0]
        sequence.append(ACTIONS[action_idx])

    if "approve" not in sequence:
        sequence[-1] = "approve"

    return sequence


def evaluate_sequence(
    sequence: List[str],
    scenario_path: str,
    scenario_indices: List[int],
    seed: int,
) -> Tuple[float, float, float]:
    rewards = []
    successes = []
    unsafe = []

    for idx in scenario_indices:
        env = ShadowSupervisorEnv(scenario_path=scenario_path, seed=seed + idx)
        env.reset(seed=seed + idx, scenario_index=idx)

        done = False

        for action in sequence:
            _, _, done, _ = env.step(action)
            if done:
                break

        if not done:
            env.step("approve")

        state = env.state()
        rewards.append(float(state["total_reward"]))
        successes.append(1.0 if state["success"] else 0.0)
        unsafe.append(1.0 if state["unsafe_approval"] else 0.0)

    return float(np.mean(rewards)), float(np.mean(successes)), float(np.mean(unsafe))


def train_rl(
    epochs: int = 60,
    population: int = 70,
    elite_frac: float = 0.2,
    max_steps: int = 12,
    seed: int = 42,
) -> Dict[str, Any]:
    rng = random.Random(seed)
    np.random.seed(seed)

    train_scenarios = load_train_scenarios()
    scenario_path = str(DATA_DIR / "scenarios_train.json")

    logits = init_logits(max_steps)
    elite_count = max(4, int(population * elite_frac))
    logs = []

    for epoch in range(1, epochs + 1):
        scenario_indices = rng.sample(
            range(len(train_scenarios)),
            k=min(8, len(train_scenarios)),
        )

        rollouts = []

        for _ in range(population):
            sequence = sample_sequence(logits, rng)
            avg_reward, success_rate, unsafe_rate = evaluate_sequence(
                sequence,
                scenario_path,
                scenario_indices,
                seed + epoch,
            )

            rollouts.append(
                {
                    "sequence": sequence,
                    "avg_reward": avg_reward,
                    "success_rate": success_rate,
                    "unsafe_rate": unsafe_rate,
                }
            )

        rollouts.sort(key=lambda x: x["avg_reward"], reverse=True)
        elites = rollouts[:elite_count]

        new_logits = np.zeros_like(logits)

        for step in range(max_steps):
            counts = np.ones(len(ACTIONS), dtype=np.float32) * 0.05

            for elite in elites:
                action = elite["sequence"][step]
                counts[ACTIONS.index(action)] += 1.0

            probs = counts / counts.sum()
            new_logits[step] = np.log(probs + 1e-8)

        logits = 0.65 * logits + 0.35 * new_logits

        mean_reward = float(np.mean([r["avg_reward"] for r in rollouts]))
        elite_reward = float(np.mean([r["avg_reward"] for r in elites]))
        best = rollouts[0]

        logs.append(
            {
                "epoch": epoch,
                "mean_reward": round(mean_reward, 3),
                "elite_reward": round(elite_reward, 3),
                "best_reward": round(best["avg_reward"], 3),
                "policy_loss": round(-elite_reward, 3),
                "best_success_rate": round(best["success_rate"], 3),
                "best_unsafe_approval_rate": round(best["unsafe_rate"], 3),
                "best_sequence": best["sequence"],
            }
        )

        if epoch == 1 or epoch % 10 == 0:
            print(
                f"epoch={epoch:03d} "
                f"mean={mean_reward:.2f} "
                f"elite={elite_reward:.2f} "
                f"best={best['avg_reward']:.2f} "
                f"success={best['success_rate']:.2f} "
                f"unsafe={best['unsafe_rate']:.2f}"
            )

    greedy = [ACTIONS[int(np.argmax(step_logits))] for step_logits in logits]

    if "approve" not in greedy:
        greedy[-1] = "approve"

    return {
        "method": "environment_connected_cross_entropy_rl",
        "epochs": epochs,
        "population": population,
        "elite_frac": elite_frac,
        "max_steps": max_steps,
        "action_sequence": greedy,
        "logs": logs,
    }


def evaluate_policy(policy, scenario_path: str, scenario_count: int) -> Dict[str, Any]:
    results = []

    for i in range(scenario_count):
        env = ShadowSupervisorEnv(scenario_path=scenario_path, seed=500 + i)
        result = policy.run_episode(env, scenario_index=i, seed=500 + i)
        results.append(result)

    return summarize_episode_results(results)


def save_plots(logs: List[Dict[str, Any]]) -> None:
    epochs = [row["epoch"] for row in logs]
    mean_reward = [row["mean_reward"] for row in logs]
    elite_reward = [row["elite_reward"] for row in logs]
    loss = [row["policy_loss"] for row in logs]
    success = [row["best_success_rate"] for row in logs]
    unsafe = [row["best_unsafe_approval_rate"] for row in logs]

    plt.figure(figsize=(9, 5))
    plt.plot(epochs, mean_reward, marker="o", label="Mean rollout reward")
    plt.plot(epochs, elite_reward, marker="o", label="Elite reward")
    plt.title("Environment-Connected RL Reward Curve")
    plt.xlabel("Training epoch")
    plt.ylabel("Average reward")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUTPUTS_DIR / "rl_reward_curve.png", dpi=200)
    plt.close()

    plt.figure(figsize=(9, 5))
    plt.plot(epochs, loss, marker="o")
    plt.title("RL Training Loss Curve")
    plt.xlabel("Training epoch")
    plt.ylabel("Policy loss = -elite reward")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(OUTPUTS_DIR / "training_loss.png", dpi=200)
    plt.close()

    plt.figure(figsize=(9, 5))
    plt.plot(epochs, success, marker="o", label="Best success rate")
    plt.plot(epochs, unsafe, marker="o", label="Best unsafe approval rate")
    plt.title("Safety Improvement During RL Training")
    plt.xlabel("Training epoch")
    plt.ylabel("Rate")
    plt.ylim(-0.05, 1.05)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUTPUTS_DIR / "rl_safety_curve.png", dpi=200)
    plt.close()


def main() -> None:
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    result = train_rl()
    policy_path = OUTPUTS_DIR / "rl_policy.json"
    logs_path = OUTPUTS_DIR / "rl_training_logs.jsonl"
    metrics_path = OUTPUTS_DIR / "rl_training_metrics.json"
    csv_path = OUTPUTS_DIR / "policy_comparison_rl.csv"

    policy_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    with logs_path.open("w", encoding="utf-8") as f:
        for row in result["logs"]:
            f.write(json.dumps(row) + "\n")

    save_plots(result["logs"])

    eval_scenarios = load_eval_scenarios()
    eval_path = str(DATA_DIR / "scenarios_eval.json")

    policies = [
        RandomSupervisorPolicy(),
        NaiveSupervisorPolicy(),
        TrainingCandidatePolicy(),
        RLEnvTrainedPolicy(),
        CautiousSupervisorPolicy(),
    ]

    summaries = {}

    for policy in policies:
        summaries[policy.name] = evaluate_policy(policy, eval_path, len(eval_scenarios))

    metrics = {
        "training_method": result["method"],
        "trained_policy_path": str(policy_path),
        "rl_logs_path": str(logs_path),
        "action_sequence": result["action_sequence"],
        "policy_summaries": summaries,
    }

    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    rows = []

    for policy_name, summary in summaries.items():
        row = {"policy": policy_name}
        row.update(summary)
        rows.append(row)

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print("\n✅ Environment-connected RL training complete.")
    print(f"Saved: {policy_path}")
    print(f"Saved: {logs_path}")
    print(f"Saved: {metrics_path}")
    print(f"Saved: {csv_path}")
    print(f"Saved: {OUTPUTS_DIR / 'rl_reward_curve.png'}")
    print(f"Saved: {OUTPUTS_DIR / 'training_loss.png'}")
    print(f"Saved: {OUTPUTS_DIR / 'rl_safety_curve.png'}")
    print("\nLearned sequence:")
    print(" -> ".join(result["action_sequence"]))
    print("\nPolicy summaries:")
    print(json.dumps(summaries, indent=2))


if __name__ == "__main__":
    main()