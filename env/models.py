"""
Pydantic models for Shadow Supervisor scenarios and state.
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class WorkerOutputs(BaseModel):
    research_agent: Optional[str] = None
    ops_agent: Optional[str] = None
    policy_agent: Optional[str] = None
    communication_agent: Optional[str] = None


class Scenario(BaseModel):
    case_id: str
    source_type: str
    domain: str
    incident: str
    source_notes: Optional[Dict[str, Any]] = Field(default_factory=dict)
    worker_outputs: WorkerOutputs
    safe_outputs: Optional[Dict[str, str]] = Field(default_factory=dict)
    hidden_failures: List[str]
    correct_actions: List[str]
    unsafe_actions: List[str]
    reward_rules: Dict[str, int]


class EnvState(BaseModel):
    case_id: str
    domain: str
    incident: str
    visible_worker_outputs: Dict[str, Optional[str]]
    completed_actions: List[str]
    risk_flags: List[str]
    resolved_risks: List[str]
    available_actions: List[str]
    step_count: int
    max_steps: int
    total_reward: float
    done: bool
    success: bool
    unsafe_approval: bool
