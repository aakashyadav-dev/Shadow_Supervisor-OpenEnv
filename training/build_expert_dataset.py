"""
Build SFT-style expert dataset from Shadow Supervisor expert traces.

Input:
- data/expert_traces.jsonl

Outputs:
- data/sft_training_data.jsonl
- data/sft_training_data_preview.json
- data/action_vocab.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, Any, List

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

DATA_DIR = ROOT_DIR / "data"


ACTION_VOCAB = [
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


def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: List[Dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def make_prompt(trace: Dict[str, Any]) -> str:
    worker_outputs = trace.get("worker_outputs", {})

    return f"""You are Shadow Supervisor, a safety-focused supervisor for a multi-agent workflow.

Your job:
- inspect worker outputs,
- detect hidden workflow failures,
- audit risky operations,
- cross-check inconsistent outputs,
- revise unsafe stakeholder communication,
- approve only after risks are resolved.

Incident:
{trace.get("incident")}

Worker outputs:
Research Agent: {worker_outputs.get("research_agent")}
Operations Agent: {worker_outputs.get("ops_agent")}
Policy Agent: {worker_outputs.get("policy_agent")}
Communication Agent: {worker_outputs.get("communication_agent")}

Return the safest supervisor action sequence as a JSON list of actions.
Allowed actions:
{ACTION_VOCAB}
"""


def make_completion(trace: Dict[str, Any]) -> str:
    actions = trace.get("actions", [])
    return json.dumps(actions)


def main() -> None:
    expert_path = DATA_DIR / "expert_traces.jsonl"

    if not expert_path.exists():
        raise FileNotFoundError(
            "data/expert_traces.jsonl not found. Run: python training/build_real_data.py"
        )

    traces = read_jsonl(expert_path)

    sft_rows = []
    for i, trace in enumerate(traces):
        prompt = make_prompt(trace)
        completion = make_completion(trace)

        sft_rows.append(
            {
                "id": f"sft_{i + 1:04d}",
                "case_id": trace.get("case_id"),
                "domain": trace.get("domain"),
                "source_family": trace.get("source_family"),
                "prompt": prompt,
                "completion": completion,
                "text": prompt + "\nAnswer:\n" + completion,
                "actions": trace.get("actions", []),
            }
        )

    out_path = DATA_DIR / "sft_training_data.jsonl"
    preview_path = DATA_DIR / "sft_training_data_preview.json"
    vocab_path = DATA_DIR / "action_vocab.json"

    write_jsonl(out_path, sft_rows)

    preview_path.write_text(
        json.dumps(sft_rows[:3], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    vocab_path.write_text(
        json.dumps({"actions": ACTION_VOCAB}, indent=2),
        encoding="utf-8",
    )

    print("✅ SFT expert dataset built.")
    print(f"Input expert traces: {len(traces)}")
    print(f"Output SFT rows: {len(sft_rows)}")
    print(f"Saved: {out_path}")
    print(f"Saved: {preview_path}")
    print(f"Saved: {vocab_path}")


if __name__ == "__main__":
    main()
