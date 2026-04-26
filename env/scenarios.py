"""
Scenario loading and validation utilities.
"""

import json
from pathlib import Path
from typing import List, Dict, Any

from env.models import Scenario


def load_scenarios(path: str) -> List[Dict[str, Any]]:
    scenario_path = Path(path)

    if not scenario_path.exists():
        raise FileNotFoundError(f"Scenario file not found: {path}")

    with scenario_path.open("r", encoding="utf-8") as f:
        raw_scenarios = json.load(f)

    if not isinstance(raw_scenarios, list):
        raise ValueError(f"Scenario file must contain a list: {path}")

    validated = []
    for item in raw_scenarios:
        scenario = Scenario(**item)
        validated.append(scenario.dict())

    return validated


def load_train_scenarios() -> List[Dict[str, Any]]:
    return load_scenarios("data/scenarios_train.json")


def load_eval_scenarios() -> List[Dict[str, Any]]:
    return load_scenarios("data/scenarios_eval.json")
