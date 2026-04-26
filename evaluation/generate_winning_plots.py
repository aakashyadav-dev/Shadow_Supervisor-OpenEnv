from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

import matplotlib.pyplot as plt

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

OUTPUTS_DIR = ROOT_DIR / "outputs"


def read_csv(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []

    with path.open("r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []

    rows = []

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))

    return rows


def to_float(value: Any) -> float:
    try:
        return float(value)
    except Exception:
        return 0.0


def short_name(name: str) -> str:
    return {
        "random_supervisor": "Random",
        "naive_supervisor": "Naive",
        "training_candidate_supervisor": "Candidate",
        "spam_all_actions_supervisor": "Spam-All",
        "rl_trained_supervisor": "RL-Trained",
        "cautious_supervisor": "Expert",
    }.get(name, name)


def add_labels(values):
    for i, value in enumerate(values):
        plt.text(i, value, f"{value:.2f}", ha="center", va="bottom", fontsize=8)


def plot_baseline_vs_trained(rows):
    labels = [short_name(r["policy"]) for r in rows]
    rewards = [to_float(r.get("avg_reward")) for r in rows]

    plt.figure(figsize=(10, 5))
    plt.bar(labels, rewards)
    plt.title("Baseline vs RL-Trained vs Expert Reward")
    plt.xlabel("Policy")
    plt.ylabel("Average reward on held-out scenarios")
    add_labels(rewards)
    plt.tight_layout()
    plt.savefig(OUTPUTS_DIR / "baseline_vs_trained.png", dpi=200)
    plt.close()


def plot_success(rows):
    labels = [short_name(r["policy"]) for r in rows]
    values = [to_float(r.get("success_rate")) for r in rows]

    plt.figure(figsize=(10, 5))
    plt.bar(labels, values)
    plt.title("Success Rate by Supervisor")
    plt.xlabel("Policy")
    plt.ylabel("Success rate")
    plt.ylim(0, 1.1)
    add_labels(values)
    plt.tight_layout()
    plt.savefig(OUTPUTS_DIR / "winning_success_rate.png", dpi=200)
    plt.close()


def plot_unsafe(rows):
    labels = [short_name(r["policy"]) for r in rows]
    values = [to_float(r.get("unsafe_approval_rate")) for r in rows]

    plt.figure(figsize=(10, 5))
    plt.bar(labels, values)
    plt.title("Unsafe Approval Rate by Supervisor")
    plt.xlabel("Policy")
    plt.ylabel("Unsafe approval rate")
    plt.ylim(0, 1.1)
    add_labels(values)
    plt.tight_layout()
    plt.savefig(OUTPUTS_DIR / "winning_unsafe_approval_rate.png", dpi=200)
    plt.close()


def plot_rl_training(logs):
    if not logs:
        return

    epochs = [int(r["epoch"]) for r in logs]
    reward = [to_float(r["elite_reward"]) for r in logs]
    loss = [to_float(r["policy_loss"]) for r in logs]

    plt.figure(figsize=(9, 5))
    plt.plot(epochs, reward, marker="o")
    plt.title("RL Training Reward Curve")
    plt.xlabel("Training epoch")
    plt.ylabel("Elite rollout reward")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(OUTPUTS_DIR / "winning_rl_reward_curve.png", dpi=200)
    plt.close()

    plt.figure(figsize=(9, 5))
    plt.plot(epochs, loss, marker="o")
    plt.title("RL Training Loss Curve")
    plt.xlabel("Training epoch")
    plt.ylabel("Policy loss")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(OUTPUTS_DIR / "winning_training_loss.png", dpi=200)
    plt.close()


def main() -> None:
    rows = read_csv(OUTPUTS_DIR / "policy_comparison_hardened.csv")

    if not rows:
        print("Run first: python evaluation/run_eval_hardened.py")
        raise SystemExit(1)

    logs = read_jsonl(OUTPUTS_DIR / "rl_training_logs.jsonl")

    plot_baseline_vs_trained(rows)
    plot_success(rows)
    plot_unsafe(rows)
    plot_rl_training(logs)

    print("✅ Winning plots generated.")
    print("Saved: outputs/baseline_vs_trained.png")
    print("Saved: outputs/winning_success_rate.png")
    print("Saved: outputs/winning_unsafe_approval_rate.png")
    print("Saved: outputs/winning_rl_reward_curve.png")
    print("Saved: outputs/winning_training_loss.png")


if __name__ == "__main__":
    main()