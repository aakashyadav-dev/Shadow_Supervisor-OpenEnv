from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from env.shadow_supervisor_env import ShadowSupervisorEnv

app = FastAPI(
    title="Shadow Supervisor OpenEnv Server",
    description="OpenEnv-style API for multi-agent oversight training.",
    version="0.1.0",
)

ENV = ShadowSupervisorEnv(
    scenario_path=str(ROOT_DIR / "data" / "scenarios_eval.json")
)


class ResetRequest(BaseModel):
    seed: Optional[int] = 42
    scenario_index: Optional[int] = 0


class StepRequest(BaseModel):
    action: str


@app.get("/")
def root():
    return {
        "name": "Shadow Supervisor",
        "description": "OpenEnv-style multi-agent oversight environment.",
        "endpoints": ["/health", "/reset", "/step", "/state", "/docs"],
    }


@app.get("/health")
def health():
    return {"status": "healthy", "env": "shadow-supervisor"}


@app.post("/reset")
def reset(req: ResetRequest):
    return ENV.reset(seed=req.seed, scenario_index=req.scenario_index)


@app.post("/step")
def step(req: StepRequest):
    observation, reward, done, info = ENV.step(req.action)
    return {
        "observation": observation,
        "reward": reward,
        "done": done,
        "info": info,
    }


@app.get("/state")
def state():
    return ENV.state()