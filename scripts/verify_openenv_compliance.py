from __future__ import annotations

import importlib.metadata
import sys
from pathlib import Path

import yaml

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from env.openenv_adapter import (
    ShadowSupervisorAction,
    ShadowSupervisorObservation,
    ShadowSupervisorOpenEnv,
    ShadowSupervisorState,
)


def main() -> None:
    version = importlib.metadata.version("openenv-core")
    print(f"openenv-core version: {version}")

    manifest_path = ROOT_DIR / "openenv.yaml"
    assert manifest_path.exists(), "openenv.yaml is missing"

    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    assert manifest["framework"]["package"] == "openenv-core"
    assert manifest["environment"]["class"] == "ShadowSupervisorOpenEnv"

    env = ShadowSupervisorOpenEnv()
    assert hasattr(env, "reset")
    assert hasattr(env, "step")
    assert hasattr(env, "state")

    obs = env.reset(seed=42, scenario_index=0)
    assert isinstance(obs, ShadowSupervisorObservation)
    assert isinstance(obs.observation, dict)

    step_obs = env.step(ShadowSupervisorAction(action="assign_research"))
    assert isinstance(step_obs, ShadowSupervisorObservation)
    assert isinstance(step_obs.reward, float)
    assert isinstance(step_obs.done, bool)
    assert isinstance(step_obs.info, dict)

    st = env.state()
    assert isinstance(st, ShadowSupervisorState)
    assert isinstance(st.state, dict)

    print("✅ OpenEnv compliance check passed.")
    print("✅ openenv-core is installed and imported.")
    print("✅ ShadowSupervisorOpenEnv wrapper works.")
    print("✅ reset(), step(), and state() work.")
    print("✅ openenv.yaml points to the OpenEnv adapter.")


if __name__ == "__main__":
    main()