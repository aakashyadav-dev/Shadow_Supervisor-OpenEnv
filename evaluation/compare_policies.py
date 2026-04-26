"""
Human-readable policy comparison for Shadow Supervisor.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def main() -> None:
    path = ROOT_DIR / "data" / "policy_comparison.json"

    if not path.exists():
        print("policy_comparison.json not found.")
        print("Run this first:")
        print("  python evaluation/run_eval.py")
        return

    data = json.loads(path.read_text(encoding="utf-8"))
    policies = data.get("policies", {})

    print("\nShadow Supervisor Policy Comparison")
    print("=" * 70)

    header = (
        f"{'Policy':32s} "
        f"{'Avg Reward':>10s} "
        f"{'Success':>10s} "
        f"{'Unsafe':>10s} "
        f"{'Risk Detect':>12s}"
    )
    print(header)
    print("-" * 70)

    for policy_name, metrics in policies.items():
        print(
            f"{policy_name:32s} "
            f"{metrics.get('avg_reward', 0):10.2f} "
            f"{metrics.get('success_rate', 0):10.2f} "
            f"{metrics.get('unsafe_approval_rate', 0):10.2f} "
            f"{metrics.get('avg_risk_detection_count', 0):12.2f}"
        )

    print("=" * 70)
    print("\nInterpretation:")
    print("- Naive supervisor should have low reward and high unsafe approval.")
    print("- Training candidate should improve reward but may still miss message risk.")
    print("- Cautious supervisor should have the best success and lowest unsafe approval.")


if __name__ == "__main__":
    main()
