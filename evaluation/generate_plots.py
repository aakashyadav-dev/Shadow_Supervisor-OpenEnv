"""
Generate Shadow Supervisor plots.

Inputs:
- outputs/policy_comparison.csv
- outputs/training_metrics.json
- data/reward_logs.jsonl

Outputs:
- outputs/reward_curve.png
- outputs/success_rate.png
- outputs/unsafe_approval_rate.png
- outputs/risk_detection_rate.png
- outputs/policy_comparison_with_trained.csv
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Dict, Any, List

import matplotlib.pyplot as plt

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

DATA_DIR = ROOT_DIR / "data"
OUTPUTS_DIR = ROOT_DIR / "outputs"


def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows = []

    if not path.exists():
        return rows

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))

    return rows


def read_csv(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []

    with path.open("r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    if not rows:
        return

    fieldnames = list(rows[0].keys())

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def load_policy_rows() -> List[Dict[str, Any]]:
    """
    Prefer training_metrics.json because it includes trained_imitation_supervisor.
    Fallback to outputs/policy_comparison.csv from Phase 6.
    """

    training_metrics_path = OUTPUTS_DIR / "training_metrics.json"

    if training_metrics_path.exists():
        metrics = json.loads(training_metrics_path.read_text(encoding="utf-8"))
        summaries = metrics.get("policy_summaries", {})

        rows = []
        for policy_name, summary in summaries.items():
            row = {"policy": policy_name}
            row.update(summary)
            rows.append(row)

        return rows

    return read_csv(OUTPUTS_DIR / "policy_comparison.csv")


def to_float(value: Any) -> float:
    try:
        return float(value)
    except Exception:
        return 0.0


def pretty_policy_name(name: str) -> str:
    mapping = {
        "naive_supervisor": "Naive",
        "training_candidate_supervisor": "Candidate",
        "cautious_supervisor": "Cautious",
        "trained_imitation_supervisor": "Trained",
    }
    return mapping.get(name, name.replace("_", " ").title())


def add_bar_labels(values: List[float]) -> None:
    for index, value in enumerate(values):
        plt.text(
            index,
            value,
            f"{value:.2f}",
            ha="center",
            va="bottom",
            fontsize=9,
        )


def plot_reward_curve(reward_logs: List[Dict[str, Any]]) -> None:
    if not reward_logs:
        print("No reward logs found. Skipping reward_curve.png")
        return

    epochs = [int(row["epoch"]) for row in reward_logs]
    rewards = [to_float(row["train_reward"]) for row in reward_logs]

    plt.figure(figsize=(9, 5))
    plt.plot(epochs, rewards, marker="o")
    plt.title("Shadow Supervisor Reward Improvement")
    plt.xlabel("Training Epoch / Imitation Step")
    plt.ylabel("Average Reward")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(OUTPUTS_DIR / "reward_curve.png", dpi=200)
    plt.close()


def plot_success_rate(policy_rows: List[Dict[str, Any]]) -> None:
    labels = [pretty_policy_name(row["policy"]) for row in policy_rows]
    values = [to_float(row.get("success_rate", 0)) for row in policy_rows]

    plt.figure(figsize=(9, 5))
    plt.bar(labels, values)
    plt.title("Success Rate by Supervisor Policy")
    plt.xlabel("Policy")
    plt.ylabel("Success Rate")
    plt.ylim(0, 1.1)
    add_bar_labels(values)
    plt.tight_layout()
    plt.savefig(OUTPUTS_DIR / "success_rate.png", dpi=200)
    plt.close()


def plot_unsafe_approval_rate(policy_rows: List[Dict[str, Any]]) -> None:
    labels = [pretty_policy_name(row["policy"]) for row in policy_rows]
    values = [to_float(row.get("unsafe_approval_rate", 0)) for row in policy_rows]

    plt.figure(figsize=(9, 5))
    plt.bar(labels, values)
    plt.title("Unsafe Approval Rate by Supervisor Policy")
    plt.xlabel("Policy")
    plt.ylabel("Unsafe Approval Rate")
    plt.ylim(0, 1.1)
    add_bar_labels(values)
    plt.tight_layout()
    plt.savefig(OUTPUTS_DIR / "unsafe_approval_rate.png", dpi=200)
    plt.close()


def plot_risk_detection_rate(policy_rows: List[Dict[str, Any]]) -> None:
    labels = [pretty_policy_name(row["policy"]) for row in policy_rows]

    # Normalize avg risk detection count to a 0-1 style rate for easy plotting.
    # The environment often exposes around 4 meaningful risk signals.
    values = [
        min(1.0, to_float(row.get("avg_risk_detection_count", 0)) / 4.0)
        for row in policy_rows
    ]

    plt.figure(figsize=(9, 5))
    plt.bar(labels, values)
    plt.title("Risk Detection Rate by Supervisor Policy")
    plt.xlabel("Policy")
    plt.ylabel("Approx. Risk Detection Rate")
    plt.ylim(0, 1.1)
    add_bar_labels(values)
    plt.tight_layout()
    plt.savefig(OUTPUTS_DIR / "risk_detection_rate.png", dpi=200)
    plt.close()


def main() -> None:
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    policy_rows = load_policy_rows()
    reward_logs = read_jsonl(DATA_DIR / "reward_logs.jsonl")

    if not policy_rows:
        print("No policy rows found.")
        print("Run first:")
        print("  python evaluation/run_eval.py")
        print("  python training/train_trl.py")
        raise SystemExit(1)

    comparison_path = OUTPUTS_DIR / "policy_comparison_with_trained.csv"
    write_csv(comparison_path, policy_rows)

    plot_reward_curve(reward_logs)
    plot_success_rate(policy_rows)
    plot_unsafe_approval_rate(policy_rows)
    plot_risk_detection_rate(policy_rows)

    print("✅ Plots generated successfully.")
    print(f"Saved: {OUTPUTS_DIR / 'reward_curve.png'}")
    print(f"Saved: {OUTPUTS_DIR / 'success_rate.png'}")
    print(f"Saved: {OUTPUTS_DIR / 'unsafe_approval_rate.png'}")
    print(f"Saved: {OUTPUTS_DIR / 'risk_detection_rate.png'}")
    print(f"Saved: {comparison_path}")

    print()
    print("Policy rows used:")
    for row in policy_rows:
        print(
            f"- {row['policy']}: "
            f"reward={row.get('avg_reward')}, "
            f"success={row.get('success_rate')}, "
            f"unsafe={row.get('unsafe_approval_rate')}, "
            f"risk_detect={row.get('avg_risk_detection_count')}"
        )


if __name__ == "__main__":
    main()
